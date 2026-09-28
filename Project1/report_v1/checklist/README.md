# Topic ⑤ 代码交付 Checklist

复核日期：2026-09-27。本目录只记录**代码部分**的验收与验证证据。可运行测试已移至与 `code/` 平级的 [`../../test/`](../../test/)。依据为课程 `code_review_checklist.tex` 的 A–E 项、`submission_checklist.tex` 的代码与提交环境项、Topic ⑤ 原题和 `visualization_guide.tex`。团队姓名、AI Log、ICS、slides 不属于本清单。代码 ZIP 按现有分工暂缓，因此这里不把“最终提交包”标为完成。

## 文件与复现

| 位置 | 用途 |
|---|---|
| `../../code/` | 英文版模型、三种求解器、实验与一键入口 `run_all.py`。 |
| `../../code_zh/` | 中文注释版，独立运行并与英文版比较数值输出。 |
| [`../../test/test_validation.py`](../../test/test_validation.py) | 检查完整隐式残差 Jacobian、解析解、收敛阶、谱、能量、自适应与秩亏情形。 |
| [`../../test/test_bilingual_parity.py`](../../test/test_bilingual_parity.py) | 分别运行两版模型与求解器，比较输出。 |
| `../figures/` | 报告实际使用的八张 PNG，由英文入口重建。 |
| `../Section2Draft_v5.tex` | 数值结果、Newton 与自适应伪代码、有限差分检验的报告正文。 |

在 `Project1/` 下运行：

```powershell
python -m pip install -r requirements.txt
python code/run_all.py
python code_zh/run_all.py
python -B -m unittest discover -s test -v
```

本轮结果：**10/10 测试通过**；中英文入口均完成；三方法观测阶分别为 `1.010 / 3.927 / 1.014`；有限时间 SVD 与独立 Radau 的终点差为 `1.16×10⁻¹³`；报告八张图与英文入口重生的 PNG 逐个 SHA-256 一致。报告 PDF 为 29 页。

## Code-Review Checklist：A–E

| 条目 | 状态 | 可核对证据 |
|---|---|---|
| A1 一键端到端运行 | 通过 | `python code/run_all.py` 生成全部 CSV、JSON 和八张图。 |
| A2 README 说明依赖与运行 | 通过 | `../../README_EN.md`、`../../README_ZH.md` 和 `requirements.txt`。 |
| B1 RHS 与报告方程一致 | 通过 | `code/model.py` 中 `X(I-XᵀX)`；报告模型节采用同一方程。 |
| B2 参数可查找 | 通过 | `benchmark()`、`experiments.py` 的常数和各实验设置。 |
| B3 单位/尺度明确 | 通过 | 模型量无量纲；报告分析初始快模态与谱跨度。 |
| C1 显式 Euler 更新 | 通过 | `solvers.py` 使用 `y+h f(t,y)`。 |
| C2 RK4 四阶段 | 通过 | 两个半步阶段、终步阶段及 `1:2:2:1` 权重正确。 |
| C3 隐式 Euler 完整残差 | 通过 | Newton 解 `F(w)=w-y_n-hf(t_{n+1},w)=0`。 |
| C4 残差 Jacobian 与差分 | 通过 | `J_F=I-hJ_f`；`test/test_validation.py`（以 `Project1/` 为根） 对完整 `F` 做中心差分，误差 `3.68×10⁻¹⁰`，报告 Implementation 节记录设置。 |
| C5 自适应没有固定步伪装 | 通过 | `initial_step` 只是首个试探值，后续由误差调整。 |
| C6 误差估计实际控制步长 | 通过 | 归一化估计决定接受/拒绝及下一步缩放。 |
| D1 解析/高精度参考 | 通过 | 完整有限时间 SVD 解与独立 Radau 交叉核对。 |
| D2 观测阶支持声称 | 通过 | `convergence.csv` 和三条 log-log 曲线。 |
| D3 能量/几何诊断 | 通过 | `trajectory.csv` 检查耗散、奇异值和正交性。 |
| D4 稳定性主张有实证 | 通过 | 稳定域、冻结谱与非线性步长扫描共同支撑，并标明局部界限。 |
| E1 函数分工清楚 | 通过 | 模型、单步、固定/自适应驱动及实验分别命名。 |
| E2 求解器可替换 RHS | 通过 | `solve_fixed`、`solve_adaptive` 将 `f` 与 `jac` 作为参数。 |
| E3 常数有名称或注释 | 通过 | 自适应安全因子、步长缩放界及 Newton 回溯下限已命名。 |
| E4 注释解释原因 | 通过 | 列优先状态、有限时间参考及拒绝步重试的原因有说明。 |
| E5 无明显死代码 | 通过 | 人工检查四个核心模块，没有注释掉的旧实现或明显未用 import。 |

F. 本轮无未解决的 blocker/major/minor。此前 C4 报告缺差分证据与 E3 未命名常数已修复。G. 提交前优先项中的 C4、E3 和 `.gitignore` 构建产物规则均已完成。

## 题目及代码提交项

| 要求 | 状态 | 证据 |
|---|---|---|
| 三种方法、矩阵向量化与有限时间完整矩阵验阶 | 通过 | `model.py`、`solvers.py`、`convergence.csv`；列优先 `vec(X)`。 |
| 指定初值、区间、步长与容差可复现 | 通过 | `benchmark()`、`experiments.py`、报告第 3–4 节。 |
| 奇异值、Lyapunov 能量与大步数值失效 | 通过 | `trajectory_diagnostics.png`、`stability_sweep.png` 与对应 CSV。 |
| 平衡点中性/收缩方向及快瞬态 | 通过 | 报告线性化、`frozen_spectrum.png` 和非线性扫描。 |
| 秩亏初值与部分等距极限 | 通过 | `rank_deficient.png/.csv`。 |
| 对角初值标量 sanity check | 通过 | `test/test_validation.py`（以 `Project1/` 为根）。 |
| 环境梯度流与正交群切向投影区分 | 通过 | 报告第 2.1 节。 |
| README、相对路径、图可重生、忽略构建产物 | 通过 | 双语 README、`run_all.py`、`.gitignore`；八图哈希核对。 |
| 正式代码 ZIP | 暂缓 | 按当前分工暂不打包；不影响上述源码与数值检查结果。 |

## 八张图对应的检查

| 图 | 用途 |
|---|---|
| `convergence.png` | 三方法完整矩阵误差、理论阶与拟合阶。 |
| `stability_regions.png` | 三个标量稳定域、边界及 `h=0.08` 的初始谱点；`-26` 快模态在 Euler 域外。 |
| `frozen_spectrum.png` | 初始 Jacobian 谱和局部显式步长界。 |
| `stability_sweep.png` | 非线性快模态放大及终点误差对步长的响应。 |
| `adaptive_steps.png` | 步长加倍控制器的接受步长。 |
| `trajectory_diagnostics.png` | 奇异值、能量、正交性缺陷与 Lyapunov 残差。 |
| `cost_accuracy.png` | 相近误差下 RHS 调用数比较。 |
| `rank_deficient.png` | 零奇异值保持及部分等距极限。 |

作图指南的提交前十项已按代码和报告图核对：log-log 坐标、量与单位、结论式标题、理论参考线、可区分的颜色/线型、图例、caption、成本指标、固定文件名与 220 DPI 均满足。舍入极限的解释写在报告正文中。
