# Bibliography identity and version decisions

The manuscript's 49 distinct source URLs resolve to 47 works. Its source
mentions now use Pandoc author-year citations, emitted as native LaTeX
`\citep` commands. Descriptive source text is retained; a parenthesized year
attached to a cited title is removed when the citation already supplies it.
The cover abstract remains free of citations.
The reference list prints the complete recorded author lists, while in-text
citations retain the author-year style. Name prefixes remain part of author
labels, including *von Hippel* and *van Rossum*.
DOI links are printed once, without a second identical DOI URL; separate
publisher and author-manuscript URLs remain where the manuscript used them.

Bibliographic identities were drawn from the supplied evidence register v0.7
and chapter-specific source notes. Journal metadata for 29 DOI-linked sources
was checked against Crossref on 2026-10-11. Publisher, institution, arXiv, and
working-paper records supplied the remaining identities and version details.
This is a bibliographic check, not a new audit of the essay's empirical claims.

## Consolidation

- The DOI and MIT manuscript URLs for von Hippel's 1986 lead-user paper share
  `vonhippel1986leadusers`.
- The DOI and MIT manuscript URLs for von Hippel's 1994 sticky-information paper
  share `vonhippel1994sticky`.
- For those two works, the bibliography links the DOI and author manuscript
  separately, preserving access without creating duplicate entries.
- Repeated mentions elsewhere share their existing citation key.

## Publication and version dates

- Brynjolfsson, Rock, and Syverson's productivity-paradox source is cited as the
  2019 book chapter; its record also identifies NBER Working Paper 24001 (2017).
- Bresnahan and Trajtenberg's general-purpose-technology source is cited as the
  1995 journal article; its record identifies Working Paper 4148 (1992).
- Dillon and colleagues' source preserves arXiv version 4, dated 13 November
  2025 in the arXiv submission record, and identifies its NBER working-paper
  family. The version is fixed rather than replaced by a later manuscript.
- Humlum and Vestergaard are cited as the March 2026 RFBerlin discussion-paper
  revision linked by the manuscript, rather than assigning its current title
  and results to the original 2025 release. The NBER family is identified too.
- *Firm Data on AI* uses the linked 16 March 2026 BFI Working Paper 2026-47.
- *The Cybernetic Teammate* uses the 2026 Organization Science issue metadata:
  volume 37, issue 4, pages 1217–1242.
- Journal entries use the issue year where early-online and issue dates differ
  (including Adner 2017 and Acs and colleagues 2009).
- The two arXiv records retain their version identifiers. Reports, working
  papers, the METR research update, and the prior essay retain their actual
  publication types rather than being presented as journal articles.
- The prior essay is Michel Blomgren's 26 November 2025 *The Coordination Shift:
  Software Engineering in the Centaur Era*. Its publication URLs remain the
  requested future C89 PDF and Markdown addresses.

The bibliography is maintained directly in `references.bib`; building does not
perform network lookups or silently update bibliographic versions.
