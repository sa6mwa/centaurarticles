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
- [Active cover composition and prompt](illustrations/cover-v3-art.md)
- [Body illustration prompts](illustrations/body-art.md)

Edit `coordination-trap.md` for prose and `references.bib` for the 12 bibliography
records. Pandoc and `manuscript.lua` regenerate `abstract.tex` and `body.tex`;
both fragments are committed for inspection. The four files under `draft/`
remain the original inputs. Their historical source-status note is superseded
by this edition's `source-notes.md`.

## Layout

The typography and geometry follow `no_place_to_land/`: A4, 11-point XCharter
body text, Helvetica section headings, 7 mm between columns, C89 footer and page
numbering. The cover follows the author's supplied sunset-and-office-tower
reference. Condensed Bebas Neue lettering sits in the open sky, with a coral-red
“TRAP” and the short cover line “When execution outruns the enterprise.” The C89
logo and author details occupy the top; a 51-word abstract sits in the dimmed
lower portion of the full-page image. The introduction uses normal black,
two-column body text, followed by an illustration and clear separation from the first section.
There is no contents page. A single-column bibliography follows the essay.
Section bookmarks and native author–year citation links provide navigation.

`coordination-trap.tex` owns cover composition and metadata;
`structure.tex` retains the companion essay's typography and bibliography
configuration. `editorial-layout.tex` supplies paragraph-safe column pairs,
a gutter inset and illustration bands. The editorial map in
`manuscript.lua` starts each major section on a fresh page and gives the evidence
and outcome-ownership sections deliberate continuation pages. It fails with an
actionable error if section order or paragraph counts change, so structural
edits require a layout review. Changes within paragraphs also need a fresh render.

One short pull quote, “The mandate must move real decisions,” sits horizontally
across the gutter in the ownership section. Matching `wrapstuff` windows narrow
the facing edges of both columns, and the prose returns to normal width above
and below it. The quote uses upright serif type with quiet quotation marks.
`body-illustrations.tex` contains four
original native drawings: the Hastings survey, the product-portfolio decision,
the proposed arrangement for outcome ownership, and the safety-control sequence.
The survey uses the published percentages without normalization. The proposal
diagrams carry no invented measurements.

The four unchanged C89 logo and logomark SVGs in `assets/` are the only imagery
carried over from another essay. `cover-v3.png` is an imagegen edit of the author's
reference, preserved in `illustrations/cover-reference.png`. The original navy
`cover.png` remains as an unused source asset. All three body illustrations were
generated for this essay.
The opening illustration, a three-panel comic and the closing workshop scene
are conceptual editorial artwork. No cover or body
illustration from another essay is reused. `illustrations/provenance.json`
records the assets and their provenance. SVG conversion preserves vector logos;
all four analytical figures and their labels remain vector/text in the PDFs.
`cover-type.svg` supplies editable cover lettering. The bundled Bebas Neue font
and its SIL Open Font License live in `assets/fonts/`; a project-local Fontconfig
configuration selects that font during conversion without a system installation.
The cover title and cover line remain selectable, embedded text in both PDFs.

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
pdfLaTeX/BibTeX with the companion essay's TeX packages plus `wrapstuff`, Pandoc,
`rsvg-convert`, Poppler, Python 3, Pillow and pypdf.

`make SQUEEZED_DPI=150` changes the placement-aware image target from the default
200 DPI. Staging never enlarges an image. The full PDF is approximately 11.26 MB;
the distribution PDF is approximately 9.23 MB. Text, vector artwork, links and
pagination are identical, with the raster illustrations resized for distribution.

`make check` runs 28 unit/integration tests, checks equality between the PDF
variants, and verifies every manuscript paragraph in order, the complete cover
abstract, artwork identity, unchanged C89 assets, figure captions and labels,
all references and citation destinations, source URLs, embedded cover font, section bookmarks,
A4 dimensions, page numbers, two-column body layout, the single verbatim gutter
quote and the absence of unresolved citations or overfull boxes. The PDF check
also checks that the background fills the cover, prose wraps on both sides of
the inset quote and returns to normal width, every prose paragraph stays within
one page and one column or full-width band, and figures remain with their intended discussion. Generated
PDFs are also rendered and reviewed visually during editorial production.

`make release` first runs the checks, then packages both PDFs and all buildable
sources in `coordination-trap.zip`. Research drafts remain in the repository;
they are not build inputs. `make clean` removes build output, PDFs, converted
logos and generated TeX fragments; the next build recreates them. Generated
PDFs, converted logos and cover lettering, archives and temporary build files are ignored by Git.

The inherited `structure.tex` keeps the Wenneker template attribution and its
license notice. The manuscript and newly created assets follow the repository's
licensing terms. The bundled third-party font retains its accompanying OFL license.
