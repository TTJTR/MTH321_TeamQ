"""Regenerate all report figures; optionally recompute classical experiments/build PDF."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd):
    print('Running: ' + ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recompute', action='store_true',
                        help='Re-solve classical experiments and replace measured timings.')
    parser.add_argument('--build-report', action='store_true', help='Also build Method.pdf with pdfLaTeX/BibTeX.')
    args = parser.parse_args()
    py = [sys.executable, '-B']
    alg, report = ROOT/'algorithm_section', ROOT/'report'
    if args.recompute:
        run(py + ['run_all.py'], alg)
    else:
        run(py + ['-m', 'unittest', 'discover', '-s', 'tests', '-v'], alg)
        run(py + ['make_figures.py'], alg)
    for stem in ['fig01_algorithm', 'fig02_sparse_assembly', 'fig03_accuracy_cost',
                 'fig04_interface', 'fig05_conditioning', 'fig06_solver_validation', 'fig07_mesh']:
        for ext in ['pdf', 'png']:
            shutil.copy2(alg/'figures'/f'{stem}.{ext}', report/'figures'/f'{stem}.{ext}')
    run(py + ['support/interface_pinn/reevaluate.py'], report)
    run(py + ['support/interface_pinn/make_figures.py'], report)
    # Architecture is native TikZ in interface_pinn_section.tex, rebuilt with the report.
    if args.build_report:
        build = report/'build'
        build.mkdir(exist_ok=True)
        latex = shutil.which('pdflatex')
        bibtex = shutil.which('bibtex')
        if not latex or not bibtex:
            raise SystemExit('Install pdfLaTeX and BibTeX and add them to PATH to use --build-report.')
        command = [latex, '-interaction=nonstopmode', '-halt-on-error', '-output-directory=build', 'Method.tex']
        run(command, report)
        env = dict(os.environ, BIBINPUTS=str(report)+os.pathsep+os.environ.get('BIBINPUTS', ''))
        subprocess.run([bibtex, 'build/Method'], cwd=report, env=env, check=True)
        run(command, report)
        run(command, report)
        shutil.copy2(build/'Method.pdf', report/'Method.pdf')
    print('All nine external figures regenerated and synced; TikZ architecture is in the TeX source.')
    print('No neural retraining. Classical timings '+('re-measured.' if args.recompute else 'preserved from archive.'))


if __name__ == '__main__':
    main()
