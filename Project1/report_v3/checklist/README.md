# report_v3：完整报告与代码 Checklist

复核日期：2026-10-03。依据：课程 code_review_checklist.tex 的 A–E 项、
submission_checklist.tex 的代码与运行环境项、Topic ⑤ 和 visualization_guide.tex。

本清单验收当前 v3 完整报告与代码交付。
报告现已包含 Sections 1--5、AI Transparency Log、ICS 和 Appendix C。
slides 与正式代码 ZIP 仍按小组最终提交安排处理。

## 文件与复现

| 位置 | 用途 |
|---|---|
| `../../code/`、`../../code_zh/` | 英文/中文注释的独立源码。 |
| [test_validation.py](../../test/test_validation.py) | 13 个模型、格式、谱、参考解、阶、几何、自适应和边界检查。 |
| [test_bilingual_parity.py](../../test/test_bilingual_parity.py) | 1 个独立子进程双语数值一致性检查，覆盖三方法。 |
| [VALIDATION_RUN_2026-10-03.md](VALIDATION_RUN_2026-10-03.md) | 当前 14 项测试、双语入口、环境版本和报告数值的独立复现记录。 |
| `../report.tex` | 编译完整报告的入口，包含 Abstract、Sections 1--5、References 和 Appendices A--C。 |
| `../figures/` | 本版八张 PNG。 |
| `../data/` | 本版六份完整 CSV 与 summary.json。 |
| `../manifest.json` | 报告、图、数据、代码与测试的 SHA-256。 |

在 Project1 下运行：

```powershell
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B code_zh/run_all.py
python -B -m unittest discover -s test -v
```

本轮 **14/14 测试通过**；两版入口均完成。观测阶 1.010 / 3.927 / 1.014
在报告显示精度内复现。新环境 SVD/Radau 终点差为 1.1680372e-13
（三位有效数字 1.17e-13），报告内置结果为 1.1613543e-13（三位有效数字
1.16e-13）；两者相差约 0.575%，数值接近且同属 1e-13 量级，但三位有效
数字并不相同。新环境中的两版六 CSV、JSON、八 PNG 一致；因依赖版本未锁定，
重生输出与报告内置图/数据的原始哈希不同。最终 `report.pdf` 已从最新 `main`
提交 `45f0a01`（包含验证合并 `b28fe39`）重编，仍为 32 页；Section 4.5 已显示
14 项测试及三项补充边界检查，目录与正文页码一致。详见本次独立复现记录。

## Code-Review Checklist：A–E

| 条目 | 状态 | 可核对证据 |
|---|---|---|
| A1 一键端到端运行 | 通过 | code/run_all.py 生成八图、六 CSV、JSON。 |
| A2 README 说明依赖和运行 | 通过 | README_EN.md、README_ZH.md、requirements.txt。 |
| B1 RHS 与报告一致 | 通过 | model.py 的 X(I−XᵀX)。 |
| B2 参数可查找 | 通过 | benchmark()、experiments.py 常数与 summary.json。 |
| B3 单位/尺度明确 | 通过 | 无量纲；理论分析快模态与谱跨度。 |
| C1 显式 Euler | 通过 | solvers.py 使用 y+h f(t,y)。 |
| C2 RK4 四阶段 | 通过 | 半步阶段、终步阶段与 1:2:2:1 权重。 |
| C3 隐式 Euler 完整残差 | 通过 | F(w)=w−y_n−h f(t_n+h,w)=0。 |
| C4 残差 Jacobian 和差分 | 通过 | I−hJ_f；test_validation.py 对完整 F 做中心差分，报告 3.4 记录检验设置。 |
| C5 实际自适应 | 通过 | initial_step 只是首个试探值，实际接受步长变化。 |
| C6 误差控制步长 | 通过 | 三方法 normalized E 控制接受/拒绝和下一步缩放。 |
| D1 精确/高精度参考 | 通过 | 有限时间完整矩阵 SVD 解与独立 Radau。 |
| D2 观测阶支持结论 | 通过 | convergence.csv、log-log 图；RK4 自动检验用 N=640/1280。 |
| D3 能量/几何诊断 | 通过 | trajectory.csv；三方法小步长趋近、不越过 1、能量单调测试。 |
| D4 稳定性有实证 | 通过 | 稳定域、冻结谱、非线性扫描；明确局部界不是全局保证。 |
| E1 分工清楚 | 通过 | model、单步/驱动、experiments、run_all 四模块。 |
| E2 可替换 RHS | 通过 | solve_fixed / solve_adaptive 传入 f 和 jac。 |
| E3 常数有名或注释 | 通过 | safety、缩放界、Newton 回溯下限等命名。 |
| E4 注释解释原因 | 通过 | 列优先、有限时间参考、失败与拒绝步处理。 |
| E5 无明显死代码 | 通过 | 四模块无注释掉的旧实现、明显未用 import。 |

