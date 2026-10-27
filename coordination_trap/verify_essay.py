#!/usr/bin/env python3
"""Check manuscript coverage, cover, citations, figures and PDF navigation."""

import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote

from PIL import Image
from pypdf import PdfReader

from squeeze import pixel_key

NAME = "coordination-trap"


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text).casefold()
                   if c.isalnum())


def manuscript_parts():
    # Independently read the complete manuscript, without the build's Lua filter.
    plain = subprocess.check_output(
        ['pandoc', f'{NAME}.md', '--from=markdown', '--to=plain', '--wrap=none'],
        text=True)
    front, body = plain.split('\nIntroduction\n', 1)
    return front.split('\nAbstract\n', 1)[1].strip(), 'Introduction\n' + body


def bibliography_records():
    return json.loads(subprocess.check_output(
        ['pandoc', 'references.bib', '--from=biblatex', '--to=csljson'], text=True))


def outline_entries(items):
    for item in items:
        if isinstance(item, list):
            yield from outline_entries(item)
        else:
            yield item


def without_furniture(text):
    return re.sub(r'Page\s+\d+\s+of\s+\d+', '', text).replace(
        'The Coordination Trap', '').replace('C89 Systems', '')


def without_figures(text):
    # Remove the known figure blocks, checked independently below.
    text = re.sub(r'Where the working week goes.*?Figure 1:.*?Zimmerman,\s*2026\)\.',
                  '', text, flags=re.S)
    text = re.sub(r'Four partial answers.*?Figure 2:.*?Zimmerman,\s*2026\)\.',
                  '', text, flags=re.S)
    text = re.sub(r'Make the whole outcome operable.*?Figure 3:.*?support the unit\.',
                  '', text, flags=re.S)
    return re.sub(r'The path to intervention.*?Figure 4:.*?after intervention\.',
                  '', text, flags=re.S)


def verify_paragraph_flow(paragraphs, runs):
    """Every paragraph must occupy one page and one column (or full-width band).

    Runs contain normalized body text with its rendered page and column. Large
    pull quotes, headings, captions and running furniture are excluded by the
    PDF reader, so repeated quotations cannot masquerade as manuscript coverage.
    """
    text = ''.join(run[0] for run in runs)
    locations = [(page, column) for content, page, column in runs for _ in content]
    position = 0
    for paragraph in paragraphs:
        fragments = list(filter(None, (normalized(p) for p in
                             re.split(r'\[@[^\]]+\]', paragraph))))
        first = None
        for fragment in fragments:
            start = text.find(fragment, position)
            assert start >= 0, f'Body paragraph missing or out of order: {paragraph[:90]}'
            if first is None:
                first = start
            position = start + len(fragment)
        occupied = set(locations[first:position])
        assert len(occupied) == 1, f'Paragraph crosses a page or column: {paragraph[:90]}'


