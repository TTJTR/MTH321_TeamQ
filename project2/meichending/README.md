# Meichen Ding — theory package (Project 2, Direction 3)

This folder holds the sources I own, so the report can be rebuilt without me:

- `support/verify/` — the three verification scripts behind Table 1, Section 4.3
  and the remark on the entrywise claim (see the README inside).
- the appendix source lives in `report/APPENDIX/MeichendingICS.tex`; the
  standalone build is in `ics/`.

The report itself (`report/Method.tex`) stays the team's file: the appendix is
pulled in with `\input{APPENDIX/MeichendingICS}` after `\appendix`.

Sections I own in the report: 1.2 (model, weak form), 2.1-2.4 (flux balance to
the five-point stencil, truncation error, interface conductance, boundary
elimination, M-matrix/DMP, convergence), the four remarks quoted in Appendix A,
Table 1, and Appendix A.
