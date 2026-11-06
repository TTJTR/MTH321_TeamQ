# Independent validation run · 2026-11-06

## Scope and environment

- Team baseline `fac2d5bb8cd7491f284354d54442913f655d9378`, recovered by Git blob ID into an isolated local copy. The tested code is in `project2/algorithm_section/`.
- New test entry point [test_validation.py](test_validation.py). The commands ran from the local `project2/` directory after adding `test/`.
- Windows 11 x64 build 26200, CPU float64, Python 3.13.15, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.1 and threadpoolctl 3.6.0. The validation suite limits BLAS to one thread.

## Executed tests

| Invocation | Exit | Measured outcome |
|---|---:|---|
| `python -B -m unittest discover -s test -v` | 0 | 8 passed, 3 skipped. Course bank and the two strict checks are opt-in. [Log](results/unittest_default.log) |
| Same command with `MTH321_TEST_BANK` set to the course bank | 0 | 9 passed, 2 skipped. The bank test made 32 solver runs across P1, P2, P4 and P5. [Log](results/unittest_with_bank.log) |
| Same command with the bank path and `MTH321_STRICT_VALIDATION=1` | 1 | The 9 checks above passed. Two additional test methods reproduced 10 failing subtests. [Log](results/unittest_strict.log) |
| `python -B run_all.py` from the isolated `algorithm_section/` copy | 0 | 7 original tests passed. The entry point regenerated 8 smooth records, 12 layered records, figures and tables. [Log](results/upstream_run.log) |

The following commands produced the independent evidence. In this run the bank path referred to the original `P2/03_Scaffolding/test_problem_bank.py`.

~~~powershell
python -B test/validate_smooth.py --algorithm algorithm_section --bank "$env:MTH321_TEST_BANK" --out "$scratch"
python -B test/validate_interface.py --algorithm-dir algorithm_section --out-dir "$scratch"
python -B test/compare_upstream.py algorithm_section "$rerun" "$scratch/upstream_comparison.csv"
python -B test/recheck_pinn.py --snapshot I-PINNs --supplement "$supplement" --output "$scratch/pinn_evidence.json"
~~~

`$rerun` is the isolated copy containing the output of `run_all.py`. `$supplement` is the path to `I-PINNs_supplement/`. [Setup and commands](README.md)

The published strict log uses relative paths in its tracebacks.

## Measured results

| Check | Result | Raw evidence |
|---|---|---|
| Smooth diffusion | Common P1-integrated L² fit over N = 32, 64, 128 was 1.999963 for FDM and 1.998978 for FEM. | [Four meshes](results/smooth_convergence.csv) |
| Boundary elimination and ordering | The independent affine test used asymmetric, nonzero Dirichlet data on all four sides. The dense-reference solution and the production solution differed by at most 4.89e-15. | [Affine check](results/smooth_affine_patch.csv), [course bank](results/smooth_course_bank.csv) |
| Layered diffusion | Harmonic FDM and fitted FEM reproduced exact nodal values within 7e-13. At N = 63, arithmetic FDM had a maximum physical interface flux error of 0.662, despite a reconstructed jump of about 4e-13. | [Interface runs](results/interface_layered.csv) |
| Algebra and conditioning | At N = 32, tightening CG from 1e-6 to 1e-12 changed the CG–LU maximum solution difference from 5.81e-10 to 5.33e-15 for FDM and from 4.00e-8 to 1.01e-14 for FEM. The nodal discretisation error remained about 8e-4. | [Residuals and tolerance](results/interface_algebra.csv), [independent spectrum](results/interface_conditioning.csv) |
| Comparison with committed data | For the stock smooth runs, the largest absolute difference in common L² was 4.58e-14. The stock condition-number routine also reproduced its original bias. | [Rerun comparison](results/upstream_comparison.csv) |
| Optional PINN evidence | Replayed six frozen checkpoints, recalculated 18 archive acceptance labels, and evaluated the frozen models on new hold-out points. This environment lacked a working PyTorch installation, so training remains outside the rerun. | [PINN data](results/pinn_evidence.json) |

## Open defects reproduced by strict mode

Paths are relative to `project2/algorithm_section/`.

| Source and trigger | Observed versus expected | Suggested change |
|---|---|---|
| `src/discretisation.py:43–56,124–126`. Layered FDM/FEM with `contrast=float("nan")` or `float("inf")`. | Four cases returned matrices or RHS values containing non-finite entries. The API should reject non-finite contrasts before assembly. | Check finiteness as well as positivity before assembly. |
| `src/discretisation.py:54–56`. Harmonic FDM at `N=7`, contrasts `1e-200` and `1e200`. | Pure right-material faces had weights of 0 and infinity. Those faces should retain the finite input material value. | Evaluate the harmonic mean using a min/max ratio to avoid an intermediate product. |
| `src/solvers.py:70–77`. Call `structure(csr_matrix([[4.0]]))`. | The empty off-diagonal reduction raises `ValueError`. A diagonal SPD matrix has zero off-diagonal magnitude. | Define the off-diagonal statistic for an empty sparse structure. |
| `src/solvers.py:80–83`. Harmonic layered FDM with `c=1` on N = 15, 31, 63. | The fixed start missed the largest eigenvalue in three cases. At N = 15, the resulting condition estimate was 89.045 instead of the closed-form 90.523. | Use a seeded non-structured start and test the uniform-coefficient spectrum against the closed form. |

[All 27 input and diagnostic probes](results/smooth_input_checks.csv)
