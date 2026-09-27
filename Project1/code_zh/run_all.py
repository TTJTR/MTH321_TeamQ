"""一键运行题目 ⑤ 的全部实验并输出图表、CSV 和结果摘要。"""

from pathlib import Path

from experiments import run_all


if __name__ == "__main__":
    destination = Path(__file__).resolve().parent / "figures"
    result = run_all(destination)
    print(f"全部结果已生成到：{destination}")
    print("观测到的收敛斜率：")
    for method, info in result["convergence"].items():
        print(f"  {method}: {info['asymptotic_fit_slope']:.3f}")
    print(f"SVD 精确解与 Radau 的差异：{result['independent_oracle']['exact_svd_disagreement']:.3e}")
