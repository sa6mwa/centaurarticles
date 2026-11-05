# Artwork provenance

The cover background and comic were generated with the built-in ImageGen tool on 5 November 2026.
They are original conceptual artwork, not photographs of the author or the interview.
The cover is rendered photographically; the interior is a three-panel ink-and-watercolour
comic. Neither borrows imagery from the films discussed in the essay. The title and
cover line are LaTeX text, not raster lettering.

## Cover — `cover.png`

The current background is an edit of the author's supplied replacement cover mockup.
All title, subtitle, author and contact lettering and orange editorial ornaments were
removed with the built-in ImageGen tool. The architecture, interview room, engineer,
sunset and futuristic city were retained and reframed to A4. `cover.tex` reconstructs
the lettering as selectable embedded font text, the contact details as live links,
and the orange rules as vectors. Anton and Barlow are included under `fonts/` with
their SIL Open Font Licenses. The previous cover is retained in Git history.

Prompt:

Use case: precise-object-edit. Asset: text-free background plate for a LaTeX essay cover. Input image: the supplied cover mockup is the edit target. Remove ALL overlaid cover typography: title at upper left, orange DISPLACED word, white subtitle, author name, email, website. Also remove all orange graphic design rules, ticks and decorative strokes at the left and bottom, so they can be redrawn precisely in LaTeX. Seamlessly reconstruct the dark concrete and reflective floor underneath. Preserve the scene and its visual identity: vast dark concrete arch curving diagonally from upper right to lower middle, quiet dark upper-left wall for the title, glass interview room with people and desk at lower left, lone engineer seen from behind near the lower middle looking across a luminous sunset, monumental curved futuristic towers with greenery and mist to the right, subtle transparent blue technical diagrams in the right architecture, warm reflected sunlight on the floor. Keep the engineer small and preserve his pose, keep lighting, color, material detail and framing as closely as possible. Adapt to A4 portrait proportions (approximately 1:1.414), widening the composition gently rather than stretching objects or cropping important elements; the upper left remains very dark and quiet, and the bottom strip remains dark for the author line. Preserve the visual positions of the main scene elements relative to the canvas. High-resolution cinematic architectural artwork. No cover lettering, no readable text anywhere, no logos, no watermark, no added ornaments. Output ONLY the finished text-free background image.

## Interior — `interview-comic.png`

Prompt:

Use case: illustration-story. Create a sophisticated editorial comic strip for a personal literary essay about an experienced software engineer who built his own AI coding agent specifically for an interview, was told he could use his favourite AI tools, then denied their use during the interview, while his agents kept implementing and testing complex systems in the background. One wide horizontal strip, three equal panels, thin ink borders, warm ivory paper, hand-drawn graphite and muted watercolour, restrained amber and midnight blue. Panel one: close-up of a person's hands putting a small glowing intricate mechanical workshop into a laptop, care and preparation. Panel two: rear three-quarter view of a middle-aged engineer seated alone facing a laptop video interview, hands paused above keyboard, an unlit workbench tool resting beside him; quiet human vulnerability, interviewers small neutral silhouettes, no villains. Panel three: a different monitor on the same desk shows an intricate miniature workshop alive with precise autonomous machinery, work progressing, same person visible softly behind it still at interview. Visual irony is simultaneity, no triumphant robots, no ridicule. No readable text, no logos, no speech bubbles. Wide 3:1 composition, crisp enough for print, full image devoted to panels. Conceptual illustration, not a portrait of an identifiable real person.

## Earlier essay — `coordination-shift-cover.png`

The actual first page of Michel Blomgren's *The Coordination Shift: Software
Engineering in the Centaur Era*, reproduced from `../pub/10x.pdf` (published at
https://c89.systems/10x.pdf). Rendered with Poppler at 1800 pixels on its long edge.
LaTeX adds the paper border, tilt and shadow; the reproduced cover is unchanged.
The paper links to the original essay in the PDF.
