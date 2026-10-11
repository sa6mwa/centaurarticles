import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from pypdf import PdfReader


class BibliographyTests(unittest.TestCase):
    def test_all_citations_resolve_to_distinct_complete_records(self):
        records = json.loads(subprocess.check_output(
            ['pandoc', 'references.bib', '--from=biblatex', '--to=csljson'], text=True))
        keys = [r['id'] for r in records]
        self.assertEqual(len(keys), 47)
        self.assertEqual(len(keys), len(set(keys)))
        cited = set(re.findall(r'\[@([\w-]+)\]', Path('no-place-to-land.md').read_text()))
        self.assertEqual(cited, set(keys))
        for record in records:
            with self.subTest(source=record['id']):
                self.assertTrue(record.get('author'))
                self.assertTrue(record.get('title'))
                self.assertTrue(record.get('issued'))
                self.assertTrue(record.get('URL') or record.get('DOI'))

    def test_latex_uses_native_citations_instead_of_inline_source_links(self):
        result = subprocess.run(
            ['pandoc', 'no-place-to-land.md', '--to=latex', '--natbib',
             '--lua-filter=manuscript.lua', '-M', 'part=body'],
            check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn(r'\citep{blomgren2025coordination}', result)
        self.assertIn(r'\citep{vonhippel1986leadusers}', result)
        self.assertNotIn(r'\href{', result)
        self.assertNotIn('https://', result)
        self.assertEqual(set(re.findall(r'\\citep\{([^}]+)\}', result)),
                         set(re.findall(r'\[@([\w-]+)\]', Path('no-place-to-land.md').read_text())))

    def test_bibtex_build_refreshes_changed_records(self):
        Path('build').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir='build', prefix='bibliography-test-') as temporary:
            root = Path(temporary)
            shutil.copy2('mkpdf.sh', root / 'mkpdf.sh')
            (root / 'fixture.tex').write_text(r'''\documentclass{article}
\usepackage[backend=bibtex,style=authoryear,natbib=true]{biblatex}
\addbibresource{references.bib}
\begin{document}
An observable citation \citep{sample}.
\printbibliography
\end{document}
''')
            for year in (2024, 2025):
                (root / 'references.bib').write_text(
                    '@article{sample, author={Researcher, Alice}, '
                    'title={A Verified Source}, journal={Example Journal}, '
                    f'year={{{year}}}' + '}\n')
                result = subprocess.run(['bash', 'mkpdf.sh', 'fixture.tex'], cwd=root,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout[-3000:])
                text = '\n'.join(p.extract_text() for p in PdfReader(root / 'build/fixture.pdf').pages)
                self.assertIn(str(year), text)
                self.assertIn('A Verified Source', text)
                if year == 2025:
                    self.assertNotIn('2024', text)
