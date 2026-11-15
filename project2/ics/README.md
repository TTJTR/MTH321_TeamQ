# Individual Contribution Statement — Meichen Ding (2362344)

`MeichendingICS.tex` is the standalone build of my appendix: Part A (AI
transparency log, with the claim audits) and Part B (individual contribution
statement), following `Checklist/ICS_bvp.tex`.

```bash
latexmk -pdf MeichendingICS.tex     # 5 pages
```

Single source: the body is `report/APPENDIX/MeichendingICS.tex`, which the
report itself inputs after `\appendix`, so the appendix page and this document
can never drift apart.

Before submission: sign and date the statement in Part B, and record the tool
versions in Table A.1 that were actually used (the table currently says
"current build, Oct–Nov 2026").
