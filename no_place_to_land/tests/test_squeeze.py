import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from pypdf import PdfReader, PdfWriter

from squeeze import image_resolutions, pixel_key, resized_dimensions, stage_images
from verify_pdfs import verify


class ResolutionTests(unittest.TestCase):
    def test_preserves_aspect_ratio_and_never_upscales(self):
        self.assertEqual(resized_dimensions((1600, 800), (400, 400), 200), (802, 401))
        self.assertEqual(resized_dimensions((800, 1200), (100, 110), 200), (800, 1200))

    def test_small_and_non_square_placements(self):
        self.assertEqual(resized_dimensions((1, 1), (600, 600), 200), (1, 1))
        self.assertEqual(resized_dimensions((1000, 1000), (200, 400), 200), (1000, 1000))

    def test_invalid_resolutions(self):
        for dpi in (0, -1):
            with self.assertRaises(ValueError):
                resized_dimensions((100, 100), (300, 300), dpi)

    def test_pixel_match_includes_alpha_and_dimensions(self):
        rgb = Image.new("RGB", (20, 10), "red")
        self.assertEqual(pixel_key(rgb), pixel_key(rgb.convert("RGBA")))
        transparent = rgb.convert("RGBA")
        transparent.putalpha(100)
        self.assertNotEqual(pixel_key(rgb), pixel_key(transparent))
        self.assertNotEqual(pixel_key(rgb), pixel_key(Image.new("RGB", (10, 20), "red")))

    @patch("squeeze.subprocess.run")
    def test_uses_largest_repeated_placement_and_ignores_masks(self, run):
        run.return_value.stdout = """header
separator
1 0 image 1600 800 rgb 3 8 image no 5 0 600 600 1K 1%
1 1 smask 1600 800 gray 1 8 image no 5 0 600 600 1K 1%
2 2 image 1600 800 rgb 3 8 image no 5 0 300 400 1K 1%
"""
        self.assertEqual(image_resolutions("fixture.pdf"), {(5, 0): (300, 400)})


class PdfIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Path("build").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir="build", prefix="squeeze-test-")
        cls.root = Path(cls.temp.name)
        cls.source = cls.root / "source"
        cls.source.mkdir()
        image = Image.new("RGBA", (1200, 600), (20, 80, 160, 150))
        image.save(cls.source / "used.png")
        Image.new("RGB", (100, 50), "red").save(cls.source / "unused.png")
        (cls.source / "fixture.tex").write_text(r"""\documentclass{article}
\usepackage{graphicx}
\usepackage{hyperref}
\begin{document}
Unchanged text and a \href{https://example.org}{link}.
\includegraphics[width=1in]{used.png}
\newpage
Largest placement: \includegraphics[width=2in]{used.png}
\end{document}
""")
        (cls.source / "references.bib").write_text("% Test bibliography\n")
        (cls.source / "assets").mkdir()
        vector = PdfWriter()
        vector.add_blank_page(width=100, height=50)
        vector.write(cls.source / "assets" / "logo.pdf")
        (cls.source / "assets" / "logo.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"/>')
        cls.compile(cls.source)
        cls.before = {p.name: hashlib.sha256(p.read_bytes()).digest()
                      for p in cls.source.iterdir() if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def compile(directory):
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-halt-on-error", "-interaction=batchmode", "fixture.tex"],
                cwd=directory, capture_output=True, text=True,
            )
            if result.returncode:
                raise AssertionError((directory / "fixture.log").read_text())

    def test_real_pdf_staging_transparency_content_and_source_preservation(self):
        output = self.root / "staged"
        output.mkdir()
        (output / "stale.png").write_bytes(b"stale")
        stage_images(self.source, self.source / "fixture.pdf", output, 200)
        self.assertFalse((output / "stale.png").exists())
        for name in ("unused.png", "fixture.tex", "references.bib"):
            self.assertEqual((self.source / name).read_bytes(), (output / name).read_bytes())
        for name in ("logo.pdf", "logo.svg"):
            self.assertEqual((self.source / "assets" / name).read_bytes(),
                             (output / "assets" / name).read_bytes())
        with Image.open(output / "used.png") as image:
            self.assertEqual(image.size, (401, 201))
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.getextrema()[3], (150, 150))
        self.compile(output)
        verify(self.source / "fixture.pdf", output / "fixture.pdf")
        resolutions = image_resolutions(output / "fixture.pdf")
        # Both placements share one embedded image; the largest gets ~200 DPI.
        self.assertEqual(len(resolutions), 1)
        self.assertTrue(all(200 <= value <= 201 for value in next(iter(resolutions.values()))))
        self.assertEqual(self.before, {p.name: hashlib.sha256(p.read_bytes()).digest()
                                      for p in self.source.iterdir() if p.is_file()})

    def test_rejects_source_overwrite_and_invalid_dpi(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            stage_images(self.source, self.source / "fixture.pdf", self.source, 200)
        with self.assertRaisesRegex(ValueError, "positive"):
            stage_images(self.source, self.source / "fixture.pdf", self.root / "bad", 0)
        self.assertFalse((self.root / "bad").exists())

    def test_unmatched_image_fails_before_staging(self):
        empty = self.root / "empty"
        empty.mkdir()
        output = self.root / "unmatched"
        with self.assertRaisesRegex(ValueError, "does not match"):
            stage_images(empty, self.source / "fixture.pdf", output, 200)
        self.assertFalse(output.exists())

    def test_upload_limit_is_strict(self):
        pdf = self.source / "fixture.pdf"
        with self.assertRaisesRegex(ValueError, "must be below"):
            verify(pdf, pdf, max_bytes=pdf.stat().st_size)

    def test_verifier_rejects_changed_text_page_count_links_sizes_and_images(self):
        for change, message in (
            ("count", "Page counts"), ("text", "text differs"),
            ("links", "links differ"), ("size", "dimensions differ"),
            ("images", "image counts differ"),
        ):
            with self.subTest(change=change):
                writer = PdfWriter(clone_from=self.source / "fixture.pdf")
                page = writer.pages[0]
                if change == "count":
                    writer.remove_page(1)
                elif change == "text":
                    content = page.get_contents()
                    font = next(iter(page["/Resources"]["/Font"]))
                    extra = f"\nBT {font} 10 Tf (Different) Tj ET\n".encode("ascii")
                    content.set_data(content.get_data() + extra)
                    page.replace_contents(content)
                elif change == "links":
                    page["/Annots"][0].get_object()["/A"].get_object().clear()
                elif change == "size":
                    page.mediabox.upper_right = (100, 100)
                else:
                    content = page.get_contents()
                    content.operations = [(args, operator) for args, operator in content.operations
                                          if operator != b"Do"]
                    page.replace_contents(content)
                    page["/Resources"]["/XObject"].clear()
                changed = self.root / f"changed-{change}.pdf"
                writer.write(changed)
                with self.assertRaisesRegex(ValueError, message):
                    verify(self.source / "fixture.pdf", changed)


if __name__ == "__main__":
    unittest.main()