E 类来自课程清单的可读性和结构要求；未增加生产系统维护、CI 或覆盖率门槛。
本次测试、哈希、数值表述修正及最终 PDF 重编后没有已知代码或报告 blocker；
报告整合改动仍须经正式 GitHub review 后再合并，不冒称已经完成审核。

## 题目与章节交付

| 要求 | 状态 | 证据 |
|---|---|---|
| 三方法、向量化、有限时间完整矩阵验阶 | 通过 | model.py / solvers.py；order='F'；convergence.csv。 |
| 指定初值、区间、容差和步长 | 通过 | benchmark、实验设置、报告第 3–4 节及 JSON。 |
| 奇异值、耗散和大步数值失效 | 通过 | trajectory / stability_sweep 图和 CSV。 |
| 中性切向、收缩法向及快瞬态 | 通过 | 理论 2.3.5、初始谱、冻结谱图和扫描。 |
| 秩亏零模态和部分等距极限 | 通过 | rank_deficient 图/CSV；测试非零模式和极限矩阵误差。 |
| 对角初值 sanity check | 通过 | test_validation.py。 |
| 环境梯度流和切向投影区分 | 通过 | 理论 2.3.5。 |
| 第 2 节与实现对应 | 通过 | section2.tex：残差/单步值区分、Newton、RK4 稳定证明、正则性。 |
| 第 3 节算法与源码一致 | 通过 | section3.tex：输出路径、参数、失败处理、Algorithm 2。 |
| 第 4 节数值内容完成 | 通过 | section4.tex：实际测量和十四项验证；不是占位。 |
| 附录 C 完整纳入截图数据 | 通过 | appendix_c.tex；六 CSV + JSON 的字段、行数、图映射和摘录。 |
| 双语说明、相对路径、可重生图片 | 通过 | 两版 README；每个源码和每张图都有解释。 |
| source only 目录要求 | 通过 | 输出移到项目级 figures/data 和 outputs_zh；忽略缓存/工作 PNG。 |
| 保留 report_v1 | 通过 | 逐文件 SHA-256 未变；版本索引与标签恢复完整旧项目。 |
| 第 1、5 节与团队材料 | 通过 | Section 1、Section 5、AI Log 和 ICS 已纳入当前 v3 报告。 |
| 正式代码 ZIP | 暂缓 | 按用户要求暂不打包。 |

伪代码位置：`../sections/section2.tex` 的 Algorithm 1（Newton）；
`../sections/section3.tex` 的 Algorithm 2（step doubling）。

## Visualization Guide：逐图复核

| 图 | 用途 | 本次核对 |
|---|---|---|
| convergence.png | 完整矩阵误差与理论/拟合阶 | log-log、理论斜率、描述性回归带；标出最细网格接近舍入量级。 |
| stability_regions.png | 三方法解析标量稳定域 | 边界、图例、h=0.08 的初始谱；正模态是物理增长。 |
| frozen_spectrum.png | 初始谱与局部截止 | 明确纵轴是步长分类，非虚部；截止点不是全局界。 |
| stability_sweep.png | 非线性放大与终点误差 | 误差—步长面板改成 log-log；失败行仍保留 CSV。 |
| adaptive_steps.png | 接受步长 | 三方法可区分；短末步不误解释为新增刚性。 |
| trajectory_diagnostics.png | 奇异值、能量、缺陷、残差 | 连续精确参照；残差补明确图例，有限时间缺陷不应为零。 |
| cost_accuracy.png | 相近误差下成本 | 双对数；误差匹配、星号、RHS 次数与 Newton 成本说明。 |
| rank_deficient.png | 零模态与非零模态极限 | 虚线精确曲线，解释部分等距。 |

共同适用项：坐标量/无量纲单位、结论式标题、理论参考、可区分颜色/线型、
图例、caption、明确成本指标、稳定文件名、220 DPI 均已核对。
确定性回归带不是误差概率区间；未观测到舍入平台，因此不声称已有平台。

v1 历史清单曾写全部符合；v2 复查发现误差—步长坐标和残差图例两项遗漏，
已经修复。v1 和 v2 历史材料保持不变。当前 v3 报告已完成 Sections 1--5
与 Appendices A--C 的整合。最终 PDF 页数为 32。

## 数据、版本与修改记录

- [convergence.csv](../data/convergence.csv)
- [cost_accuracy.csv](../data/cost_accuracy.csv)
- [stability_sweep.csv](../data/stability_sweep.csv)
- [trajectory.csv](../data/trajectory.csv)
- [adaptive_steps.csv](../data/adaptive_steps.csv)
- [rank_deficient.csv](../data/rank_deficient.csv)
- [summary.json](../data/summary.json)
- [数据说明](../data/README.md)
- [修改记录](../CHANGELOG.md)
- [版本索引](../../notes/REPORT_VERSIONS.md)
