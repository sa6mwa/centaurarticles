from pathlib import Path
import subprocess
import unittest


class ManuscriptBuildTests(unittest.TestCase):
    def convert(self, part):
        return subprocess.run(
            ['pandoc', 'no-place-to-land.md', '--to=plain', '--wrap=none',
             '--lua-filter=manuscript.lua', '-M', f'part={part}'],
            capture_output=True, text=True,
        )

    def test_cover_has_only_the_complete_abstract(self):
        result = self.convert('abstract')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('This essay examines why'))
        self.assertTrue(result.stdout.strip().endswith('capacity to put them to use.'))
        self.assertNotIn('Introduction', result.stdout)
        self.assertNotIn('No Place To Land', result.stdout)

    def test_body_includes_all_chapters_without_the_cover_abstract(self):
        result = self.convert('body')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('Introduction\n'))
        self.assertNotIn('This essay examines why', result.stdout)
        for line in Path('no-place-to-land.md').read_text().splitlines():
            if line.startswith('## ') and line != '## Abstract':
                self.assertIn(line[3:].replace('’', "'"), result.stdout.replace('’', "'"))
        self.assertTrue(result.stdout.strip().endswith('after the technology is finished.'))

    def test_unknown_manuscript_part_fails_with_actionable_error(self):
        result = self.convert('unknown')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Select -M part=abstract or -M part=body', result.stderr)

    def test_missing_tex_argument_reports_usage(self):
        result = subprocess.run(['bash', 'mkpdf.sh'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('file.tex', result.stdout)
