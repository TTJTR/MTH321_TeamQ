# Numerical evidence / 数值证据

六份完整 CSV 与 summary.json 对应本版全部数值图。
附录 C 提供逐列定义、公式、对应图和摘录。行数不含表头。
模型量、时间与步长无量纲，工作量是次数。
SVD 列 s1≥s2≥s3 降序保存，不是初始对角输入顺序。

| File / 文件 | Rows / 行数 | Purpose / 用途 |
|---|---:|---|
| `adaptive_steps.csv` | 3375 | Accepted steps / 实际接受步长与局部估计 |
| `convergence.csv` | 15 | Full-matrix convergence / 误差、观测阶与工作量 |
| `cost_accuracy.csv` | 19 | Matched accuracy / 误差和匹配点工作量 |
| `rank_deficient.csv` | 1601 | Rank-deficient singular values / 秩亏数值与精确奇异值 |
| `stability_sweep.csv` | 39 | Nonlinear sweep / 扰动放大、能量、越过 1 与失败 |
| `trajectory.csv` | 401 | Resolved trajectory / 奇异值、能量、缺陷与区间残差 |
| `summary.json` | — | 软件、参数、谱、拟合阶、工作量、自适应与几何汇总 / Software, settings, spectra and diagnostics |

## Fields / 字段

### adaptive_steps.csv

```text
method, t_start, h, normalized_local_error
```

### convergence.csv

```text
method, n_steps, h, terminal_frobenius_error, observed_order, rhs_evaluations, jacobian_evaluations, newton_iterations
```

### cost_accuracy.csv

```text
method, n_steps, h, terminal_frobenius_error, rhs_evaluations, jacobian_evaluations, newton_iterations, matched_point
```

### rank_deficient.csv

```text
t, s1, s2, s3, exact_s1, exact_s2, exact_s3
```

### stability_sweep.csv

```text
method, h, n_steps, one_step_fast_perturbation_amplification, one_step_energy_change, max_energy_increase, singular_value_crossing, terminal_exact_error, status
```

### trajectory.csv

```text
t, s1, s2, s3, energy, exact_energy, orthogonality_defect, exact_orthogonality_defect, lyapunov_identity_residual_next_interval
```


## Interpretation / 解释

- terminal_frobenius_error / terminal_exact_error compare the full matrix
  with the finite-time exact SVD solution, not the limiting polar factor.
- observed_order 是相邻粗/细网格误差比的 log2；每方法首行无前一网格，留空。
- matched_point=True identifies starred cost points. RHS counts include Newton
  residual/backtracking evaluations and do not represent elapsed time.
- status=diverged_or_failed 表示运行未完成；空值/NaN 是未获得的量，不是零误差。
  单步已测得的量仍可保留。Failed runs retain available one-step measurements.
- lyapunov_identity_residual_next_interval 属于该行之后的区间，绘在中点；
  最后一行为空。附录 C 给出公式；缩放分母 max(1,|理论变化率|) 不是真正相对误差。
- normalized_local_error 是接受步的 step-doubling 局部估计，不超过 1；
  不是全局终点误差界。最后短步可能只为到达终点。
- exact_s1–exact_s3 是有限时间精确奇异值；秩亏零模态为排序后的第三列。

记录环境 / Recorded environment: Python 3.12.4, NumPy 1.26.4,
SciPy 1.13.1, Matplotlib 3.8.4. JSON records actual runtime versions.

在 Project1 下重建工作输出 / From Project1:

```powershell
python -B code/run_all.py
```

此命令只更新项目级 data/ 和 figures/，不修改已归档报告。
Manifest hashes and the version tag match the submitted data and figures.
