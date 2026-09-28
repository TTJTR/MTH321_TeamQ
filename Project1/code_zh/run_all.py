"""一键运行题目 ⑤ 的全部实验并输出图表、CSV 和结果摘要。"""

from pathlib import Path

from experiments import run_all


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    # 中文运行使用独立输出目录，便于与英文结果比较，也避免覆盖报告版本。
    figure_dir = project_root / "outputs_zh" / "figures"
    data_dir = project_root / "outputs_zh" / "data"
    result = run_all(figure_dir, data_dir)
    print(f"图片已生成到：{figure_dir}")
    print(f"数值数据已生成到：{data_dir}")
    print("观测到的收敛斜率：")
    for method, info in result["convergence"].items():
        print(f"  {method}: {info['asymptotic_fit_slope']:.3f}")
    print(f"SVD 精确解与 Radau 的差异：{result['independent_oracle']['exact_svd_disagreement']:.3e}")
