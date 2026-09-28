# Independent Validation Run - 2026-09-28

## 1. Scope and provenance

- Repository: <https://github.com/TTJTR/MTH321_TeamQ>
- Base/source commit validated: `c4a3024e14887e81518200d7c49812f7339be89b`
- Scope: Topic 5 numerical code, independent reference checks, report-number
  reproduction, English/Chinese parity, and three new edge-case tests.
- The base commit contains 10 tests. The final working tree adds three tests,
  for a total of 13. The validation additions were not assigned a commit SHA
  during this run; the eventual author should commit them under their own name.

The latest remote `main` commit was reproduced in a separate detached worktree
so that running the generators could not mix regenerated CSV/PNG files into the
test changes.

## 2. Fresh environment

| Item | Value |
|---|---|
| Operating system | Windows 11, build 26200 |
| Python | 3.12.14 |
| NumPy | 2.5.3 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.2 |

The repository's `requirements.txt` names the three packages but does not pin
versions. The committed `summary.json` records the earlier stack Python 3.12.4,
NumPy 1.26.4, SciPy 1.13.1, and Matplotlib 3.8.4. This difference matters for
last-bit numerical values and binary image hashes, so the findings below compare
scientific claims and stated tolerances rather than requiring byte identity.

## 3. Reproduction commands

Run from `Project1/` with the clean virtual environment's Python executable:

```powershell
git rev-parse HEAD
python -c "import platform,numpy,scipy,matplotlib; print(platform.python_version(), numpy.__version__, scipy.__version__, matplotlib.__version__)"
python -B -m unittest discover -s report_v1/checklist -v
python code/run_all.py
python code_zh/run_all.py
```

