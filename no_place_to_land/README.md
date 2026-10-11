# No Place To Land

Author: Michel Blomgren, <mike@c89.systems>.

This is the initial LaTeX layout, derived from the `10x/` article template:
XCharter body text, sans-serif headings, A4 pages, and a two-column essay body.
The cover has new blue-on-black synthwave artwork, the C89 Systems vector logo,
and the complete manuscript abstract. A single-column chapter contents page
precedes the essay. PDF bookmarks also include its subsections.

## Manuscript and layout

`no-place-to-land.md` is the local manuscript snapshot from
`../../c89.systems/docs/no_place_to_land/no-place-to-land-manuscript-v0.5.md`.
The prose is preserved. The displayed title is **No Place To Land**, publication
metadata identifies C89 Systems and the author, and links to 10x use
`https://c89.systems/10x.pdf`. The contents page also offers
`https://c89.systems/10x.md`; these are intentional future publication URLs.

The original v0.5 manuscript's SHA-256 at import was
`e9ebd71cab9b8f1a928afa5e6a466e588f2dff37926640312c15dfa2dac24144`.

Edit the local Markdown for manuscript changes. `make` regenerates `abstract.tex`
and `body.tex` with Pandoc and `manuscript.lua`. Edit `no-place-to-land.tex` for
cover composition, branding, contents, and the cover fade settings; edit
`structure.tex` for typography and page geometry. The generated TeX fragments
are committed so the essay's typeset source is inspectable.

The four original SVG branding assets are copied into `assets/`. The build
converts them to vector PDFs without modifying the source SVGs. The white logo
appears on the dark cover; the black logo appears on the white contents page.
Both requested logomark variants are also available for later layout work.

## Build

Run `make` in this directory to produce `no-place-to-land.pdf` and
`no-place-to-land-squeezed.pdf`, with build copies under `build/`.
The Makefile, convergence script, image squeezing, and PDF comparison workflow
follow `10x/`. SVG conversion and manuscript-fragment generation are added;
the inline research links require no BibTeX bibliography.

Dependencies: pdfLaTeX with the packages used by 10x, Pandoc, `rsvg-convert`,
Poppler (`pdfimages`, `pdftoppm`), and Python 3 with Pillow and pypdf.

`make SQUEEZED_DPI=150` changes the image target (default 200 DPI). Vector logos,
native text, and links remain unchanged. `make check` runs the image-staging
tests, compares both PDFs, and checks manuscript coverage, front-page abstract,
author metadata, chapter navigation, and publication links. `make release`
packages both PDFs and their buildable sources in `no-place-to-land.zip`.
`make clean` removes generated output, including the TeX fragments; the next
build recreates them.

Cover generation provenance and the complete prompt are in `cover-art.md`.
