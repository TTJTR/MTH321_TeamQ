"""Regenerate all baseline and advanced Topic 5 report figures and data."""

import subprocess
import sys
from pathlib import Path

from experiments import run_all


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    figure_dir = project_root / "figures"
    data_dir = project_root / "data"
    result = run_all(figure_dir, data_dir)
    print(f"Generated figures in {figure_dir}")
    print(f"Generated numerical data in {data_dir}")
    print("Observed convergence slopes:")
    for method, info in result["convergence"].items():
        print(f"  {method}: {info['asymptotic_fit_slope']:.3f}")
    print(f"Exact SVD vs Radau: {result['independent_oracle']['exact_svd_disagreement']:.3e}")
    sys.stdout.flush()

    # Keep the advanced experiment independent while giving the report one
    # reproducible entry point. A failed comparison fails this command too.
    subprocess.run(
        [sys.executable, "-B", str(project_root / "code_advanced" / "run_comparison.py")],
        cwd=project_root,
        check=True,
    )