def verify(path):
    reader = PdfReader(path)
    abstract, manuscript = manuscript_parts()
    assert reader.metadata.title == 'The Coordination Trap', 'Incorrect PDF title'
    assert reader.metadata.author == 'Michel Blomgren', 'Incorrect PDF author'
    assert len(reader.pages) == 11, 'Editorial pagination changed; review every spread'
    cover = reader.pages[0].extract_text()
    assert normalized('The Coordination Trap') in normalized(cover), 'Cover title missing'
    assert normalized(abstract) in normalized(cover), 'Complete cover abstract missing'
    assert 'Michel Blomgren' in cover and 'mike@c89.systems' in cover
    assert len(reader.pages[0].images) == 1, 'Cover artwork missing'
    image_source = Path('build/squeezed/cover.png' if 'squeezed' in Path(path).stem
                        else 'cover.png')
    with Image.open(image_source) as source:
        assert pixel_key(reader.pages[0].images[0].image) == pixel_key(source), \
            'Wrong cover artwork embedded'
    body_art = {1: 'opening-illustration.png', 4: 'unit-comic.png',
                9: 'closing-illustration.png'}
    for number, page in enumerate(reader.pages[1:], 1):
        assert len(page.images) == (1 if number in body_art else 0), \
            f'Unexpected artwork on page {number + 1}'
        if number in body_art:
            source_path = Path('build/squeezed' if 'squeezed' in Path(path).stem else '.') / body_art[number]
            with Image.open(source_path) as source:
                assert pixel_key(page.images[0].image) == pixel_key(source), \
                    f'Wrong artwork on page {number + 1}'

    extracted = [without_furniture(page.extract_text()) for page in reader.pages[1:]]
    full_text = normalized(without_figures('\n'.join(extracted)))
    assert normalized(abstract) not in full_text, 'Cover abstract repeated in the body'
    assert normalized(extracted[0]).startswith('introduction'), 'Essay must begin on page 2'
    assert 'Contents' not in '\n'.join(extracted), 'Unexpected contents page'
    assert 'computersweden' not in normalized(cover + '\n'.join(extracted)), \
        'Removed publication reappeared'
    assert len(abstract.split()) <= 55, 'Cover abstract is no longer a short executive hook'
    position = 0
    paragraphs = [p for p in manuscript.split('\n\n') if p.strip()]
    for paragraph in paragraphs:
        for fragment in filter(None, (normalized(p) for p in
                                      re.split(r'\[@[^\]]+\]', paragraph))):
            start = full_text.find(fragment, position)
            assert start >= 0, f'Manuscript text missing or out of order: {paragraph[:100]}'
            position = start + len(fragment)

    records = bibliography_records()
    cited = set(re.findall(r'\[@([\w-]+)\]', Path(f'{NAME}.md').read_text()))
    assert cited == {r['id'] for r in records}, 'Missing or uncited bibliography entries'
    assert {'hastings2026deployment', 'slok2026payoff'} <= cited
    destinations = reader.named_destinations
    for key in cited:
        assert f'cite.0@{key}' in destinations, f'Citation destination missing: {key}'
    bibliography_page = min(reader.get_destination_page_number(destinations[f'cite.0@{key}'])
                            for key in cited)
    assert 'References' in reader.pages[bibliography_page].extract_text()
    assert bibliography_page > 1, 'Bibliography must follow the essay'
    headings = [h for h in re.findall(r'^## (.+)$', Path(f'{NAME}.md').read_text(), re.M)
                if h != 'Abstract']
    prose_paragraphs = [p for p in paragraphs if p.strip() not in headings]
    runs = []
    for number in range(1, bibliography_page):
        def collect_body(text, cm, tm, font, size):
            x, y = tm[4] + cm[4], tm[5] + cm[5]
            if (10.5 < size < 11.5 or 15.5 < size < 16.5) and 55 < y < 775:
                content = normalized(text)
                if content:
                    runs.append((content, number, 'right' if x > 295 else 'left'))
        reader.pages[number].extract_text(visitor_text=collect_body)
    verify_paragraph_flow(prose_paragraphs, runs)
    links = set()
    linked_citations = set()
    for number, page in enumerate(reader.pages):
        assert abs(float(page.mediabox.width) - 595.276) < 1
        assert abs(float(page.mediabox.height) - 841.89) < 1
        if number:
            assert f'Page {number + 1} of {len(reader.pages)}' in page.extract_text(), \
                f'Wrong page numbering on page {number + 1}'
            assert 'The Coordination Trap' in page.extract_text() and 'C89 Systems' in page.extract_text(), \
                f'Missing running title or C89 footer on page {number + 1}'
        if 0 < number < bibliography_page:
            columns = [0, 0]
            def count_body_text(text, cm, tm, font, size):
                x, y = tm[4] + cm[4], tm[5] + cm[5]
                if text.strip() and 10 < size < 12 and 80 < y < 770:
                    if 55 < x < 80:
                        columns[0] += 1
                    elif 305 < x < 330:
                        columns[1] += 1
            page.extract_text(visitor_text=count_body_text)
            assert min(columns) >= 3, f'Body page {number + 1} does not contain two text columns'
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            if action.get('/URI'):
                uri = unquote(str(action['/URI']))
                links.add(uri)
                if 0 < number < bibliography_page:
                    assert uri == 'https://c89.systems', 'Source URL left in body prose'
            if action.get('/S') == '/GoTo' and number < bibliography_page:
                linked_citations.add(str(action.get('/D')))
    assert {f'cite.0@{key}' for key in cited} <= linked_citations, \
        'A citation does not link from the essay to its reference'
    assert {'https://c89.systems/10x.pdf', 'mailto:mike@c89.systems'} <= links
    for record in records:
        for uri in ([record['URL']] if record.get('URL') else []) + (
                ['https://doi.org/' + record['DOI']] if record.get('DOI') else []):
            assert unquote(uri) in links, f'Missing source link: {record["id"]}'
        page = reader.get_destination_page_number(destinations[f'cite.0@{record["id"]}'])
        nearby = '\n'.join(without_furniture(p.extract_text()) for p in reader.pages[page:page + 2])
        assert normalized(record['title']) in normalized(nearby), \
            f'Bibliography title missing: {record["id"]}'

    outline = list(outline_entries(reader.outline))
    headings += ['References']
    assert [str(entry.title) for entry in outline] == headings, 'Section bookmarks differ'
    assert reader.get_destination_page_number(outline[0]) == 1
    assert reader.get_destination_page_number(outline[-1]) == bibliography_page
    assert [reader.get_destination_page_number(entry) for entry in outline] == \
        [1, 2, 4, 5, 6, 8, 9, 10], 'A section no longer starts on its intended page'
    for entry in outline:
        assert float(entry['/Top']) > 740, f'Section starts too far down the page: {entry.title}'

    pull_quotes = {
        5: 'The institution can afford the delay while the useful work remains undone.',
        6: 'A unit that must seek fresh agreement across departments for every meaningful action has responsibility without control.',
        9: 'We cannot keep paying capable people to wait and expect abundance to emerge from the queue.',
    }
    for number, quote in pull_quotes.items():
        display = []
        def collect_quote(text, cm, tm, font, size):
            if 21 < size < 23:
                display.append(text)
        reader.pages[number].extract_text(visitor_text=collect_quote)
        assert normalized(quote) in normalized(''.join(display)), \
            f'Pull quote missing or no longer prominent on page {number + 1}'
        assert normalized(quote) in normalized(manuscript), 'Pull quote is not verbatim essay text'

    for number, details in {
        1: ['Where the working week goes', '44%', '37%', '18%', '76%', '85%',
            '300 respondents', 'Self-reported time allocation'],
        2: ['Four partial answers', 'Finance', 'Manufacturing', 'Planning', 'Marketing',
            'Who owns the combined result?', 'product-portfolio example'],
        3: ['Make the whole outcome operable', 'Enterprise mandate', 'Information',
            'Authority', 'Execution and feedback', 'complete outcome'],
        4: ['The path to intervention', 'AUTHORITY AS A QUEUE', 'AUTHORITY WITHIN AGREED LIMITS',
            'Stop, contain', 'Verification and independent scrutiny'],
    }.items():
        anchors = [destination for key, destination in destinations.items()
                   if key.startswith('figure.') and f'Figure {number}:' in
                   reader.pages[reader.get_destination_page_number(destination)].extract_text()]
        assert len(anchors) == 1, f'Figure {number} has no unique caption destination'
        page = reader.get_destination_page_number(anchors[0])
        assert page == {1: 2, 2: 3, 3: 7, 4: 8}[number], \
            f'Figure {number} has drifted away from its discussion'
        text = normalized(reader.pages[page].extract_text())
        assert 0 < page < bibliography_page
        for detail in details:
            assert normalized(detail) in text, f'Figure {number} label/caption missing: {detail}'

    log = Path('build/squeezed/build' if 'squeezed' in Path(path).stem else 'build') / f'{NAME}.log'
    assert not re.search(r'Overfull \\[hv]box|Citation .+ undefined|There were undefined|Please rerun',
                         log.read_text()), 'Unresolved typesetting or citation warnings'
    print(f'{path}: {len(reader.pages)} A4 pages; {len(paragraphs)} manuscript blocks; '
          f'{len(cited)} references and linked citations; cover abstract, original artwork, '
          'three editorial illustrations, four native figures, three pull quotes, '
          'unbroken paragraphs, page numbering and all section bookmarks verified')


if __name__ == '__main__':
    for pdf in (f'{NAME}.pdf', f'{NAME}-squeezed.pdf'):
        verify(pdf)
