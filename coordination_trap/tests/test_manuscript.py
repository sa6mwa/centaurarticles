import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

from verify_essay import (normalized, verify_paragraph_flow,
                          verify_background_extent, verify_gutter_geometry)


class ManuscriptTests(unittest.TestCase):
    def test_artwork_and_c89_assets_match_recorded_originals(self):
        provenance = json.loads(Path('illustrations/provenance.json').read_text())
        assets = ([provenance['cover'], provenance['original_cover'],
                   provenance['cover_reference']] + provenance['branding'] +
                  provenance['body_art'] + provenance['cover_font'])
        for asset in assets:
            with self.subTest(asset=asset['file']):
                self.assertEqual(hashlib.sha256(Path(asset['file']).read_bytes()).hexdigest(),
                                 asset['sha256'])

    def test_cover_type_is_embedded_selectable_and_uses_the_bundled_font(self):
        text = subprocess.check_output(['pdftotext', 'assets/cover-type.pdf', '-'], text=True)
        self.assertEqual(normalized(text), normalized(
            'The Coordination Trap When execution outruns the enterprise'))
        fonts = subprocess.check_output(['pdffonts', 'assets/cover-type.pdf'], text=True)
        self.assertRegex(fonts, r'BebasNeue-Regular\s+TrueType\s+\S+\s+yes\s+yes\s+yes')
        self.assertIn('SIL OPEN FONT LICENSE Version 1.1', Path('assets/fonts/OFL.txt').read_text())

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
        self.assertEqual(re.findall(r'\\href\{([^}]+)\}', result.stdout),
                         ['https://c89.systems/10x.pdf'])
        self.assertIn(r'\href{https://c89.systems/10x.pdf}{\emph{The Coordination Shift}}',
                      result.stdout)
        self.assertEqual(result.stdout.count(r'\SurveyFigure'), 1)
        self.assertEqual(result.stdout.count(r'\OutcomeFigure'), 1)
        self.assertEqual(result.stdout.count(r'\PortfolioFigure'), 1)
        self.assertEqual(result.stdout.count(r'\SafetyFigure'), 1)
        self.assertEqual(result.stdout.count(r'\GutterQuote'), 3)
        self.assertEqual(result.stdout.count(r'\NextGutterColumn'), 3)
        self.assertNotIn(r'\PullQuote', result.stdout)
        self.assertNotIn('OpeningLead', result.stdout)
        self.assertNotIn('ContinuedSection', result.stdout)
        self.assertEqual(result.stdout.count(r'\EssayArt'), 3)
        self.assertNotIn(r'\UnitComic', result.stdout)
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

    def test_every_prose_paragraph_is_inside_two_column_flow(self):
        result = self.convert('body', 'json')
        self.assertEqual(result.returncode, 0, result.stderr)
        inside_columns = False
        for block in json.loads(result.stdout)['blocks']:
            if block['t'] == 'RawBlock':
                text = block['c'][1]
                if r'\begin{EssayColumns}' in text:
                    self.assertFalse(inside_columns)
                    inside_columns = True
                if r'\end{EssayColumns}' in text:
                    self.assertTrue(inside_columns)
                    inside_columns = False
            elif block['t'] == 'Para':
                self.assertTrue(inside_columns, 'A prose paragraph escaped the two-column layout')
        self.assertFalse(inside_columns)

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

    def test_full_page_background_accepts_exact_cover_and_overscan(self):
        verify_background_extent([595, 0, 0, 842, 0, 0], 595, 842)
        verify_background_extent([601, 0, 0, 848, -3, -3], 595, 842)

    def test_full_page_background_rejects_image_strips_and_inset_images(self):
        for matrix in ([595, 0, 0, 300, 0, 200], [550, 0, 0, 842, 20, 0],
                       [595, 0, 0, 842, 0, -100]):
            with self.subTest(matrix=matrix), self.assertRaisesRegex(AssertionError, 'not full-page'):
                verify_background_extent(matrix, 595, 842)

    def gutter_words(self):
        return [(100, 207, 230, 217), (370, 207, 450, 217),
                (250, 140, 280, 150), (320, 140, 340, 150),
                (250, 280, 280, 290), (320, 280, 340, 290)]

    def test_gutter_quote_has_prose_on_both_sides_and_normal_columns_above_below(self):
        verify_gutter_geometry((240, 200, 360, 230), self.gutter_words(), 600)

    def test_gutter_quote_rejects_banners_overlap_or_missing_prose(self):
        cases = [self.gutter_words()[1:], self.gutter_words()[:4],
                 self.gutter_words() + [(245, 207, 260, 217)]]
        for words in cases:
            with self.subTest(words=words), self.assertRaises(AssertionError):
                verify_gutter_geometry((240, 200, 360, 230), words, 600)
        with self.assertRaisesRegex(AssertionError, 'not centered'):
            verify_gutter_geometry((50, 200, 170, 230), self.gutter_words(), 600)

    def test_gutter_quote_checks_clearance_against_each_visible_line(self):
        quote = (240, 200, 360, 230)
        rows = [(240, 200, 360, 211), (255, 218, 345, 230)]
        words = self.gutter_words() + [(245, 220, 250, 229), (350, 220, 355, 229)]
        verify_gutter_geometry(quote, words, 600, rows)
        with self.assertRaisesRegex(AssertionError, 'Prose overlaps'):
            verify_gutter_geometry(quote, words + [(260, 220, 280, 229)], 600, rows)

    def test_wrapped_columns_allow_optical_protrusion_at_their_edges(self):
        words = [(55, 207, 229, 217), (371, 207, 545, 217)] + self.gutter_words()[2:]
        verify_gutter_geometry((240, 200, 360, 230), words, 600, wrap_width=120)

    def test_wrapped_columns_reject_words_in_the_padding_or_outside_the_page_margin(self):
        normal = [(100, 207, 226, 217), (374, 207, 450, 217)] + self.gutter_words()[2:]
        for overrun in [(100, 207, 234, 217), (366, 207, 450, 217),
                        (50, 207, 226, 217), (374, 207, 550, 217),
                        (100, 194, 234, 199), (366, 231, 450, 236)]:
            with self.subTest(overrun=overrun), self.assertRaisesRegex(
                    AssertionError, 'escapes the wrapped column'):
                verify_gutter_geometry((240, 200, 360, 230), normal + [overrun],
                                       600, wrap_width=120)

    def test_missing_tex_argument_reports_usage(self):
        result = subprocess.run(['bash', 'mkpdf.sh'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('file.tex', result.stdout)
