# Topic 5 report / 题目 ⑤ 报告

`Section2Draft_v5.tex` is the report source. Its `\graphicspath` points to
`figures/` in this folder; the eight PNGs are the actual outputs of
`../code/run_all.py`, saved at 220 DPI. Compile from this directory with
`pdflatex Section2Draft_v5.tex` (run twice for references). The matching
compiled PDF is `Section2Draft_v5.pdf`.

`Section2Draft_v5.tex` 是报告 LaTeX 源码；图片路径指向本目录的 `figures/`。
八张 PNG 均由 `../code/run_all.py` 生成，分辨率为 220 DPI。在本目录连续
运行两次 `pdflatex Section2Draft_v5.tex` 可重建 PDF。

| Figure | Purpose / 用途 |
|---|---|
| `convergence.png` | Full-matrix error, theoretical orders and fitted lines / 完整矩阵误差、理论阶与拟合线 |
| `stability_regions.png` | Three scalar absolute-stability regions / 三种方法的标量绝对稳定域 |
| `frozen_spectrum.png` | Initial Jacobian spectrum against local explicit-step limits / 初始 Jacobian 谱与局部显式步长界限 |
| `stability_sweep.png` | Nonlinear fast-mode amplification and terminal error versus step size / 非线性快模态放大与终点误差 |
| `adaptive_steps.png` | Accepted step sizes under step doubling / 步长加倍算法接受的步长 |
| `trajectory_diagnostics.png` | Singular values, energy, orthogonality and Lyapunov residual / 奇异值、能量、正交性与 Lyapunov 残差 |
| `cost_accuracy.png` | Achieved full-matrix error versus measured RHS calls / 实际矩阵误差与 RHS 调用成本 |
| `rank_deficient.png` | Rank-deficient singular values versus exact solution / 秩亏奇异值与精确解 |

For each code file, numerical settings, CSV columns and interpretation, see
[English README](../README_EN.md) or [中文 README](../README_ZH.md).

Team names/IDs, the final AI Transparency Log and one ICS per member are
intentionally pending team completion before final course submission.
团队姓名学号、完整 AI 使用记录和每位成员的 ICS 仍须由小组据实填写。
