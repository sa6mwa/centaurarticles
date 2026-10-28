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
- [Revised comic and closing illustration prompts](illustrations/body-art-v2.md)
- [Opening illustration and original body artwork prompts](illustrations/body-art.md)

Edit `coordination-trap.md` for prose and `references.bib` for the 12 bibliography
records. Pandoc and `manuscript.lua` regenerate `abstract.tex` and `body.tex`;
both fragments are committed for inspection. The four files under `draft/`
remain the original inputs. Their historical source-status note is superseded
by this edition's `source-notes.md`.

## Layout

The typography and geometry follow `no_place_to_land/`: A4, 11-point XCharter
body text, uppercase Helvetica section headings, 7 mm between columns, C89 footer and page
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
gutter insets and illustration bands. The editorial map in
`manuscript.lua` starts each major section on a fresh page and gives the evidence
and outcome-ownership sections deliberate page breaks. Those pages resume the
two-column text without added continuation headers. Every prose paragraph stays
in the column flow. The map fails with an
actionable error if section order or paragraph counts change, so structural
edits require a layout review. Changes within paragraphs also need a fresh render.

Three pull quotes emphasize the cost of delay, responsibility without control,
and paying capable people to wait. Each sits horizontally across the gutter.
Matching `wrapstuff` windows measure the actual lettering, with 4.5 mm side
clearance and 1.5 mm vertical separation. Prose returns to normal width above
and below each quote. The quotes use upright 17-point serif type with quiet quotation marks.
The narrow reflow pass retains a 1em emergency-spacing allowance; the installed
`wrapstuff` otherwise disables it and can let words overrun the column. A guarded
local adapter enables that fallback, and PDF geometry checks enforce both the
reserved quote space and the outer column edges, allowing only optical protrusion.
`body-illustrations.tex` contains four
original native drawings: the Hastings survey, the product-portfolio decision,
the proposed arrangement for outcome ownership, and the safety-control sequence.
The survey uses one full-week bar on a 0–100% scale, with the published 44%, 37%
and 18% shares preserved without normalization. A bracket makes the combined
55% for coordination and administration explicit while keeping both categories
distinct. The final 1% remains unfilled because of rounding in the reported
shares. Work preferences appear separately below the bar as large 18-point
76% and 85% callouts, with their labels underneath. The proposal diagrams
carry no invented measurements.

The four unchanged C89 logo and logomark SVGs in `assets/` are the only imagery
carried over from another essay. `cover-v3.png` is an imagegen edit of the author's
reference, preserved in `illustrations/cover-reference.png`. The original navy
`cover.png` remains as an unused source asset. All three body illustrations were
generated for this essay.
The opening illustration, a three-panel comic and the closing bridge diptych
are conceptual editorial artwork. The revised comic contrasts disconnected
departmental contributions with a human–AI unit completing a working service
for its user. Its short dialogue belongs inside the panels. The wordless
closing diptych shows the same completed bridge blocked by approvals, then open
to use. Neither image relies on an explanatory caption. The earlier pump comic
and workshop closing scene remain as unused source assets. No cover or body
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
200 DPI. Staging never enlarges an image. The full PDF is approximately 11.50 MB;
the distribution PDF is approximately 9.43 MB. Text, vector artwork, links and
pagination are identical, with the raster illustrations resized for distribution.

`make check` runs 32 unit/integration tests, checks equality between the PDF
variants, and verifies every manuscript paragraph in order, the complete cover
abstract, artwork identity, unchanged C89 assets, figure captions and labels,
the survey's full-week scale and 18-point work-preference callouts,
all references and citation destinations, source URLs, embedded cover font, section bookmarks,
A4 dimensions, page numbers, strictly two-column body prose, uppercase headings,
three verbatim gutter quotes and the absence of unresolved citations or overfull boxes. The PDF check
also checks that the background fills the cover, prose wraps on both sides of
each inset quote and returns to normal width, every prose paragraph stays within
one page and one column, and figures and artwork remain with their intended discussion. Generated
PDFs are also rendered and reviewed visually during editorial production.

`make release` first runs the checks, then packages both PDFs and all buildable
sources in `coordination-trap.zip`. Research drafts remain in the repository;
they are not build inputs. `make clean` removes build output, PDFs, converted
logos and generated TeX fragments; the next build recreates them. Generated
PDFs, converted logos and cover lettering, archives and temporary build files are ignored by Git.

The inherited `structure.tex` keeps the Wenneker template attribution and its
license notice. The manuscript and newly created assets follow the repository's
licensing terms. The bundled third-party font retains its accompanying OFL license.
