# Project 2 — Variable diffusion, Team Q

Solve `-div(a grad u) = f` on the unit square with prescribed Dirichlet data
on all four outer edges. Conservative five-point FDM is the core method;
conforming triangular P1 FEM provides the matched depth comparison. An
Interface PINN baseline is an additional extension. It uses two independent
subnetworks and is not an exact reproduction of the published I-PINNs model.

## Report and source

- [Report PDF — MTH321_Project2_TeamQ_Report.pdf](report/MTH321_Project2_TeamQ_Report.pdf)
- [LaTeX entry — Method.tex](report/Method.tex)
- [Report source/build guide](report/README.md)
- [Course checklist and remaining manual items](reviews/CHECKLIST_STATUS.md)

The report has 50 pages, including references, AI records, five labelled ICS
and the evidence index. Keep the complete `report/` directory to compile it.
`report/Method.pdf` is retained as a compatibility build copy; the formally
named PDF above is the reader-facing report. Both contain the same document.

## Environment

Reuse the established course environment; do not rebuild or upgrade the
fixed NumPy/SciPy/Matplotlib base. [ENVIRONMENT.md](ENVIRONMENT.md) records
Project 1 context and the actual versions used here. The existing local `dl`
environment already contains the dependencies used in the recorded runs.

PINN adds PyTorch: CPU replay was tested with 2.7.1+cpu. The optional
[PINN requirement](requirements-pinn.txt) records that extension. Archived
training used PyTorch 2.8.0+cu128 on an A100-PCIE-40GB; replaying checkpoints
is distinct from training. `pypdf` is used for artifact checks only.
[requirements.txt](requirements.txt) lists compatibility bounds for the
combined workflow, rather than an instruction to upgrade the course base.

## One-command reproduction

From the repository root:

```text
conda activate dl
cd project2
python -B code/run_all.py
```

The default command:

1. Runs the seven production micro-tests.
2. Regenerates seven classical figures from saved data.
3. Replays three interface and three single-network checkpoints on CPU,
   solving FDM/FEM references at common sample points.
4. Regenerates the two neural figures and synchronizes all nine external
   figures into `report/figures/`.

It preserves archived timing measurements and does not retrain networks.
The architecture diagram is native TikZ and is rebuilt with the report.

| Command, from `project2/` | Effect |
|---|---|
| `python -B code/run_all.py` | Replay evidence and regenerate all external figures |
| `python -B code/run_all.py --recompute` | Also re-solve classical experiments; overwrite their CSVs and timings |
| `python -B code/run_all.py --build-report` | Also build the report; requires pdfLaTeX/BibTeX on PATH |
| `python -B code/run_all.py --recompute --build-report` | Combine both options |

The build publishes `report/MTH321_Project2_TeamQ_Report.pdf` and the
compatibility `report/Method.pdf`. Neither option retrains PINNs. New
hardware timings must be reviewed before replacing reported table snapshots.

## Targeted commands

Run from `project2/`:

```text
python -B report/support/interface_pinn/reevaluate.py
python -B report/support/interface_pinn/make_figures.py
python -B report/support/verify/check_interface_order.py
python -B report/support/verify/check_stability.py
python -B report/support/verify/check_matrix_evidence.py
python -B code/check_artifacts.py
```

The interface-order and stability checks use independent small models; the
matrix-evidence check deliberately imports the production assembler.
For classical plots only, run `python -B make_figures.py` inside
`algorithm_section/`. The `--review` option redraws the accuracy/cost,
interface, conditioning and mesh plots. The unified entry also copies
classical figures into the report automatically.

## Validation

Run the independent default suite from `project2/`:

```text
python -B -m unittest discover -s test -v
```

To include the course bank and strict regressions in PowerShell, point the
variable at your instructor-provided file, then run the same suite:

```powershell
$env:MTH321_TEST_BANK = 'path/to/test_problem_bank.py'
$env:MTH321_STRICT_VALIDATION = '1'
python -B -m unittest discover -s test -v
```

The filename may contain spaces or `(1)`; the quoted path is passed unchanged.
The bank remains external. Without its path the bank test is skipped;
without the strict flag two regression tests are skipped.

The bank-enabled strict run on 2026-11-16 passed **11/11 tests, no skips**,
including 32 solves for P1/P2/P4/P5, FDM/FEM and four meshes.
[Output](reviews/evidence/strict_tests_with_bank.txt) and
[bank hash/run record](reviews/evidence/course_bank_run.json) are retained.
Production code has not changed since that passing run; later work adjusted
report text, documentation and the report export filename.

## File navigation

| Directory | Contents |
|---|---|
| [code/](code/) | Unified reproduction entry and artifact checker |
| [algorithm_section/](algorithm_section/) | Production assembly/solvers, configuration, micro-tests, CSVs, tables and plots |
| [test/](test/) | Independent validation code and numerical records |
| [report/](report/) | Current report PDF, LaTeX, references, figures and appendices |
| [report/support/interface_pinn/](report/support/interface_pinn/) | Six checkpoints, matching model source, logs, hashes and common-point replay |
| [report/support/verify/](report/support/verify/) | Canonical theory-check scripts |
| [report/support/ai_log/](report/support/ai_log/) | Contributor audit extracts and integrity record |
| [reviews/](reviews/) | Checklist, code review and scoped verification evidence |
| [I-PINNs/](I-PINNs/), [meichending/](meichending/) | Earlier experiment/contributor archives; `report/` is the current integrated report |

## Interpretation and submission status

The smooth FDM/FEM comparison matches data, mesh scale, unknown count,
solver tolerance and the integrated error norm. Layered FDM/FEM use different
mesh parities by design. The Interface PINN comparison uses an explicitly
named sampled relative norm; it must not be substituted for an integrated
continuous L2 error. The single-network ablation has 8,577 parameters versus
17,154 for the interface model and is not parameter matched.

Figure PDFs use vector graphics; PNG previews are saved at 300 dpi. Figure
filenames contain no timestamps. Figure 5 distinguishes finest-three-mesh
fitted lines from the labelled h-squared reference. The conditioning CSV's
spectral columns were corrected; original CG counts and timings are retained.

The report, code and evidence are present. Member signatures/draft
confirmations, presentation timing and final slides/report consistency remain
individual/team tasks, as recorded in the checklist. No fresh environment or
neural retraining is required to replay the submitted evidence.
