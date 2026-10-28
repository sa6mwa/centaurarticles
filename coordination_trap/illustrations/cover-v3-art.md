# Cover composition

The cover follows the author's supplied reference, preserved as `cover-reference.png`.
The active background, `../cover-v3.png`, was generated on 2026-10-28 with the
built-in imagegen tool by editing that reference. Its original lettering was
removed, the open sky retained, and headroom reserved for the publisher and author.
The image is conceptual editorial artwork, not a photograph of a real company.

## Typography and placement

- Full-page sunset and city on the left; occupied office tower on the right.
- Unchanged C89 Systems logo at the upper left; author and linked email at the upper right.
- Warm-white condensed “THE / COORDINATION” and coral-red “TRAP” in the open sky.
- Short cover line: “WHEN EXECUTION / OUTRUNS / THE ENTERPRISE”.
- The complete 51-word abstract sits over a translucent fade at the bottom.

`../cover-type.svg` holds the title and cover line as editable text.
`../assets/fontconfig.conf` selects the bundled Bebas Neue font without installing
anything into the host's font directories. The existing rsvg-convert build step
embeds it as searchable TrueType text in `../assets/cover-type.pdf`.
The other cover text is set directly in LaTeX. The source archive includes the
font, its SIL Open Font License, the SVG, the background and this reference.

Bebas Neue by Ryoichi Tsunekawa, downloaded from the official
[Google Fonts repository](https://github.com/google/fonts/tree/main/ofl/bebasneue).
The exact downloaded font and license hashes are recorded in `provenance.json`.
The original, unused navy background remains as `../cover.png`, documented by
`../cover-art.md`; it is not used in the final cover.

## Exact image edit prompt

Use case: compositing
Asset type: full-bleed portrait essay cover BACKGROUND, based on the supplied cover reference.
Edit this supplied image. Retain its compelling composition: warm red-orange sunset and river city filling the left half; a dramatic transparent office tower rising along the right, with visible people in meetings, stacked glass rooms, stairs and warm interior lights. Preserve the sun, the city depth, the detailed architectural realism and the restrained, sophisticated cinematic atmosphere.
Remove ALL existing text and lettering from the image, cleanly reconstructing the sky behind it. We will typeset the cover separately.
Make space for a publisher logo and author details at the very top: extend the scene upward slightly and make the uppermost 10 percent a quiet dark navy-plum sky and dim upper building floors. This must look like a continuous full-page photograph, not a solid rectangular header or added band.
Reserve an uninterrupted open-sky area on the LEFT, approximately x=5–51 percent and y=15–47 percent, for a tall condensed three-line title and a short cover line. In that area preserve beautiful subdued violet/red clouds but avoid any building projections, bright lights or high contrast cloud edges. The office tower should begin on the RIGHT around x=55 percent in the upper half, and can step outward to x=44 percent below the title area. Keep the original skyscraper-on-right / open-sky-on-left composition.
Keep rich architecture and sunset detail through the middle. The lowest 17 percent should fall into natural deep shadow so a short white abstract will be legible across the page. No abrupt fade boundaries or opaque panels.
No typography, letters, logos, watermark or drawn frames. Portrait 2:3. Preserve the overall visual character of the supplied reference rather than substituting a different architectural scene.
