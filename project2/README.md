# Project 2 — Direction 3, Team Q

The report solves -div(a grad u)=f on the unit square with Dirichlet data on
all four outer edges. Conservative FDM is compared with fitted triangular
P1 FEM. Interface PINN is an additional baseline, not an exact reproduction
of the published shared-parameter I-PINNs architecture.

## One-command reproduction

From this `project2` directory, after installing dependencies:

```text
python -m pip install -r requirements.txt
python -B code/run_all.py
```

This command runs the seven production micro-tests, regenerates the seven
classical figures from archived data, replays six neural checkpoints on CPU,
regenerates both neural figures and synchronizes every external figure into
`report/figures/`. No neural training is performed. Archived CPU timings are
preserved by default. The architecture figure is native TikZ, rebuilt with
the LaTeX report. PDF figure exports use vector graphics; PNG previews use
300 dpi. Filenames identify their role and contain no timestamps.

```text
python -B code/run_all.py --recompute
python -B code/run_all.py --build-report
```

`--recompute` also reruns the classical experiments and overwrites their CSV
results and timings with measurements from the current machine. It does not
retrain PINNs. `--build-report` requires pdfLaTeX/BibTeX on PATH and produces
`report/Method.pdf`. It can be combined with `--recompute`. LaTeX needs the
packages listed in `report/Method.tex`, including TikZ and stmaryrd.

## Independent checks

```text
python -B -m unittest discover -s test -v
python -B report/support/verify/check_interface_order.py
python -B report/support/verify/check_stability.py
python -B report/support/verify/check_matrix_evidence.py
python -B code/check_artifacts.py
```

The matrix-evidence script deliberately imports the production assembler;
the interface and stability scripts use separate small models. The analytic
course-bank test is skipped unless `MTH321_TEST_BANK` names the instructor's
`test_problem_bank.py`. Two additional strict defect-regression tests require
`MTH321_STRICT_VALIDATION=1`. They passed after fixing finite-input guards,
overflow/underflow in harmonic averaging, diagonal-only structure inspection,
and a largest-eigenvalue start-vector defect. A default run does not enable them.
The historical bank-enabled run is recorded under `test/`; this check does
not invent a fresh bank-enabled result if the course file is unavailable.

## Files and evidence

- `report/Method.tex`: report entry, with local section files, bibliography,
  vector figures, AI log and five labelled ICS bodies in `APPENDIX/`.
- `algorithm_section/`: production assembler, solvers, seven micro-tests,
  configuration, numerical tables and raw results.
- `test/`: independent validation suite and its historical run records.
- `report/support/verify/`: canonical theory-check scripts used in the report.
- `report/support/interface_pinn/`: six archived checkpoints, model code,
  training logs, hashes and common-point solution/flux replay.
- `report/support/ai_log/`: contributor-supplied audit extracts and hash.
- `reviews/CHECKLIST_STATUS.md`: current course-checklist status and limits.
- `reviews/evidence/`: outputs from this integration's targeted checks.
- `I-PINNs/`, `meichending/`: earlier archived experiment/contributor packages;
  `report/` is the canonical integrated report.

The single-network ablation has 8,577 parameters versus 17,154 for the
interface model; it is not parameter matched. The main FDM/FEM depth study
uses matching smooth-problem settings and a common integrated error norm.
Replaying checkpoints does not establish training reproducibility from scratch.
Signatures and contribution confirmations belong to the individual members.


The conditioning CSV eigenvalue columns were refreshed after the spectrum fix;
CG counts and previously measured timings are preserved. Initial failing strict
regressions and the passing rerun are both retained in `reviews/evidence/`.
