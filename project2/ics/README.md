# ICS & AI Transparency Log — Meichen Ding (2362344)

This folder holds **one** ICS, mine, as required for the individual part of the
submission. It follows the format of `Checklist/ICS_bvp.tex`:

* **Part A — Team AI Transparency Log** (A1 tools, A2 claim audits, A3
  independent verification and decision, A4 intellectual ownership), and
* **Part B — Individual Contribution Statement** (name, role, the specific
  things I did, what I would do differently, what I should have asked for help
  with earlier).

## Build

```bash
cd project2/ics
latexmk -pdf MeichendingICS.tex     # -> MeichendingICS.pdf, 6 pages
```

Clean build: 0 errors, 0 overfull boxes, 0 undefined references.

## Single source

`MeichendingICS.tex` is only a title page. The body is
`../meichending/ics/MeichendingICS.tex`, which is also included as Appendix A of
`../meichending/Method.tex`. There is exactly one copy of the text, so the ICS
you submit and the appendix in the report cannot disagree. The report build sets
`\def\reportbuild{}` first, which makes the cross-references resolve to the
report's numbers; this standalone build leaves it unset and prints descriptive
words instead, so no reference can dangle.

## Note on Part A

Part A is the team-level log; I drafted and audited it, and it is the copy that
belongs in the team report. Table A.4 (ownership declaration) carries only my
own signed row: an ownership declaration is not drafted on another member's
behalf, so the other four rows are completed and signed by each member in their
own copy.
