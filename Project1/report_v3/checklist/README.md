# Current delivery checklist

Checked against the Topic 5 assignment, the course code review checklist, the submission checklist and the visualization guide. This checklist describes the **current** English-source delivery; [the 2026-10-03 validation run](VALIDATION_RUN_2026-10-03.md) records a historical 14-test bilingual state.

| Requirement | Evidence | Status |
|---|---|---|
| Matrix ODE and prescribed initial condition | `code/model.py`, Sections 2–3 | Complete |
| Explicit Euler, classical RK4 and implicit Euler | `code/solvers.py`, Sections 2–4 | Complete |
| Finite-time full-matrix exact solution and order plot | `code/model.py`, `convergence.png`, `convergence.csv` | Complete |
| Step-doubling adaptive control with stated tolerance | `code/solvers.py`, `adaptive_steps.png`, `summary.json` | Complete |
| Quantitative stability and linearised spectrum | `stability_regions.png`, `frozen_spectrum.png`, `stability_sweep.png` | Complete |
| Lyapunov, singular-value and rank-deficient diagnostics | `trajectory_diagnostics.png`, `rank_deficient.png`, Appendix C | Complete |
| Advanced two-stage Gauss implicit RK4 | `code_advanced/`, Section 5 and four advanced figures | Complete |
| Core independent tests | `test/test_validation.py` (13 tests) | Complete |
| Advanced method tests | `code_advanced/test_gauss_irk4.py` | Complete |
| Figure/data descriptions and reproduction | `README_EN.md`, `report_v3/README.md`, Appendix C | Complete |
| Historical reports retained | `report_v1/`, `report_v2/` | Complete |

## Commands

From `Project1/`:

```powershell
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B -m unittest discover -s test -v
python -B code_advanced/test_gauss_irk4.py
python -B code_advanced/run_comparison.py
```

The two pseudocode blocks are Algorithm 1 in `sections/section2.tex` (Newton) and Algorithm 2 in `sections/section3.tex` (step doubling). The current report includes Sections 1–6 and Appendices A–C. Past result counts in the historical validation record describe its dated run and should not be used as current test counts.
