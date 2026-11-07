# Meichen Ding — individual package, Project 2 (PDE BVP, Direction 3)

This folder is my own contribution package for Project 2. It is **independent of
`project2/report/`**: nothing here overwrites the team's report files. It
contains

* a self-contained build of the report I am responsible for (model,
  discretisation and discrete analysis, with the team's results sections
  included unchanged so that the document compiles on its own),
* my ICS and the team AI transparency log as Appendix A,
* the three verification scripts I wrote, which regenerate the numerical claims
  quoted in that appendix and in §2.4.

## Build

```bash
cd project2/meichending
latexmk -pdf Method.tex          # -> Method.pdf, 32 pages
```

Requirements: TeX Live (pdflatex, bibtex, latexmk). The build is clean:

```
0 errors | 0 overfull boxes | 0 undefined references | 0 undefined citations
```

Every number quoted in the text comes from either the team's committed results
(`tables/`, `figures/`, produced by `project2/algorithm_section/run_all.py`) or
from the scripts in `support/verify/`; the provenance is stated in Appendix A,
table A.3, and in §5.

## Layout

| path | what it is |
| --- | --- |
| `Method.tex` | the report: §1 Introduction, §2 Discretisation and Analysis, §3–§5 (team), Appendix A (AI log + my ICS), Appendix B (provenance) |
| `algorithm_section.tex`, `results_section.tex`, `conclusion.tex` | the team's §3, §4, §5, included unchanged |
| `tables/` | the six result tables, included by the sections above |
| `figures/` | `fig01`–`fig06`, included by `algorithm_section.tex` |
| `refs.bib` | bibliography (8 entries) |
| `ics/MeichendingICS.tex` | **single source** of Appendix A: team AI transparency log (A1–A4) + my individual contribution statement |
| `support/verify/` | the three verification scripts and their README |
| `src/discretisation.py` | copy of the team's assembler, used by `check_matrix_evidence.py` |

`ics/MeichendingICS.tex` is also the body of the standalone ICS document
`project2/ics/MeichendingICS.tex`, so the report appendix and the ICS submission
can never drift apart. The report build sets `\def\reportbuild{}` before
including it, which turns the cross-references into the report's numbers; the
standalone build leaves it unset and prints words instead, so it has no
unresolved references.

## What is mine in this document

Per the sections and per Appendix A, table A.4:

* §1.2 — the model, its hypotheses, the variational form and well-posedness;
* §2.1–§2.4 — the conservative face-coefficient scheme, the truncation-error and
  interface-conductance analysis, boundary treatment, discrete structure
  (SPD / M-matrix / discrete maximum principle), discrete stability and the
  O(h²) convergence theorem, and the matched-settings protocol;
* the four remarks on the θ-correction, mesh parity, the two-dimensional
  boundary and symmetry-versus-accuracy;
* Appendix A (log and audits), Appendix B (provenance);
* `support/verify/*.py`.

§1.1, §3, §4, §5, the tables and the figures are the team's work, reproduced
here without modification so that this package compiles on its own.

## Verification scripts

```bash
python3 support/verify/check_interface_order.py    # 1D interface orders (A.3, audit 1)
python3 support/verify/check_stability.py          # counterexample + barrier bound (A.3, audit 2)
python3 support/verify/check_matrix_evidence.py    # symmetry defect, λ_min, Cholesky (§2.4 table)
```

`check_interface_order.py` and `check_stability.py` need only NumPy and do not
import the project solver; that independence is the point. The third one imports
the team's assembler on purpose, because its job is to corroborate the matrix
that is actually submitted.

## Known limitations (stated in the report)

* The maximum interface-flux error of the arithmetic-averaged scheme (≈ 0.662)
  is a boundary effect of the prescribed Dirichlet trace on `y = 0, 1`; it is an
  observation on this benchmark, not an estimate valid for other boundary data
  (§4.3, Remark `rem:arith_2d_boundary`).
* The constant `1/(8 a_min)` in the maximum-norm bound is sharp in one dimension
  and only an upper bound in two (`0.0736` versus `0.125`);
  §2.4, Remark `rem:conv_constant`, and `check_stability.py` show both.
* The repository history of the team report is a single upload commit, so
  authorship of individual sections is not visible in `git log`; the ownership
  table in Appendix A therefore carries only my own signed row.
