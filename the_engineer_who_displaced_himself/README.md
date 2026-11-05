# The Engineer Who Displaced Himself

An illustrated essay by Michel Blomgren, retaining the AI narrator of the supplied drafts.

`manuscript.tex` is the canonical combined manuscript. `the-engineer-who-displaced-himself.tex`
assembles the document; `cover.tex` places the cover typography and vector accents;
`notes.tex` records sources and links.
The original two Markdown drafts and `context.md` remain intact as editorial sources.

The opening retains the first draft's moment of recognition while bringing the interview
preparation and simultaneous agent work into the scene. The revised draft contributes its
stronger treatment of credentials, employment and the closing decision. The added C89
comparison establishes that the professional choice preceded the interview.

The cover background is regenerated from the supplied cinematic mockup, with its
lettering removed. LaTeX recreates the title, subtitle, author, contact links and orange
accents using embedded Anton and Barlow fonts; licenses are included under `fonts/`.
The composition is adapted to A4, with no film imagery or company branding.
Only the author's name, email and website accompany the title and story line. The interior
comic is conceptual, not a documentary reconstruction or likeness. No contents page or
abstract interrupts the opening. The XCharter body type, Helvetica headings, A4 geometry
and page furniture follow the companion essays. The inherited template license remains
in `structure.tex`. Image-generation prompts and provenance are in `illustrations/artwork.md`.

## Build and verification

Requires Tectonic, Make and Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`).
Tectonic downloads its TeX packages into the repository-local ignored `build/cache`.

```sh
make
make check
make render
```

For an engine outside PATH, set `TECTONIC=/absolute/path/to/tectonic` on the Make command.
The build is serialized. The PDF is produced both at the essay root and under `build/`.
PDFs and intermediate output are ignored by Git. `make clean` removes generated output
and the local package cache. Rendered pages under `build/render/` support visual inspection.

`make check` checks that the PDF can be read, extracts its text, and rejects overfull
boxes, missing glyphs, font substitutions and unresolved references in the TeX log.
Visual inspection is necessary for spacing, image placement and cover contrast.
Short sections mark the narrative turns. Both pull quotes sit in the gutter, with
black italic text and one oversized orange opening mark in a contrasting serif.
The cutouts share upper and lower boundaries, with 2.25mm clearance beside the
opening mark and 4.5mm on the right. Quotes are vertically centred; header blocks align to the
body baseline grid so both columns enter and leave the cutout on the same row.
`editorial-layout.tex` uses native TeX paragraph shapes and paragraph hooks, retaining
the companion essay's composition without requiring a newer TeX bundle.
The Coordination Shift passage includes a linked reproduction of the earlier essay cover, tilted as a paper inset.
Nine additional editorial illustrations follow the story from the narrow
assessment frame through the working system, the choice and its cost, to the
unfinished frontier. Body pages contain two images each, with three on the
closing page; references remain unillustrated. The opening page separates its
small illustration at the head of column two from the panorama below the text.
Contemporary cinematic artwork uses cool shadows, selective orange light and
substantial compact mechanical keyboards. The updated comic retains its
three-part story; the approved closing landscape is retained unchanged.
The closing panorama is cropped in LaTeX; its full source is retained.
The built-in image-generation prompts are recorded in
`illustrations/art-direction.md`, beside the source PNGs.
`notes.tex` contains the references and concise engineering descriptions of the projects.
Product links point to repository roots (or the Vectis product page).
