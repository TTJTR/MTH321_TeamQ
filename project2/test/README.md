# Project 2 · Independent tests

This directory follows the [Project 1 test layout](https://github.com/TTJTR/MTH321_TeamQ/tree/fac2d5bb8cd7491f284354d54442913f655d9378/Project1/test). Place it under `project2/` alongside `algorithm_section/`. Run the commands from `project2/`.

```powershell
python -m pip install -r algorithm_section/requirements.txt
python -B -m unittest discover -s test -v
```

The core suite exercises the production FDM and FEM assemblers and solvers. Independent checks cover the smooth source and four-mesh rates, asymmetric Dirichlet elimination and indexing, positive definiteness, layered interface flux and maximum principle, and explicit residuals and algebraic error. The suite writes no results to disk.

## Course bank and defect regression

Use the original course bank file to enable P1, P2, P4 and P5. The test solves all four problems with both production assemblers on four meshes. P3 requires a Neumann boundary closure and is outside the scope of these all-Dirichlet assemblers.

```powershell
$env:MTH321_TEST_BANK = 'C:/path/to/03_Scaffolding/test_problem_bank.py'
python -B -m unittest discover -s test -v

$env:MTH321_STRICT_VALIDATION = '1'
python -B -m unittest discover -s test -v
Remove-Item Env:MTH321_STRICT_VALIDATION
```

Strict mode checks the intended behaviour for known defects in the pinned snapshot. It exits nonzero on that snapshot. Use it to verify fixes for coefficient validation and averaging, diagonal-matrix diagnostics, and uniform-material spectral estimation.

## Regenerate the evidence tables

The checked-in `results/` files are the measured record. The commands below put a fresh run in a separate folder.

```powershell
$scratch = Join-Path ([IO.Path]::GetTempPath()) ("mth321-p2-validation-" + [guid]::NewGuid())
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
python -B test/validate_smooth.py --algorithm algorithm_section --bank "$env:MTH321_TEST_BANK" --out "$scratch"
python -B test/validate_interface.py --algorithm-dir algorithm_section --out-dir "$scratch"
```

For a stock rerun, copy `algorithm_section/` and run `python -B run_all.py` from the copy. Compare its output with the untouched directory using the command below.

```powershell
python -B test/compare_upstream.py algorithm_section 'C:/path/to/rerun-copy' "$scratch/upstream_comparison.csv"
```

The optional PINN check uses the six checkpoint files in the pinned `I-PINNs/` tree and the local `I-PINNs_supplement/` data. It evaluates frozen weights using NumPy.

```powershell
python -B test/recheck_pinn.py --snapshot I-PINNs --supplement 'C:/path/to/I-PINNs_supplement' --output "$scratch/pinn_evidence.json"
```

See the [dated validation run](VALIDATION_RUN_2026-11-06.md) for the executed commands, logs, measurements and remaining defects.
