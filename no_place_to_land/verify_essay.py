#!/usr/bin/env python3
"""Falsify manuscript loss, broken front matter, or missing PDF navigation."""

from pathlib import Path
import re
import subprocess
import unicodedata
import json
from urllib.parse import unquote

from pypdf import PdfReader


def normalized(text):
    # Line-end hyphenation, punctuation, and decomposed ligatures are typography.
    return ''.join(c for c in unicodedata.normalize('NFKD', text).casefold()
                   if c.isalnum())


def manuscript_part(part):
    plain = subprocess.run(
        ['pandoc', 'no-place-to-land.md', '--to=plain', '--wrap=none',
         '--from=markdown'],
        check=True, capture_output=True, text=True,
    ).stdout
    # Read the independent full manuscript, without the build's splitting filter.
    abstract, body = plain.split('\nIntroduction\n', 1)
    if part == 'abstract':
        return abstract.split('\nAbstract\n', 1)[1].strip()
    return 'Introduction\n' + body


def outline_titles(items):
    for item in items:
        if isinstance(item, list):
            yield from outline_titles(item)
        else:
            yield str(item.title)


def bibliography_records():
    return json.loads(subprocess.run(
        ['pandoc', 'references.bib', '--from=biblatex', '--to=csljson'],
        check=True, capture_output=True, text=True,
    ).stdout)


def verify(path):
    reader = PdfReader(path)
    assert reader.metadata.title == 'No Place To Land', 'Incorrect PDF title'
    assert reader.metadata.author == 'Michel Blomgren', 'Incorrect PDF author'
    assert len(reader.pages) >= 4, 'Cover, contents, or essay body missing'
    cover = reader.pages[0].extract_text()
    assert 'No Place' in cover and 'To Land' in cover, 'Cover title spacing is incorrect'
    assert normalized(manuscript_part('abstract')) in normalized(cover), \
        'The complete abstract must appear on the cover'
    assert 'Michel Blomgren' in cover and 'mike@c89.systems' in cover
    contents = reader.pages[1].extract_text()
    assert 'Contents' in contents and 'Conclusion' in contents

    text = []
    for page in reader.pages[2:]:
        extracted = page.extract_text()
        extracted = re.sub(r'Page\s+\d+\s+of\s+\d+', '', extracted)
        extracted = extracted.replace('No Place To Land', '').replace('C89 Systems', '')
        text.append(extracted)
    body = normalized('\n'.join(text))
    paragraphs = [p for p in manuscript_part('body').split('\n\n') if p.strip()]
    position = 0
    for paragraph in paragraphs:
        # Only inserted author-year citations may interrupt the manuscript text.
        fragments = [normalized(p) for p in re.split(r'\[@[^\]]+\]', paragraph)]
        previous_end = None
        for fragment in filter(None, fragments):
            start = body.find(fragment, position)
            assert start >= 0, f'Manuscript text missing: {paragraph[:100]}'
            if previous_end is not None:
                assert start - previous_end <= 250, 'Unexpected text between citation fragments'
            position = start + len(fragment)
            previous_end = position

    links = []
    for page in reader.pages:
        for ref in page.get('/Annots', []):
            action = ref.get_object().get('/A', {})
            if action.get('/URI'):
                links.append(str(action['/URI']))
    for uri in ('https://c89.systems/10x.pdf', 'https://c89.systems/10x.md',
                'mailto:mike@c89.systems'):
        assert uri in links, f'Missing publication link: {uri}'
    records = bibliography_records()
    research_links = {unquote(r['URL']) for r in records if r.get('URL')}
    research_links.update('https://doi.org/' + unquote(r['DOI'])
                          for r in records if r.get('DOI'))
    actual_links = {unquote(uri) for uri in links}
    assert research_links.issubset(actual_links), \
        f'Bibliography links missing: {research_links.difference(actual_links)}'
    assert not any('pkt.systems/10x' in uri for uri in links), 'Old 10x URL retained'

    cited = set(re.findall(r'\[@([\w-]+)\]', Path('no-place-to-land.md').read_text()))
    assert cited == {r['id'] for r in records}, 'Missing or uncited bibliography entries'
    destinations = reader.named_destinations
    for key in cited:
        assert f'cite.0@{key}' in destinations, f'Bibliography destination missing: {key}'
    bibliography_page = min(reader.get_destination_page_number(destinations[f'cite.0@{key}'])
                            for key in cited)
    assert 'References' in '\n'.join(page.extract_text()
                                    for page in reader.pages[bibliography_page:])
    for page in reader.pages[2:bibliography_page]:
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            assert not action.get('/URI') or action['/URI'] == 'https://c89.systems', \
                'External source link retained inside essay prose'
    for record in records:
        page = reader.get_destination_page_number(destinations[f"cite.0@{record['id']}"])
        nearby = '\n'.join(p.extract_text() for p in reader.pages[page:page + 2])
        nearby = re.sub(r'Page\s+\d+\s+of\s+\d+', '', nearby)
        nearby = nearby.replace('No Place To Land', '').replace('C89 Systems', '')
        assert normalized(record['title']) in normalized(nearby), \
            f"Bibliography title missing: {record['id']}"

    titles = list(outline_titles(reader.outline))
    expected = ['Introduction'] + re.findall(r'^## (\d+\. .+)$',
                                            Path('no-place-to-land.md').read_text(), re.M)
    expected += ['Conclusion — From Coordination to Conversion', 'References']
    for title in expected:
        assert title in titles, f'PDF bookmark missing: {title}'
        assert normalized(title) in normalized(contents), f'Contents entry missing: {title}'
    navigation = [a.get_object().get('/A', {})
                  for a in reader.pages[1].get('/Annots', [])]
    assert sum(a.get('/S') == '/GoTo' for a in navigation) >= len(expected), \
        'Contents entries must link to the essay chapters'
    for page in reader.pages:
        assert abs(float(page.mediabox.width) - 595.276) < 1
        assert abs(float(page.mediabox.height) - 841.89) < 1
    print(f'{path}: {len(reader.pages)} A4 pages; {len(paragraphs)} manuscript '
          f'blocks retained; {len(cited)} references, citation destinations, '
          f'cover abstract, metadata, source URLs, and navigation verified')


if __name__ == '__main__':
    for name in ('no-place-to-land.pdf', 'no-place-to-land-squeezed.pdf'):
        verify(name)
