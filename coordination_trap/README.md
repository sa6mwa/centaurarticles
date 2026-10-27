# The Coordination Trap

Michel Blomgren · C89 Systems · <mike@c89.systems>

An eleven-page illustrated research essay about the organizational cost of absorbing new AI
capability into an unchanged division of work. The manuscript combines the
supplied drafts, with the Hastings–Syverson–Zimmerman survey and Torsten Slok's
original Apollo note as its organizing sources. It retains the first-person,
pressing tone and develops a practical argument about outcome ownership,
decision authority, incentives and timely safety control.

## Read and edit

- [Full PDF](coordination-trap.pdf)
- [Distribution PDF](coordination-trap-squeezed.pdf)
- [Manuscript](coordination-trap.md)
- [Source verification and editorial decisions](source-notes.md)
- [Cover prompt and provenance](cover-art.md)
- [Body illustration prompts](illustrations/body-art.md)

Edit `coordination-trap.md` for prose and `references.bib` for the 12 bibliography
records. Pandoc and `manuscript.lua` regenerate `abstract.tex` and `body.tex`;
both fragments are committed for inspection. The four files under `draft/`
remain the original inputs. Their historical source-status note is superseded
by this edition's `source-notes.md`.

## Layout

The typography and geometry follow `no_place_to_land/`: A4, 11-point XCharter
body text, Helvetica section headings, Montserrat cover lettering, 7 mm between
columns, C89 footer and page numbering. The redesigned cover uses a large
headline, a 16-point subtitle, a reframed architectural image and a 51-word
abstract. The introduction has its own illustrated page with a larger opening
paragraph. There is no contents page. A single-column bibliography follows the
essay. Section bookmarks and native author–year citation links provide navigation.

`coordination-trap.tex` owns cover composition and metadata;
`structure.tex` retains the companion essay's typography and bibliography
configuration. `editorial-layout.tex` supplies paragraph-safe column pairs,
full-width pull quotes and illustration bands. The editorial map in
`manuscript.lua` starts each major section on a fresh page and gives the evidence
and outcome-ownership sections deliberate continuation pages. It fails with an
actionable error if section order or paragraph counts change, so structural
edits require a layout review. Changes within paragraphs also need a fresh render.

Three pull quotes reproduce the author's words, including the central challenge
about responsibility without control. `body-illustrations.tex` contains four
original native drawings: the Hastings survey, the product-portfolio decision,
the proposed arrangement for outcome ownership, and the safety-control sequence.
The survey uses the published percentages without normalization. The proposal
diagrams carry no invented measurements.

The only imported image assets are the four unchanged C89 logo and logomark
SVGs in `assets/`. `cover.png` and the three body illustrations were generated
for this essay. The cover's underlying pixels are unchanged by this revision.
The opening illustration, a three-panel comic and the closing workshop scene
are conceptual editorial artwork. No cover or body
illustration from another essay is reused. `illustrations/provenance.json`
records the assets and their provenance. SVG conversion preserves vector logos;
all four analytical figures and their labels remain vector/text in the PDFs.

## Build and verify

Run these commands in this directory:

```sh
make
make check
make release
```

`make` produces both PDFs here and under `build/`, using the same pdfLaTeX,
BibTeX convergence, PNG staging and PDF comparison process as `no_place_to_land/`.
The build is serialized even when `make -j` is requested. Dependencies are
pdfLaTeX/BibTeX with the companion essay's TeX packages, Pandoc,
`rsvg-convert`, Poppler, Python 3, Pillow and pypdf.

`make SQUEEZED_DPI=150` changes the placement-aware image target from the default
200 DPI. Staging never enlarges an image. The full PDF is approximately 11.23 MB;
the distribution PDF is approximately 9.20 MB. Text, vector artwork, links and
pagination are identical, with the raster illustrations resized for distribution.

`make check` runs 23 unit/integration tests, checks equality between the PDF
variants, and verifies every manuscript paragraph in order, the complete cover
abstract, artwork identity, unchanged C89 assets, figure captions and labels,
all references and citation destinations, source URLs, section bookmarks,
A4 dimensions, page numbers, two-column body layout, prominent verbatim pull
quotes and the absence of unresolved citations or overfull boxes. The PDF check
also proves that every prose paragraph stays within one page and one column
or full-width band, and that figures remain with their intended discussion. Generated
PDFs are also rendered and reviewed visually during editorial production.

`make release` first runs the checks, then packages both PDFs and all buildable
sources in `coordination-trap.zip`. Research drafts remain in the repository;
they are not build inputs. `make clean` removes build output, PDFs, converted
logos and generated TeX fragments; the next build recreates them. Generated
PDFs, converted logos, archives and temporary build files are ignored by Git.

The inherited `structure.tex` keeps the Wenneker template attribution and its
license notice. The manuscript and newly created assets follow the repository's
licensing terms.
