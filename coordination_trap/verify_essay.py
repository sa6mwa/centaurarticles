#!/usr/bin/env python3
"""Check manuscript coverage, cover, citations, figures and PDF navigation."""

import json
from pathlib import Path
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
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
    """Every paragraph must occupy one page and one column.

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


def verify_background_extent(matrix, width, height):
    a, b, c, d, e, f = matrix
    points = [(e, f), (a + e, b + f), (c + e, d + f), (a + c + e, b + d + f)]
    assert min(x for x, _ in points) <= 0.5 and min(y for _, y in points) <= 0.5 \
        and max(x for x, _ in points) >= width - 0.5 \
        and max(y for _, y in points) >= height - 0.5, 'Cover background is not full-page'


def verify_gutter_geometry(quote, words, page_width, quote_rows=None):
    left, top, right, bottom = quote
    assert abs((left + right) / 2 - page_width / 2) < 12, 'Quote is not centered on the gutter'
    beside = [w for w in words if top < (w[1] + w[3]) / 2 < bottom]
    assert any(w[2] < left - 4 for w in beside), 'No prose flows to the left of the quote'
    assert any(w[0] > right + 4 for w in beside), 'No prose flows to the right of the quote'
    # Centered quote lines have different lengths. Check the actual ink on each
    # line so a longer line cannot create a false collision beside a shorter one.
    for row_left, row_top, row_right, row_bottom in quote_rows or [quote]:
        adjacent = [w for w in words if w[1] < row_bottom and w[3] > row_top]
        assert all(w[2] < row_left - 4 or w[0] > row_right + 4 for w in adjacent), \
            'Prose overlaps the quote'
    for start, stop in [(top - 80, top - 30), (bottom + 30, bottom + 80)]:
        nearby = [w for w in words if start < (w[1] + w[3]) / 2 < stop]
        assert any(left < (w[0] + w[2]) / 2 < page_width / 2 for w in nearby) \
            and any(page_width / 2 < (w[0] + w[2]) / 2 < right for w in nearby), \
            'Both columns must regain their normal width above and below the quote'


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
    image_source = Path('build/squeezed/cover-v3.png' if 'squeezed' in Path(path).stem
                        else 'cover-v3.png')
    with Image.open(image_source) as source:
        assert pixel_key(reader.pages[0].images[0].image) == pixel_key(source), \
            'Wrong cover artwork embedded'
    image_placements = []
    def cover_image_operator(operator, operands, cm, tm):
        if operator == b'Do':
            resource = reader.pages[0]['/Resources']['/XObject'].get(operands[0])
            if resource and resource.get_object().get('/Subtype') == '/Image':
                image_placements.append(cm)
    reader.pages[0].extract_text(visitor_operand_before=cover_image_operator)
    assert len(image_placements) == 1
    verify_background_extent(image_placements[0], float(reader.pages[0].mediabox.width),
                             float(reader.pages[0].mediabox.height))
    assert 'AI is changing what people can accomplish' not in cover, 'Long cover subtitle reappeared'
    assert normalized('When execution outruns the enterprise') in normalized(cover), \
        'Short cover line missing or no longer selectable'
    fonts = subprocess.check_output(['pdffonts', '-f', '1', '-l', '1', str(path)], text=True)
    assert re.search(r'BebasNeue-Regular\s+TrueType\s+\S+\s+yes\s+yes\s+yes', fonts), \
        'The bundled cover font must be embedded with Unicode text mapping'
    body_art = {1: 'opening-illustration.png', 4: 'unit-comic-v2.png',
                9: 'closing-illustration-v2.png'}
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
    paragraphs = [p for p in manuscript.split('\n\n') if p.strip()]

    records = bibliography_records()
    cited = set(re.findall(r'\[@([\w-]+)\]', Path(f'{NAME}.md').read_text()))
    assert cited == {r['id'] for r in records}, 'Missing or uncited bibliography entries'
    assert {'hastings2026deployment', 'slok2026payoff'} <= cited
    destinations = reader.named_destinations
    for key in cited:
        assert f'cite.0@{key}' in destinations, f'Citation destination missing: {key}'
    bibliography_page = min(reader.get_destination_page_number(destinations[f'cite.0@{key}'])
                            for key in cited)
    assert 'REFERENCES' in reader.pages[bibliography_page].extract_text()
    assert bibliography_page > 1, 'Bibliography must follow the essay'
    headings = [h for h in re.findall(r'^## (.+)$', Path(f'{NAME}.md').read_text(), re.M)
                if h != 'Abstract']
    prose_paragraphs = [p for p in paragraphs if p.strip() not in headings]
    runs = []
    for number in range(1, bibliography_page):
        def collect_body(text, cm, tm, font, size):
            x, y = tm[4] + cm[4], tm[5] + cm[5]
            if 10.5 < size < 11.5 and 55 < y < 775:
                content = normalized(text)
                if content:
                    runs.append((content, number, 'right' if x > 295 else 'left'))
        reader.pages[number].extract_text(visitor_text=collect_body)
    verify_paragraph_flow(prose_paragraphs, runs)
    links = set()
    linked_citations = set()
    introduction_links = set()
    introduction_citations = set()
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
                    allowed = {'https://c89.systems'}
                    if number == 1:
                        allowed.add('https://c89.systems/10x.pdf')
                        introduction_links.add(uri)
                    assert uri in allowed, 'Unexpected external link in body prose'
            if action.get('/S') == '/GoTo' and number < bibliography_page:
                linked_citations.add(str(action.get('/D')))
                if number == 1:
                    introduction_citations.add(str(action.get('/D')))
    assert 'https://c89.systems/10x.pdf' in introduction_links, \
        'Introduction must link directly to The Coordination Shift PDF'
    assert 'cite.0@blomgren2025coordination' in introduction_citations, \
        'Introduction must retain its Coordination Shift bibliography link'
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
        heading_page = reader.get_destination_page_number(entry)
        assert str(entry.title).upper() in ' '.join(reader.pages[heading_page].extract_text().split()), \
            f'Section heading is not uppercase: {entry.title}'
    assert '/ CONTINUED' not in '\n'.join(p.extract_text().upper() for p in reader.pages), \
        'An invented continuation header reappeared'

    quote_lines = {
        5: ['The institution can afford', 'the delay while the useful', 'work remains undone.'],
        6: ['A unit that must seek fresh', 'agreement across departments',
            'for every meaningful action has', 'responsibility without control.'],
        9: ['We cannot keep paying', 'capable people to wait',
            'and expect abundance', 'to emerge from the queue.'],
    }
    display = {number: [] for number in quote_lines}
    for number in range(1, bibliography_page):
        def collect_quote(text, cm, tm, font, size):
            if text.strip() and 16.5 < size < 17.5:
                assert number in quote_lines, 'An additional display quote appeared'
                display[number].append(text)
        reader.pages[number].extract_text(visitor_text=collect_quote)
    bbox = ET.fromstring(subprocess.check_output(['pdftotext', '-bbox-layout', str(path), '-']))
    ns = {'x': 'http://www.w3.org/1999/xhtml'}
    def bounds(element):
        return tuple(float(element.get(key)) for key in ('xMin', 'yMin', 'xMax', 'yMax'))
    for number, lines in quote_lines.items():
        quote = ' '.join(lines)
        assert normalized(quote) == normalized(''.join(display[number])), \
            f'Missing or changed pull quote on page {number + 1}'
        assert normalized(quote) in normalized(manuscript), 'Pull quote is not verbatim essay text'
        page = bbox.findall('.//x:page', ns)[number]
        quote_words = []
        quote_rows = []
        matched_lines = []
        for line in page.findall('.//x:line', ns):
            # Poppler can merge adjacent prose into the same geometric line.
            # Isolate the larger quote glyphs before checking their wording.
            words = [word for word in line.findall('x:word', ns)
                     if 13 < bounds(word)[3] - bounds(word)[1] < 15.5]
            content = normalized(''.join(w.text or '' for w in words))
            if content in {normalized(expected) for expected in lines}:
                quote_words.extend(words)
                matched_lines.append(content)
                quote_rows.append((min(bounds(w)[0] for w in words), min(bounds(w)[1] for w in words),
                                   max(bounds(w)[2] for w in words), max(bounds(w)[3] for w in words)))
        assert matched_lines == [normalized(line) for line in lines], \
            f'Quote line breaks changed on page {number + 1}'
        rectangles = [bounds(w) for w in quote_words]
        quote_bounds = (min(w[0] for w in rectangles), min(w[1] for w in rectangles),
                        max(w[2] for w in rectangles), max(w[3] for w in rectangles))
        body_words = [bounds(w) for w in page.findall('.//x:word', ns) if w not in quote_words]
        verify_gutter_geometry(quote_bounds, body_words,
                               float(reader.pages[number].mediabox.width), quote_rows)

    assert normalized('One human–AI unit owns the outcome across all three stages') \
        not in normalized(reader.pages[4].extract_text()), 'Removed comic caption reappeared'
    preferences = []
    def collect_preferences(text, cm, tm, font, size):
        if text.strip() and 17.5 < size < 18.5:
            preferences.append(text)
    reader.pages[2].extract_text(visitor_text=collect_preferences)
    assert normalized(''.join(preferences)) == normalized('76% 85%'), \
        'The two preference percentages must remain prominent 18-point callouts'

    for number, details in {
        1: ['Where the working week goes', '44%', '37%', '18%', '55%', '76%', '85%',
            '0%', '50%', '100%', '55% coordination + administration', 'Desired change',
            'Substantive work', 'Coordination', 'Administration',
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
          'three editorial illustrations, full-week survey chart with large preference callouts, four native figures, '
          'three quotes with prose wrapping on both sides, '
          'uppercase headings, unbroken paragraphs, page numbering and all section bookmarks verified')


if __name__ == '__main__':
    for pdf in (f'{NAME}.pdf', f'{NAME}-squeezed.pdf'):
        verify(pdf)
