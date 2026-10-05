# Independent Validation Run — 2026-10-03

## 1. Scope and provenance

- Repository: <https://github.com/TTJTR/MTH321_TeamQ>
- Latest `main` used as the clean base: `023c928d6a218202968c3b14a67a6c9471aedb43`.
- Validation-test commit exercised in this run: `c4ca4eee16108e5bc9d76577e8df556059b428dd`.
- Source of the three migrated edge cases: PR #1, commit
  `6b0b65467e356feee1b519a2d4b3a15643325378`.
- Current locations: `Project1/test/` for runnable tests and
  `Project1/report_v3/checklist/` for this record. No obsolete
  `report_v1/checklist/test_validation.py` or root `V1_DELIVERY_CHECKLIST.md`
  was restored.

The current suite contains 13 tests in `test/test_validation.py` and one
independent bilingual parity test, for 14 tests in total. The previous PR's
`13/13` result was not reused.

## 2. Fresh environment

| Item | Value |
|---|---|
| Operating system | Windows 11, build 26200 |
| Python | 3.12.14 |
| NumPy | 2.5.3 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.2 |

The repository requirements are unpinned. The bundled report data records
Python 3.12.4, NumPy 1.26.4, SciPy 1.13.1 and Matplotlib 3.8.4, so raw PNG
hashes and last-bit numerical values are not expected to match across these
two environments.

## 3. Commands actually run

Run from `Project1/` with the clean virtual environment:

```powershell
.\.venv\Scripts\python.exe -c "import platform,numpy,scipy,matplotlib; print(platform.platform()); print(platform.python_version(), numpy.__version__, scipy.__version__, matplotlib.__version__)"
.\.venv\Scripts\python.exe -B -m unittest discover -s test -v
.\.venv\Scripts\python.exe -B code/run_all.py
.\.venv\Scripts\python.exe -B code_zh/run_all.py
```

After activation of the same virtual environment, these are equivalent to the
submission commands `python -B ...` listed in the project README files.

## 4. Test result

```text
Ran 14 tests in 16.443s

OK
```

All existing tests remained in place and all three migrated tests passed.

### 4.1 Adaptive tolerance sensitivity

`test_tighter_adaptive_tolerance_reduces_global_error` uses the exact
finite-time matrix as an independent global-error reference.

| Setting | Accepted | Rejected | Maximum accepted local ratio | Exact global error |
|---|---:|---:|---:|---:|
| `atol=1e-5`, `rtol=1e-3` | 7 | 1 | 0.835843 | 8.99391e-5 |
| `atol=1e-10`, `rtol=1e-8` | 42 | 2 | 0.900174 | 1.95767e-8 |

The tighter run used more accepted steps and reduced measured global error by
a factor of about 4594. This is numerical evidence, not a claim that the local
acceptance ratio is a certified global-error bound.

### 4.2 Large explicit step

`test_large_explicit_step_causes_singular_value_crossing` compares Explicit
Euler at two fixed step sizes.

| Step size | Singular-value crossing | Exact terminal error |
|---:|---|---:|
| 0.05 | no | 3.78091e-3 |
| 0.10 | yes | 2.36606e-2 |

The larger step remains finite but violates the no-crossing qualitative
behaviour and has a materially larger terminal error.

### 4.3 Newton failure and retry

`test_newton_failure_and_adaptive_retry_path` confirmed that one Implicit Euler
step of length 0.15 with `max_newton=4` reports
`StepFailure("Newton iteration did not converge")`. The adaptive controller
then rejected one attempt, halved the trial to 0.075, and completed at times
`[0, 0.075, 0.15]`. Its first accepted state matched an independently executed
two-half-step fixed calculation to machine precision. Its global error against
the exact ODE state at `t=0.075` was 1.28903e-1, illustrating that Newton
residual convergence and time-discretisation error are different quantities.

## 5. Reproduction of project results

Both English and Chinese entry points completed successfully. They printed:

| Quantity | Fresh run | Bundled report artifact |
|---|---:|---:|
| Explicit Euler fitted slope | 1.0101162413 | 1.0101162413 (displayed as 1.010) |
| RK4 fitted slope | 3.9274495745 | 3.9274157242 (displayed as 3.927) |
| Implicit Euler fitted slope | 1.0136814873 | 1.0136814873 (displayed as 1.014) |
| Exact SVD versus Radau | 1.1680372e-13 (1.17e-13 at 3 s.f.) | 1.1613543e-13 (1.16e-13 at 3 s.f.) |

Within the fresh environment, the English and Chinese outputs had identical
normalized CSV/JSON content and byte-identical PNG files. Compared with the
bundled `report_v3` artifacts, all CSV shapes and status fields agreed, and the
three convergence slopes reproduced the report's displayed precision. The
fresh Radau disagreement rounds to 1.17e-13 at three significant figures,
whereas the bundled result rounds to 1.16e-13. Their absolute difference is
6.68e-16 (about 0.575%), so they are close and support the same 1e-13-scale
cross-check, but they do not agree at three significant figures. Floating-point
last digits and all eight PNG hashes differed under the newer dependency
versions. Regenerated working data were inspected and then excluded from the
commit; the checked-in report artifacts were not overwritten.

The verification-coverage wording in `sections/section4.tex` was updated from
eleven to fourteen tests. On 2026-10-04, final report integration rebuilt
`report.pdf` from the latest `main` commit `45f0a01`, which includes validation
merge `b28fe39`, with Tectonic 0.17.0.
The stable output remains 32 pages: the table of contents places Section 4 on
page 22, Section 4.5 and Section 5 on page 27, References on page 28, and the
appendices on page 29. Section 4.5 now states fourteen tests and records all
three added edge checks. The final log has no undefined references, and all 32
rendered pages were visually checked.

After the final PDF and documentation corrections were complete, every manifest
entry was regenerated using the declared extension policy (raw bytes for CSV,
PNG, PDF and JSON; CRLF/CR-to-LF normalization for other files). Independent
verification then confirmed all 41 listed paths with 41/41 matches.

## 6. Evidence map

| New check | Related report evidence | Interpretation |
|---|---|---|
| Tighter adaptive tolerance | `adaptive_steps.csv` and `adaptive_steps.png` describe the report's standard tolerance run; the two extra tolerance settings are test-only. | Supports the local-versus-global error caveat; it is not plotted report data. |
| Large Explicit Euler step | `data/stability_sweep.csv` and `figures/stability_sweep.png`. | Confirms the documented large-step singular-value crossing. |
| Newton failure and retry | Section 3 adaptive algorithm and Section 4 limitations. | Exercises failure reporting and restart from the last accepted state; no separate CSV or figure is claimed. |

## 7. Verdict

The three edge cases are compatible with the current code and complement the
existing tests without replacing them. The full 14-test suite and both
reproduction entry points passed. The convergence slopes agree with the report
at its displayed precision; the Radau cross-check is close and on the same
1e-13 scale but rounds differently at three significant figures. Pin dependency
versions if future submissions require byte-identical figures rather than
numerical agreement.
