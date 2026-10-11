# Building 10x

Run `make` in this directory to produce both `10x.pdf` (original images) and
`10x-squeezed.pdf` (for distribution). Copies also live under `build/`.

Dependencies: the existing pdfLaTeX/BibTeX setup, Python 3 with Pillow and pypdf,
and Poppler's `pdfimages` command. Install the Python dependencies with
`python3 -m pip install Pillow pypdf` if needed.

The squeezed build measures each PNG's effective DPI in the full-size PDF,
then resamples a separate copy to approximately 200 DPI at its largest actual
placement. It preserves aspect ratios and transparency and never enlarges an
image. The cover and any other images already below the target stay unchanged.
Unused PNGs are copied unchanged because they do not affect PDF size. All source
PNGs remain untouched; generated assets live in `build/squeezed/`.

To change the target, use `make SQUEEZED_DPI=150`. A changed DPI or edited source
automatically rebuilds the squeezed PDF. `make` rejects squeezed outputs at or
above 20,000,000 bytes and verifies unchanged page counts, text, page dimensions,
URI links and image counts. Text, fonts, tables and hyperlinks remain native PDF
content; only the staged PNGs are resized.

Run `make check` for the automated tests and PDF checks. `make release` packages
both PDFs in `10x.zip`. `make clean` removes generated build files and PDFs.
