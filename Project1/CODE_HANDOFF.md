# Code and numerical-results handoff

This file is for assembling Sections 3 and 4 of the group report. The
assignment brief and Problem Pack are the requirements; the aligned v5
report is `report_v1/Section2Draft_v5.tex`. All numbers below come from `python code/run_all.py`
and are reproducible from `code/figures/summary.json` and the companion CSVs.

## Reproduction and implementation (Section 3)

Run from `Project1` after installing `requirements.txt`:

```powershell
python code/run_all.py
python -B -m unittest discover -s report_v1/checklist -v
```

The state is `vec(X)` with column-major ordering (`order='F'`) throughout.
`code/model.py` defines the Topic 5 benchmark, RHS, analytic Fréchet/Jacobian,
finite-time SVD solution, and diagnostics. `code/solvers.py` implements Explicit
Euler, classical RK4, and Implicit Euler with a damped Newton solve. The Newton
stopping rule is `||F(w)||_inf <= tol * (1 + ||w||_inf)`, with `tol=1e-12`.
Backtracking requires a strict residual decrease. In adaptive integration a
failed Newton attempt is rejected and retried at half the step from the last
accepted state. Fixed-grid convergence runs instead signal failure, since
changing their grid would invalidate the observed-order calculation.

Adaptive integration uses step doubling. It compares one full step with two
half steps, accepts the fine result when the normalized componentwise error is
at most one, and updates `h` with safety factor 0.9 and scale limits [0.2, 2].
SciPy `solve_ivp(method='Radau')` is used only for the **independent reference
check**, not as one of the three tested solvers.

## Exact-solution validation (Section 4.1)

Benchmark: `X0 = R(0.4) diag(0.2, 1.4, 3) R(-0.7)^T`, interval `[0,2]`.
Terminal error is `||X_h(2) - X_exact(2)||_F`, using the **full finite-time
matrix**, not the limiting polar factor. The independent Radau solution
(`rtol=1e-12`, `atol=1e-14`) differs from the SVD solution by `1.16e-13`.

| Method | Fitted slope | Fit range h | Finest-grid error |
|---|---:|---|---:|
| Explicit Euler | 1.010 | 0.05 to 0.00625 | 4.61e-4 |
| RK4 | 3.927 | 0.003125 to 0.00078125 | 7.40e-14 |
| Implicit Euler | 1.014 | 0.05 to 0.00625 | 4.64e-4 |

RK4's coarse-grid adjacent orders are irregular because the `s0=3` mode has a
rapid initial transient; the slope approaches four on refined grids. Its
finest error is close to floating-point scale, so do not extrapolate the trend
indefinitely. Use `convergence.png` and `convergence.csv` for the figure and
complete numerical table.

## Cost at matched accuracy (Section 4)

`cost_accuracy.png` plots achieved error against RHS evaluations over several
fixed grids; stars identify the matched-error comparison points, and
`cost_accuracy.csv` contains all plotted rows. Explicit Euler uses `N=160` and error
`9.2066e-4` with 160 RHS evaluations; RK4 uses `N=17` and error `8.8502e-4`
with 68 RHS evaluations; Implicit Euler uses `N=160` and error `9.3194e-4`
with 862 RHS evaluations, 351 Jacobian evaluations and 351 Newton updates.
The largest error is about 5.3% above the smallest. The plotted cost measure
is RHS evaluations; Jacobian assembly, linear factorization, Python overhead
and plotting are not counted, so the curves are not a wall-clock ranking.

## Stability and geometry (Sections 4.2 and 4.4)

`stability_regions.png` shows all three analytic amplification regions;
`frozen_spectrum.png` shows `h lambda` for `h=0.05` and `h=0.10`. The initial
Jacobian has eigenvalues `[-26, -14.16, -8.64, -7.44, -5.76, -4.88,
-1.28, -0.72, 0.88]`. The positive eigenvalue is physical growth of the
small singular value, not a spurious numerical mode. The local negative-real
thresholds from the `-26` mode are `h≈0.0769` (Euler) and `h≈0.1071` (RK4).

`stability_sweep.csv` tests `h=2/N` over `N=6,...,80` (selected values).
It contains one-step amplification of a `1e-7` perturbation in the fast
singular-vector direction, maximum energy increase, singular-value crossings,
terminal exact error, and a failure marker. For Euler at `h=0.10`, the
one-step perturbation grows by `1.60` and a singular value crosses 1, although
the full trajectory remains finite. Euler at `h=2/7≈0.2857` raises the
energy by `31.9` in the first step and later diverges. RK4 at `h=1/3`
also diverges. Implicit Euler finishes these sweeps. These observations test
the local prediction, but the `h lambda` lines are **not** nonlinear global
stability boundaries. In particular, an RK4 run above `0.1071` may still
finish because the state-dependent Jacobian changes after the first step.

For a well-resolved RK4 trajectory (`h=0.005`), all sampled singular values move
toward 1 without crossing and `Phi(X)` is monotone. At `t=2`, its
orthogonality defect is `0.305932824226`, versus the **nonzero** exact value
`0.305932824210`. The midpoint discrete check of
`dPhi/dt = -||X(I-X^T X)||_F^2` has a maximum residual scaled by
`max(1, |theoretical rate|)` of `4.69e-4`; this is not a pure relative error.
It is a finite-difference diagnostic, so zero is not expected. The figure has
a fourth panel showing the absolute residual at every interval midpoint.
Use `trajectory_diagnostics.png` and `trajectory.csv`.

## Adaptivity (Section 4.3)

With `atol=1e-8`, `rtol=1e-6`, and initial trial `h=0.15`, RK4 accepts 17
steps and rejects 2, with accepted steps ranging from `0.0223` to `0.2442`.
Its largest accepted normalized local error is `0.754`, and terminal exact
error is `6.89e-7`. Both Euler methods need about 1680 accepted steps to
meet the same local budget. The final clipped step can be unusually short;
do not interpret it as renewed stiffness. Use `adaptive_steps.png` and CSV.
The local error tolerance is not a bound on the *global* terminal error.

## Rank-deficient experiment (Section 4.5)

Replacing `0.2` by zero and integrating over `[0,8]` with RK4 `h=0.005`
leaves the smallest singular value below `7.1e-15`. The final
orthogonality defect is `1.0000000000000064`, consistent with a rank-two
partial isometry rather than an orthogonal matrix. Use
`rank_deficient.png` and `rank_deficient.csv`.

## Report integration status

The v5 report in `report/Section2Draft_v5.tex` now identifies
`code/experiments.py` as the generator, includes both stability figures and
the other six PNGs, and replaces the old Sections 3 and 4 placeholders with
the measured experiments above. Its implicit Euler argument separates the
exact-endpoint residual from the one-step error, and its Newton and adaptive
pseudocode follow the completed code. The remaining team-specific inputs are
names/IDs, full AI transparency information, and individual contribution
statements. See `CHANGELOG_V5.md` for the itemized revision record.
