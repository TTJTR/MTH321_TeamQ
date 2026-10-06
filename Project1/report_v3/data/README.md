# Baseline numerical evidence

The six complete CSV files and `summary.json` support the eight baseline figures. Appendix C provides formulas, figure links and rounded extracts. Row counts exclude headers. All model quantities, time and step lengths are dimensionless. SVD columns are sorted in descending order, so `s1,s2,s3` do not follow the order of the input diagonal.

| File | Rows | Content |
|---|---:|---|
| `adaptive_steps.csv` | 3375 | Accepted steps and normalized estimated local error. |
| `convergence.csv` | 15 | Full-matrix error, observed order and work counts. |
| `cost_accuracy.csv` | 19 | Error and work for matched-accuracy comparison. |
| `rank_deficient.csv` | 1601 | Numerical and exact singular values for the rank-deficient case. |
| `stability_sweep.csv` | 39 | Perturbation amplification, energy, crossing and failure status. |
| `trajectory.csv` | 401 | Singular values, energy, orthogonality defect and identity residual. |
| `summary.json` | — | Software versions, parameters, spectra, orders, work and diagnostics. |

## Columns

```text
adaptive_steps.csv: method, t_start, h, normalized_local_error
convergence.csv: method, n_steps, h, terminal_frobenius_error, observed_order, rhs_evaluations, jacobian_evaluations, newton_iterations
cost_accuracy.csv: method, n_steps, h, terminal_frobenius_error, rhs_evaluations, jacobian_evaluations, newton_iterations, matched_point
rank_deficient.csv: t, s1, s2, s3, exact_s1, exact_s2, exact_s3
stability_sweep.csv: method, h, n_steps, one_step_fast_perturbation_amplification, one_step_energy_change, max_energy_increase, singular_value_crossing, terminal_exact_error, status
trajectory.csv: t, s1, s2, s3, energy, exact_energy, orthogonality_defect, exact_orthogonality_defect, lyapunov_identity_residual_next_interval
```

Terminal errors compare the full matrix with the finite-time exact SVD solution. `observed_order` uses the log-base-2 ratio between adjacent grids; the first row of each method has no previous grid. RHS counts include Newton residual and backtracking evaluations and are not elapsed time. `diverged_or_failed` means that the run did not finish; missing measurements are not zeros. The Lyapunov residual belongs to the interval after its row and is plotted at the midpoint. `normalized_local_error` is an accepted-step estimate, not a bound on global endpoint error. Regenerate working outputs with `python -B code/run_all.py` from `Project1/`; the submitted report snapshot is unaffected.
