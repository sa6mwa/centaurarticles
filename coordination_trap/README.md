# The Coordination Trap

Michel Blomgren · C89 Systems · <mike@c89.systems>

An eight-page research essay about the organizational cost of absorbing new AI
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

Edit `coordination-trap.md` for prose and `references.bib` for the 13 bibliography
records. Pandoc and `manuscript.lua` regenerate `abstract.tex` and `body.tex`;
both fragments are committed for inspection. The four files under `draft/`
remain the original inputs. Their historical source-status note is superseded
by this edition's `source-notes.md`.

## Layout

The typography and geometry follow `no_place_to_land/`: A4, 11-point XCharter
body text, Helvetica section headings, Montserrat cover lettering, 7 mm between
columns, C89 footer and page numbering. The cover carries the complete abstract,
the author and the C89 Systems vector logo. The essay begins on page 2 and flows
in two columns; there is no contents page. The last body page balances its
columns, followed by a single-column bibliography. Section bookmarks and native
author–year citation links provide navigation.

`coordination-trap.tex` owns cover composition, metadata and column layout;
`structure.tex` retains the companion essay's typography and bibliography
configuration. `body-illustrations.tex` contains two original native drawings:
the Hastings survey chart and the proposed arrangement for outcome ownership.
The chart uses the published percentages without normalization. The proposal
figure is identified as the essay's recommendation.

The only imported image assets are the four unchanged C89 logo and logomark
SVGs in `assets/`. `cover.png` is newly generated for this essay. No cover or body
illustration from another essay is reused. `illustrations/provenance.json`
records the assets and their provenance. SVG conversion preserves vector logos;
both body figures and all labels remain vector/text in the PDFs.

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
pdfLaTeX/BibTeX with the companion essay's TeX packages (plus `balance`), Pandoc,
`rsvg-convert`, Poppler, Python 3, Pillow and pypdf.

`make SQUEEZED_DPI=150` changes the placement-aware image target from the default
200 DPI. Staging never enlarges an image. The present 1024 × 1536 cover is already
below that default at its full-page placement, so both PDF variants are about
2.44 MB; the distribution path is still built and verified independently.

`make check` runs 18 unit/integration tests, checks equality between the PDF
variants, and verifies every manuscript paragraph in order, the complete cover
abstract, artwork identity, unchanged C89 assets, figure captions and labels, all references and
citation destinations, source URLs, section bookmarks, A4 dimensions, page
numbers, two-column body layout, and the absence of unresolved citations or overfull boxes. Generated
PDFs are also rendered and reviewed visually during editorial production.

`make release` first runs the checks, then packages both PDFs and all buildable
sources in `coordination-trap.zip`. Research drafts remain in the repository;
they are not build inputs. `make clean` removes build output, PDFs, converted
logos and generated TeX fragments; the next build recreates them. Generated
PDFs, converted logos, archives and temporary build files are ignored by Git.

The inherited `structure.tex` keeps the Wenneker template attribution and its
license notice. The manuscript and newly created assets follow the repository's
licensing terms.
