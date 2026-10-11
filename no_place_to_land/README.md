# No Place To Land

Author: Michel Blomgren, <mike@c89.systems>.

This is the initial LaTeX layout, derived from the `10x/` article template:
XCharter body text, sans-serif headings, A4 pages, and a two-column essay body.
The cover has new blue-on-black synthwave artwork, the C89 Systems vector logo,
and the complete manuscript abstract. A single-column contents page with dotted
leaders includes the chapters, introduction, conclusion, and references.
Subsections remain available in the PDF bookmarks.
Below the contents, a transparent landscape illustrates sustained use and the
wider capability frontier. The image has a small settlement, a construction
site, open terrain, and strong boundaries designed to remain readable at its
165 mm placement. The legend is native LaTeX text.
The introduction occupies its own page. Each numbered chapter and the
conclusion begins on a fresh page; subsections flow within their chapters.
“When the producer moves ahead” starts in the next column. Chapter text uses
`multicols`, with an explicit `\columnbreak` at that subsection and `\clearpage`
before each major section. The last columns balance before a wide illustration.

Nine numbered body figures add visual pauses across the chapters: six
imagegen scenes (painting, caricature, and diorama), plus native drawings of
measurement questions, quotation-service responsibility, and the versioned
operating blueprint retained through handover. Two figures use a column; seven
span the text width. The factory panorama occupies the bottom of page 5.
The quotation figure states our prediction and cites its research basis;
the images themselves are conceptual illustrations.
The chapter 3 comparison fills the lower part of page 11. A local
`\enlargethispage{\baselineskip}` at the measurement drawing keeps the preceding
economic-outcomes paragraph together on page 10; the prose is unchanged.
The handover blueprint uses three spaced rows in each panel and a Git history
with branch commits and a merge.

## Manuscript and layout

`no-place-to-land.md` is the local manuscript snapshot from
`../../c89.systems/docs/no_place_to_land/no-place-to-land-manuscript-v0.5.md`.
Source links are converted to author-year citations and redundant parenthesized
years after cited titles removed. The quotation example now states an explicit
prediction about customer consequences, supported by Milgrom and Roberts's complementarity
analysis and the P&G experiment on AI-assisted integration of expertise.
`illustrations/caption-evidence.json` records the sources, locators, and inference.
The displayed title is **No Place To Land**, publication metadata identifies C89 Systems and
the author, and the 10x bibliography entry uses
`https://c89.systems/10x.pdf`. The contents page also offers
`https://c89.systems/10x.md`; these are intentional future publication URLs.

The original v0.5 manuscript's SHA-256 at import was
`e9ebd71cab9b8f1a928afa5e6a466e588f2dff37926640312c15dfa2dac24144`.

Edit the local Markdown for manuscript changes. `make` regenerates `abstract.tex`
and `body.tex` with Pandoc and `manuscript.lua`. Edit `no-place-to-land.tex` for
cover composition, branding, contents, and the cover fade settings; edit
`structure.tex` for typography and page geometry. The generated TeX fragments
are committed so the essay's typeset source is inspectable.
Body illustration sizes, drawings, and captions live in `body-illustrations.tex`;
`manuscript.lua` assigns them to stable heading identifiers. All six selected
generated body images are saved beside the main TeX for the existing squeeze workflow.

The four original SVG branding assets are copied into `assets/`. The build
converts them to vector PDFs without modifying the source SVGs. The white logo
appears on the dark cover; the black logo appears on the white contents page.
Both requested logomark variants are also available for later layout work.

## Citations and bibliography

The essay uses the same `biblatex` configuration as 10x:
`backend=bibtex,style=authoryear,natbib=true`. Markdown citations such as
`*The Coordination Shift* [@blomgren2025coordination]` become native
`\citep{blomgren2025coordination}` commands. Source titles and descriptions
remain ordinary text; citations link to the corresponding entries in the
single-column References section, which appears in the contents and bookmarks.
External research URLs and DOIs appear in the bibliography.
The reference list prints complete author lists and retains name prefixes in
author labels, including *von Hippel*.

Edit `references.bib` for bibliographic details. The 47 entries consolidate
alternate URLs for the same work. `bibliography-notes.md` records identity and
version decisions. The build refreshes BibTeX on each PDF rebuild so changes to
author, year, or other record fields cannot leave stale citations behind.

## Build

Run `make` in this directory to produce `no-place-to-land.pdf` and
`no-place-to-land-squeezed.pdf`, with build copies under `build/`.
The Makefile, convergence script, image squeezing, and PDF comparison workflow
follow `10x/`. SVG conversion and manuscript-fragment generation are added.

Dependencies: pdfLaTeX/BibTeX with the packages used by 10x, Pandoc, `rsvg-convert`,
Poppler (`pdfimages`, `pdftoppm`), and Python 3 with Pillow and pypdf.

`make SQUEEZED_DPI=150` changes the image target (default 200 DPI). Vector logos,
native text, and links remain unchanged. `make check` runs the image-staging
tests, compares both PDFs, and checks manuscript coverage, front-page abstract,
author metadata, chapter navigation, all cited bibliography entries, native
citation destinations, source URLs, and publication links. `make release`
packages both PDFs and their buildable sources in `no-place-to-land.zip`.
`make clean` removes generated output, including the TeX fragments; the next
build recreates them.

Cover generation provenance and the complete prompt are in `cover-art.md`.
Contents illustration prompts and concept history are in
`illustrations/concepts.json`; the selected asset is `frontier-landscape-v2.png`.
Body artwork prompts, media, captions, and asset paths are in
`illustrations/body-art.json`. `make check` also verifies all nine captions,
the six raster placements, native drawing text, and the mix of widths.
Superseded body variants are retained in `illustrations/` with their provenance.
