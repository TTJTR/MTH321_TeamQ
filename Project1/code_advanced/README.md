# Advanced comparison: two-stage Gauss implicit RK4

This folder adds a fourth-order Gauss–Legendre implicit Runge–Kutta method as a separate extension. It imports the matrix model and three baseline solvers from `../code/` and writes working outputs to `../figures/advanced_irk4/` and `../data/advanced_irk4/`.

The two stages are solved together by damped Newton on an 18-dimensional nonlinear system for a 9-dimensional vectorized matrix state. This method differs from four-stage explicit classical RK4. Its scalar stability function is `R(z)=(1+z/2+z²/12)/(1-z/2+z²/12)`: it is A-stable but not L-stable because `R(z)→1` as real `z→−∞`.

The method and tableau follow J. C. Butcher, *Numerical Methods for Ordinary Differential Equations*, 3rd ed., Wiley, 2016, Chapter 3 §34.2 (Gaussian quadrature methods), with stability discussion in §35.3 and implementation in §36.0. D. F. Griffiths and D. J. Higham, *Numerical Methods for Ordinary Differential Equations: Initial Value Problems*, Springer, 2010, Chapters 9–11 provide background on implicit methods and stability. See Section 5 and `references.tex` of the current report for citations.

| File | Purpose |
|---|---|
| `gauss_irk4.py` | Gauss tableau, coupled-stage Newton solver, stability function and work counts. |
| `run_comparison.py` | Runs four-method convergence, cost, energy and stability comparisons; writes data and figures. |
| `test_gauss_irk4.py` | Six checks of order, stability, nonlinear solve behavior and flow diagnostics. |
| `VALIDATION_RUN_2026-10-05.md` | Historical validation record for the extension at the time it was added. |

From `Project1/`:

```powershell
python -B code_advanced/test_gauss_irk4.py
python -B code_advanced/run_comparison.py
```

The script produces `convergence_comparison.png`, `cost_comparison.png`, `energy_comparison.png` and `stability_comparison.png`, plus `convergence_cost.csv`, `energy_trajectories.csv` and `summary.json`. The current report bundles the four figures in `report_v3/figures/advanced_irk4/`; the machine-readable advanced data are in project-level `data/advanced_irk4/`.
