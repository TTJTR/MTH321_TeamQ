
# MTH321 Project 1：极分解因子梯度流代码说明

## 安装与运行

使用 Python 3.10 或更新版本，在 `Project1` 目录运行：

本次记录的结果使用 Python 3.12.4、NumPy 1.26.4、SciPy 1.13.1 和
Matplotlib 3.8.4 生成。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -B code/run_all.py
.venv\Scripts\python -B code_zh/run_all.py
.venv\Scripts\python -B -m unittest discover -s test -v
```

英文入口把八张 PNG 写到项目级 `figures/`，把六份 CSV 和
`summary.json` 写到 `data/`。中文入口使用独立的
`outputs_zh/figures/` 和 `outputs_zh/data/`。

两个源码目录只放代码；运行入口不会覆盖已归档报告。
两版保留相同的函数名、数据列名和英文图标签，便于核对并放入英文报告。
`summary.json` 记录运行时 Python 和依赖库版本。

## 数学模型与验证基准

题目 ⑤ 指定的 3×3 矩阵初值问题为：

```text
X'(t) = X(t) [I - X(t)^T X(t)]
X(0)  = R(0.4) diag(0.2, 1.4, 3) R(-0.7)^T .
```

求解器使用**列优先**展开的状态向量 `vec(X)`（`order='F'`），自行实现
显式 Euler、经典 RK4 和带阻尼 Newton 的隐式 Euler。有限时间精确矩阵
由初值 SVD 重建：

```text
X_exact(t)=U diag(s_i(t)) V^T
```

其中

```text
s_i(t)=s_i(0)/sqrt(s_i(0)^2+[1-s_i(0)^2]exp(-2t))
```

精确解只用于**测量误差**，不参与任何数值步的推进。SciPy 的
`solve_ivp(method='Radau')` 只做独立交叉验证，不是被比较的三种方法之一。

## 每个源码文件做什么

| 文件 | 用途 |
|---|---|
| `code/model.py` | 构造指定初值和秩亏初值；在矩阵和列优先状态之间转换；计算方程右端、Fréchet 导数和解析 Jacobian；重建有限时间 SVD 精确解；计算奇异值、Lyapunov 能量/变化率及正交性缺陷。 |
| `code/solvers.py` | 实现三种单步方法、隐式 Euler 的阻尼 Newton、固定均匀网格积分和步长加倍自适应积分；统计 RHS/Jacobian 调用、Newton 更新及拒绝步。 |
| `code/experiments.py` | 执行所有数值实验，生成八张图、六份 CSV 数据及机器可读的结果摘要。 |
| `code/run_all.py` | 英文版命令行入口；调用全部实验并打印拟合收敛阶与独立参考解差异。 |
| `code_zh/model.py` | `code/model.py` 的中文注释、独立运行版本。 |
| `code_zh/solvers.py` | `code/solvers.py` 的中文注释版本，数值行为一致。 |
| `code_zh/experiments.py` | `code/experiments.py` 的中文注释版本，由入口分别传入图片和数据输出目录。 |
| `code_zh/run_all.py` | 中文版命令行入口。 |
| `test/test_validation.py` | 核对解析 Jacobian 与有限差分、初始及平衡态完整谱、能量恒等式、对角初值标量 sanity check、SVD/Radau 结果、三方法收敛阶、自适应行为、秩亏情形、容差敏感性、大步长奇异值越界及 Newton 缩步重试。 |
| `test/test_bilingual_parity.py` | 分别运行中英文源码并比较模型、固定步和自适应输出。 |
| `report_v3/checklist/README.md` | 验收清单、证据、图片对应关系和复现命令。 |
| `report_v3/checklist/VALIDATION_RUN_2026-10-03.md` | 当前 14 项测试的干净环境运行与复现记录。 |
| `report_v3/sections/section1.tex` | Background：项目背景、极分解梯度流与研究动机。 |
| `report_v3/sections/section2.tex` | 理论和 Newton 伪代码（Algorithm 1）。 |
| `report_v3/sections/section3.tex` | 实现和自适应伪代码（Algorithm 2）。 |
| `report_v3/sections/section4.tex` | 数值实验、结果和验证覆盖。 |
| `report_v3/sections/section5.tex` | Conclusions：主要数值结果、稳定性、成本比较与限制总结。 |
| `report_v3/appendices/appendix_a.tex` | AI Transparency Log。 |
| `report_v3/appendices/appendix_b.tex` | Individual Contribution Statements（ICS）。 |
| `report_v3/appendices/appendix_c.tex` | 数据/图对应、字段字典、数值摘录与复现说明。 |
| `notes/REPORT_VERSIONS.md` | 报告版本、Git 标签和恢复说明。 |
| `requirements.txt` | 列出 NumPy、SciPy、Matplotlib 三项依赖。 |
| `CODE_HANDOFF.md` | 供报告第 3–4 节使用的具体数字和解释。 |
| `report_v3/report.tex` | 当前完整报告的 LaTeX 编译入口，包含 Abstract、Sections 1--5、References 和 Appendices A--C。 |
| `report_v3/CHANGELOG.md` | 记录 v3 的整合、修改和验证情况。 |
| `slides/Topic5_presentation.tex` | 演示文稿源码；对应 PDF 位于 `slides/`。 |

## `figures/` 中每张图是什么

英文运行的八张工作图位于 `figures/`，对应 CSV/JSON 位于 `data/`；
中文输出位于 `outputs_zh/`。

当前完整报告保存的八张图位于 `report_v3/figures/`，
六份完整 CSV 和 `summary.json` 位于 `report_v3/data/`，
因此无需先运行 Python 即可编译报告。

附录 C 解释文件—图对应、每列的含义、缺失值和数值摘录。
`report_v1/` 和 `report_v2/` 原样保留，作为历史报告快照。

| 图片 | 含义及对应数据 |
|---|---|
| `convergence.png` | 三个双对数面板展示终点**完整矩阵 Frobenius 误差**、理论 `h¹`/`h⁴` 参考斜率、拟合直线及 95% 回归带。`convergence.csv` 包含步数、步长、误差、相邻网格观测阶和工作量。RK4 仅用最细的三个网格拟合。回归带只是确定性网格数据的描述性最小二乘诊断，不代表 ODE 误差的概率区间。 |
| `cost_accuracy.png` | 三种方法在多个固定网格上的**实际误差—RHS 调用次数**双对数曲线。星号标出误差约 `9×10⁻⁴` 的三个匹配点，灰带覆盖它们的实际误差。`cost_accuracy.csv` 包含全部绘图点、`matched_point` 标记、步数、RHS/Jacobian 调用和 Newton 更新次数。 |
| `stability_regions.png` | 分别显示三种方法满足 `|R(hλ)|≤1` 的解析标量稳定域，并叠加 `h=0.08` 时的初始 Jacobian 谱：叉号为收缩模态，空心圆为物理增长模态。此图没有单独 CSV。 |
| `frozen_spectrum.png` | 初始 9×9 Jacobian 的特征值乘以 `h=0.05` 和 `h=0.10`，对照 Euler 与 RK4 负实轴截止点。两行标明步长，纵向位置不是特征值虚部；正特征值 `+0.88` 是最小奇异值真实增长。数字见 `summary.json`。 |
| `stability_sweep.png` | 左图为初始最快方向小扰动经过一个非线性步后的放大倍数，右图为不同固定步长的终点精确矩阵误差。`stability_sweep.csv` 还含能量变化、奇异值越过 1 与失败状态。冻结 Jacobian 截止点只是**局部诊断**，不是全局非线性稳定保证。 |
| `trajectory_diagnostics.png` | 四幅轨迹图：奇异值和精确曲线、数值与精确 Lyapunov 能量、数值与精确的有限时间正交性缺陷、离散 Lyapunov 恒等式残差。`trajectory.csv` 保存轨迹及每一行之后时间区间对应的残差。 |
| `adaptive_steps.png` | 三种步长加倍求解器实际接受的步长。`adaptive_steps.csv` 含每步起点、步长和归一化的**估计局部误差**。最后一小步也可能只是为了准确落在 `t=2`。 |
| `rank_deficient.png` | 首个初始奇异值为零时的数值轨迹和虚线精确曲线。`rank_deficient.csv` 保存 `[0,8]` 上的两组数据；零模态维持在浮点误差量级，极限为部分等距矩阵。 |

`summary.json` 汇总区间、软件版本、全部实验参数、拟合阶数、
初始和平衡态特征谱、局部稳定步长估计、匹配精度成本、
自适应统计及秩亏诊断。

`stability_sweep.csv` 中的 `status=diverged_or_failed`
表示大步长运行未完成；该行的空值或 `nan` 不代表零误差。

## 可复现参数与结果解释

| 实验 | 参数 |
|---|---|
| 主基准 | `t∈[0,2]`；初始奇异值 `(0.2,1.4,3)`。 |
| 固定步长收敛阶 | Euler 和隐式 Euler：`N=40,80,160,320`；RK4：`N=40,80,160,320,640,1280,2560`。参考值是**有限时间完整矩阵**，不是极限正交因子。 |
| Newton | 从上一个已接受状态初始化。残差停止条件 `||F(w)||∞≤10^-12(1+||w||∞)`；回溯要求候选残差下降。固定网格失败会报错，自适应积分才从上个已接受状态以半步长重试。 |
| 独立参考解 | SciPy Radau：`rtol=10^-12`、`atol=10^-14`。 |
| 自适应积分 | 初始试探 `h=0.15`，`atol=10^-8`、`rtol=10^-6`；比较一个全步和两个半步，归一化估计不大于 1 时接受细步结果。这样做不提高基础方法的阶数，也不证明全局误差或稳定性。 |
| 轨迹和秩亏 | RK4 在 `[0,2]` 用 `N=400`；秩亏初始奇异值 `(0,1.4,3)`，在 `[0,8]` 用 `N=1600`。 |
| 匹配精度成本 | Euler、RK4、隐式 Euler 分别用 `N=(160,17,160)`。实际终点误差约为 `(9.21,8.85,9.32)×10^-4`，最大差异不到 6%；RHS 调用为 `(160,68,862)`。 |

本模型无量纲；重新生成的 PNG 均为 220 DPI。

多方法共用坐标轴时，颜色同时配有不同标记或线型。
成本图只统计 RHS 调用；Jacobian 调用和 Newton 更新另列在 CSV。
它没有统计 Jacobian 组装、线性代数分解、Python 开销和绘图，
因此不能直接当作墙钟时间排名。

Lyapunov 残差图使用数值轨迹上的能量有限差分及中点处连续理论变化率；
非零残差反映离散误差。摘要中的“缩放残差”
以 `max(1, |变化率|)` 为分母，**不是严格的相对误差**。

## 当前报告与版本

`report_v3/report.pdf` 是当前整合后的完整报告，包含：

- Abstract
- Sections 1--5
- References
- Appendix A: AI Transparency Log
- Appendix B: Individual Contribution Statements
- Appendix C: Supplementary Figures and Data

14 项验证测试全部通过，包括三项新增边界检查、三种方法的自适应积分与
中英文源码数值一致性检查。详见
[2026-10-03 复现记录](report_v3/checklist/VALIDATION_RUN_2026-10-03.md)。

此前的 `report_v1/` 和 `report_v2/` 保留为历史报告快照。

当前 v3 的 `checklist`、`CHANGELOG`、版本索引和 `manifest.json`
应在最终文件确定后统一更新，以保证版本说明、页数和 SHA-256 一致。

版本与恢复说明见 [版本索引](notes/REPORT_VERSIONS.md)。
