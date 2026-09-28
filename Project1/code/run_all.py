"""Run all Topic 5 experiments and write reproducible plots, CSVs, and summary."""

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