To create an equivalent environment from scratch:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s report_v1/checklist -v
.\.venv\Scripts\python.exe code/run_all.py
.\.venv\Scripts\python.exe code_zh/run_all.py
```

## 4. Baseline reproduction

The unmodified latest commit's original suite passed **10/10** tests. Both
`code/run_all.py` and `code_zh/run_all.py` completed and generated eight PNGs,
six CSV files, and `summary.json` in their respective output directories.

Key regenerated values were:

| Quantity | Regenerated value | Printed value |
|---|---:|---:|
| Explicit Euler fitted slope | 1.01011624131295 | 1.010 |
| RK4 fitted slope | 3.92744957454398 | 3.927 |
| Implicit Euler fitted slope | 1.01368148734238 | 1.014 |
| Exact SVD versus Radau | 1.16803719973896e-13 | 1.168e-13 |

The regenerated English and Chinese `summary.json` files had identical
SHA-256 hashes, and all eight English/Chinese generated PNG pairs were
byte-identical.

The two upstream commits added after the earlier `7d89799` validation baseline
were also checked explicitly. Commit `8e5103c` adds an `h=0.08` initial-spectrum
overlay to the stability-region figure and records
`stability_region_overlay_step = 0.08`; the fastest mode is
`0.08 * (-26) = -2.08`, as stated in the updated report. Commit `c4a3024`
documents the minimal report layout and standardizes the test command with
`-B`; it does not change the numerical model, solvers, or original tests.

## 5. Report-number check

| Report claim | Fresh reproduction | Result |
|---|---:|---|
| Euler slope 1.010 | 1.010116 | PASS at reported precision |
| RK4 slope 3.927 | 3.927450 | PASS at reported precision |
| Implicit Euler slope 1.014 | 1.013681 | PASS at reported precision |
| Euler finest error 4.6141e-4 | 4.6140917e-4 | PASS |
| RK4 finest error 7.3968e-14 | 7.39647e-14 | PASS at 3 significant digits (7.40e-14) |
| Implicit Euler finest error 4.6429e-4 | 4.642855e-4 | PASS |
| Adaptive accepted/rejected counts | Euler 1680/5; RK4 17/2; Implicit Euler 1678/5 | PASS exactly |
| Adaptive terminal errors | 5.0752e-5; 6.8890e-7; 5.0921e-5 | PASS at reported precision |
| Matched-cost errors/RHS calls | 9.2066e-4/160; 8.8502e-4/68; 9.3194e-4/862 | PASS |
| Exact SVD versus Radau 1.16e-13 | 1.168037e-13 | PASS against `<5e-12`; version-sensitive display value |

The Radau result remains more than an order of magnitude inside the automated
acceptance threshold. It does not literally reproduce the report's `1.16e-13`
to three significant digits under the newer SciPy version (the fresh value
rounds to `1.17e-13`). This is recorded as dependency sensitivity, not hidden.

The eight newly rendered English PNGs did not have the same hashes as the eight
committed report PNGs under the newer Matplotlib stack. Their English and Chinese
counterparts did match each other, and the numerical conclusions reproduced.
Therefore the earlier `8/8 identical` statement remains evidence for the
original recorded environment, not a claim about arbitrary Matplotlib versions.

## 6. New edge-case tests

### 6.1 Adaptive tolerance sensitivity

`test_tighter_adaptive_tolerance_reduces_global_error` compares two RK4 runs
against the exact finite-time matrix.

| Setting | Accepted | Rejected | Maximum accepted local ratio | Exact global error |
|---|---:|---:|---:|---:|
| `atol=1e-5`, `rtol=1e-3` | 7 | 1 | 0.835843 | 8.99391e-5 |
| `atol=1e-10`, `rtol=1e-8` | 42 | 2 | 0.900174 | 1.95767e-8 |

Both runs satisfy the controller's local acceptance rule. The tighter run uses
more steps and reduces the independently measured global error by more than a
factor of 100. The test deliberately does not treat the local error estimate as
a certified global-error bound.

### 6.2 Large-step geometric failure

`test_large_explicit_step_causes_singular_value_crossing` compares Explicit
Euler on the same interval and initial matrix.

| Step size | Singular-value crossing | Exact terminal error |
|---:|---|---:|
| 0.05 | no | 3.78091e-3 |
| 0.10 | yes | 2.36606e-2 |

The test confirms that a run may remain finite while a large step destroys a
qualitative property of the exact flow and materially increases global error.

### 6.3 Newton failure and adaptive retry

`test_newton_failure_and_adaptive_retry_path` first verifies that an Implicit
Euler step of length 0.15 with `max_newton=4` raises
`StepFailure("Newton iteration did not converge")`. The adaptive controller then
rejects that attempt, retries from the last accepted state with step 0.075, and
finishes at times `[0, 0.075, 0.15]`. The first accepted state agrees to
`atol=1e-14` with an independent fixed-grid calculation made from the original
state using two steps of length 0.0375.

## 7. Final test result

After adding the three edge tests, the complete suite passed **13/13** tests:

```text
Ran 13 tests
OK
```

## 8. Updated PDF check and verdict

The committed `Section2Draft_v5.pdf` is readable as a 29-page A4 PDF. All 29
pages were rendered for visual inspection. No clipped text, overlapping objects,
missing figures, or unreadable labels were found. The updated stability-region
figure on page 13 contains the `h=0.08` spectrum markers, the `-2.08` annotation,
and a caption consistent with the regenerated summary and source code.

The built-in LaTeX compiler could not independently rebuild the source in this
environment because its runtime reported `Unable to find standard directories
for platform`. This is recorded as an environment limitation rather than a
successful compilation check; PDF readability and rendering were verified
directly from the committed artifact.

Verdict: the core numerical claims reproduce, the independent exact/Radau
evidence remains comfortably within its acceptance criterion, and the new tests
cover the previously unasserted loose-tolerance, large-step, and Newton-retry
paths. For stronger binary reproducibility, pin the dependency versions or add a
lock file; otherwise continue to compare numerical claims at declared precision
instead of requiring PNG/CSV byte identity across library versions.
