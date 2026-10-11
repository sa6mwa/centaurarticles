#!/usr/bin/env python3
"""Falsify manuscript loss, broken front matter, or missing PDF navigation."""

from pathlib import Path
import re
import subprocess
import unicodedata
import json
from urllib.parse import unquote

from pypdf import PdfReader
from PIL import Image
from squeeze import pixel_key


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


def outline_entries(items):
    for item in items:
        if isinstance(item, list):
            yield from outline_entries(item)
        else:
            yield item


def bibliography_records():
    return json.loads(subprocess.run(
        ['pandoc', 'references.bib', '--from=biblatex', '--to=csljson'],
        check=True, capture_output=True, text=True,
    ).stdout)


def verify_body_art(reader, path):
    plan_path = Path('illustrations/body-art.json')
    figures = json.loads(plan_path.read_text())['figures']
    assert len(figures) == 8, 'The body illustration set must contain eight figures'
    text = '\n'.join(page.extract_text() for page in reader.pages[2:])
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text).replace('No Place To Land', '')
    raster_count = 0
    wide_count = 0
    for figure in figures:
        anchor = f"figure.{figure['number']}"
        assert anchor in reader.named_destinations, f'Figure anchor missing: {anchor}'
        page_number = reader.get_destination_page_number(reader.named_destinations[anchor])
        assert normalized(figure['caption']) in normalized(text), \
            f"Figure caption missing: {figure['label']}"
        assert normalized(figure['caption']) in normalized(reader.pages[page_number].extract_text()), \
            f"Figure caption separated from its anchor: {figure['label']}"
        if 'file' in figure:
            raster_count += 1
            source = plan_path.parent / figure['file']
            if 'squeezed' in Path(path).stem:
                source = Path('build/squeezed') / source.name
            with Image.open(source) as image:
                expected = pixel_key(image)
            assert any(pixel_key(image.image) == expected
                       for image in reader.pages[page_number].images), \
                f"Figure image and caption must share a page: {figure['label']}"
            if figure['number'] == 1:
                matched = next(image for image in reader.pages[page_number].images
                               if pixel_key(image.image) == expected)
                widths = []
                def placement(op, operands, cm, tm):
                    if op == b'Do' and str(operands[0]) == '/' + matched.name.rsplit('.', 1)[0]:
                        widths.append((cm[0] ** 2 + cm[1] ** 2) ** 0.5)
                reader.pages[page_number].extract_text(visitor_operand_before=placement)
                assert widths and max(widths) > 440, 'Factory scene must span both columns'
        if figure['width'] == 'text':
            wide_count += 1
    assert raster_count == 5 and wide_count == 6, 'Illustration media or width balance changed'
    for detail in ('Task effort', 'Completed work', 'Wages and hours',
                   'Contributions kept separate', 'Completion held together', 'Ordinary offers',
                   'The versioned operating blueprint', 'Git history', 'service/', 'runbooks/',
                   'Deployable artifacts', 'Recoverable state', 'Verification evidence',
                   'Access and authority', 'Next authorised operator',
                   'The service continues'):
        assert normalized(detail) in normalized(text), f'Native drawing detail missing: {detail}'
    for number, detail in ((4, 'Ordinary offers'), (8, 'The versioned operating blueprint')):
        page = reader.get_destination_page_number(reader.named_destinations[f'figure.{number}'])
        assert normalized(detail) in normalized(reader.pages[page].extract_text()), \
            f'Native drawing separated from its caption: figure {number}'
    assert 'Customer benefit remains a separate proposition to test' not in text
    factory_page = reader.get_destination_page_number(reader.named_destinations['figure.1'])
    assert factory_page == 4, 'The full-width factory illustration must remain on page 5'
    return len(figures)


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
    assert 'Sustained use' in contents and 'Capability frontier' in contents, \
        'Contents illustration legend missing'
    assert len(reader.pages[1].images) == 1, 'Contents landscape image missing'
    assert reader.pages[1].images[0].image.mode == 'RGBA', \
        'Contents landscape must preserve its transparent background'

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

    entries = list(outline_entries(reader.outline))
    titles = [str(entry.title) for entry in entries]
    expected = ['Introduction'] + re.findall(r'^## (\d+\. .+)$',
                                            Path('no-place-to-land.md').read_text(), re.M)
    expected += ['Conclusion — From Coordination to Conversion', 'References']
    for title in expected:
        assert title in titles, f'PDF bookmark missing: {title}'
        assert normalized(title) in normalized(contents), f'Contents entry missing: {title}'
    starts = {str(entry.title): reader.get_destination_page_number(entry)
              for entry in entries if str(entry.title) in expected}
    assert len(set(starts.values())) == len(expected), \
        'Major sections must start on separate pages'
    assert starts['Introduction'] == 2 and starts[expected[1]] == 3, \
        'The introduction must occupy page 3, with chapter 1 starting on page 4'
    for title, number in starts.items():
        beginning = reader.pages[number].extract_text().replace('No Place To Land', '')
        assert normalized(beginning).startswith(normalized(title)), \
            f'Major section does not begin at the top of its page: {title}'
    navigation = [a.get_object().get('/A', {})
                  for a in reader.pages[1].get('/Annots', [])]
    assert sum(a.get('/S') == '/GoTo' for a in navigation) >= len(expected), \
        'Contents entries must link to every chapter'
    for title in re.findall(r'^### (.+)$', Path('no-place-to-land.md').read_text(), re.M):
        assert title in titles, f'PDF subsection bookmark missing: {title}'
        assert normalized(title) not in normalized(contents), \
            f'Subsection retained in chapter-only contents: {title}'
    producer = next(entry for entry in entries if entry.title == 'When the producer moves ahead')
    producer_page = reader.get_destination_page_number(producer)
    assert producer_page == starts[expected[1]] + 1, \
        'Producer subsection must remain on the second page of chapter 1'
    page_box = reader.pages[producer_page].mediabox
    assert float(producer.left) > float(page_box.width) / 2, \
        'Producer subsection must start in the right column'
    assert float(producer.top) > float(page_box.height) - 100, \
        'Producer subsection must start at the top of its column'
    assert re.search(r'\.(?:\s*\.){4,}', contents), 'Contents dotted leaders missing'
    assert reader.pages[2].extract_text().count('Introduction') >= 1, \
        'The complete contents must fit on page 2, with the essay beginning on page 3'
    for page in reader.pages:
        assert abs(float(page.mediabox.width) - 595.276) < 1
        assert abs(float(page.mediabox.height) - 841.89) < 1
    figure_count = verify_body_art(reader, path)
    print(f'{path}: {len(reader.pages)} A4 pages; {len(paragraphs)} manuscript '
          f'blocks retained; {len(cited)} references, citation destinations, '
          f'cover abstract, metadata, source URLs, navigation, and '
          f'{len(starts)} major section page starts, and {figure_count} body illustrations verified')


if __name__ == '__main__':
    for name in ('no-place-to-land.pdf', 'no-place-to-land-squeezed.pdf'):
        verify(name)
