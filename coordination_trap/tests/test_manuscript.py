import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

from verify_essay import normalized, verify_paragraph_flow


class ManuscriptTests(unittest.TestCase):
    def test_artwork_and_c89_assets_match_recorded_originals(self):
        provenance = json.loads(Path('illustrations/provenance.json').read_text())
        for asset in [provenance['cover']] + provenance['branding'] + provenance['body_art']:
            with self.subTest(asset=asset['file']):
                self.assertEqual(hashlib.sha256(Path(asset['file']).read_bytes()).hexdigest(),
                                 asset['sha256'])

    def convert(self, part, output='plain', source='coordination-trap.md'):
        return subprocess.run(
            ['pandoc', source, '--to=' + output, '--wrap=none', '--natbib',
             '--lua-filter=manuscript.lua', '-M', f'part={part}'],
            capture_output=True, text=True)

    def test_cover_contains_the_complete_abstract_only(self):
        result = self.convert('abstract')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('Companies are buying'))
        self.assertTrue(result.stdout.strip().endswith('blame the technology?'))
        self.assertLessEqual(len(result.stdout.split()), 55)
        self.assertNotIn('Introduction', result.stdout)
        self.assertNotIn('When I read', result.stdout)

    def test_body_preserves_every_section_and_final_paragraph(self):
        result = self.convert('body')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('Introduction\n'))
        for heading in re.findall(r'^## (.+)$', Path('coordination-trap.md').read_text(), re.M):
            if heading != 'Abstract':
                self.assertIn(heading, result.stdout)
        self.assertNotIn('Companies are buying new productive capabilities', result.stdout)
        self.assertTrue(result.stdout.strip().endswith('abundance to emerge from the queue.'))

    def test_invalid_or_missing_part_fails_with_actionable_error(self):
        for part in ('unknown', ''):
            result = self.convert(part)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Select -M part=abstract or -M part=body', result.stderr)

    def test_missing_abstract_is_rejected(self):
        result = subprocess.run(
            ['pandoc', '--to=latex', '--lua-filter=manuscript.lua', '-M', 'part=abstract'],
            input='## Introduction\n\nAn essay without an abstract.\n',
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requested manuscript part is empty', result.stderr)

    def test_every_source_is_complete_unique_and_cited(self):
        records = json.loads(subprocess.check_output(
            ['pandoc', 'references.bib', '--from=biblatex', '--to=csljson'], text=True))
        keys = [r['id'] for r in records]
        self.assertEqual(len(keys), len(set(keys)))
        cited = set(re.findall(r'\[@([\w-]+)\]', Path('coordination-trap.md').read_text()))
        self.assertEqual(cited, set(keys))
        self.assertTrue({'hastings2026deployment', 'slok2026payoff'} <= cited)
        for record in records:
            with self.subTest(source=record['id']):
                self.assertTrue(record.get('author'))
                self.assertTrue(record.get('title'))
                self.assertTrue(record.get('issued') or record.get('accessed'))
                self.assertTrue(record.get('URL') or record.get('DOI'))

    def test_sources_become_native_citations_and_figures_are_placed(self):
        result = self.convert('body', 'latex')
        self.assertEqual(result.returncode, 0, result.stderr)
        cited = set(re.findall(r'\[@([\w-]+)\]', Path('coordination-trap.md').read_text()))
        self.assertEqual(set(re.findall(r'\\citep\{([^}]+)\}', result.stdout)), cited)
        self.assertNotIn('https://', result.stdout)
        self.assertEqual(result.stdout.count(r'\SurveyFigure'), 1)
        self.assertEqual(result.stdout.count(r'\OutcomeFigure'), 1)
        self.assertEqual(result.stdout.count(r'\PortfolioFigure'), 1)
        self.assertEqual(result.stdout.count(r'\SafetyFigure'), 1)
        self.assertEqual(result.stdout.count(r'\PullQuote'), 3)
        self.assertEqual(result.stdout.count(r'\EssayArt'), 3)
        self.assertEqual(result.stdout.count(r'\begin{EssayColumns}'),
                         result.stdout.count(r'\end{EssayColumns}'))

    def test_changed_paragraph_structure_requires_layout_review(self):
        source = Path('coordination-trap.md').read_text().replace(
            '## The unit of work has changed',
            'An additional paragraph.\n\n## The unit of work has changed')
        result = subprocess.run(
            ['pandoc', '--to=latex', '--lua-filter=manuscript.lua', '-M', 'part=body'],
            input=source, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Editorial layout needs review', result.stderr)

    def test_changed_section_order_requires_layout_review(self):
        source = Path('coordination-trap.md').read_text().replace(
            '## The unit of work has changed', '## A different section')
        result = subprocess.run(
            ['pandoc', '--to=latex', '--lua-filter=manuscript.lua', '-M', 'part=body'],
            input=source, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Editorial layout needs review', result.stderr)

    def test_pdf_flow_accepts_complete_paragraphs_and_citation_expansion(self):
        verify_paragraph_flow(['A complete thought [@source] ends here.', 'Next paragraph.'], [
            (normalized('A complete thought (Author, 2026) ends here.'), 2, 'left'),
            (normalized('Next paragraph.'), 2, 'right')])

    def test_pdf_flow_rejects_a_paragraph_split_across_pages_or_columns(self):
        for location in [(3, 'left'), (2, 'right')]:
            with self.subTest(location=location), self.assertRaisesRegex(AssertionError, 'crosses'):
                verify_paragraph_flow(['A complete thought ends here.'], [
                    (normalized('A complete thought'), 2, 'left'),
                    (normalized('ends here.'), *location)])

    def test_pdf_flow_rejects_missing_or_reordered_text(self):
        for text in ['A thought ends here.', 'ends here. A complete thought']:
            with self.subTest(text=text), self.assertRaisesRegex(AssertionError, 'missing or out of order'):
                verify_paragraph_flow(['A complete thought ends here.'], [(normalized(text), 2, 'left')])

    def test_missing_tex_argument_reports_usage(self):
        result = subprocess.run(['bash', 'mkpdf.sh'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('file.tex', result.stdout)
