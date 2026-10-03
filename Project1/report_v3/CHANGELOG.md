# report_v3 修改记录 / Revision record

日期：2026-10-03。

## v3 整合与完善

- 将原 `report_v2` 的 Sections 2--4 和 Appendix C 整合到完整报告。
- 新增 Section 1（Background），补充项目背景、极分解、梯度流和数值研究动机。
- 新增 Section 5（Conclusions），汇总收敛、稳定性、自适应、计算成本、
  几何性质和秩亏实验的主要结果。
- 新增 Abstract，并将完整报告结构统一为 Sections 1--5。
- 新增 Appendix A（AI Transparency Log）。
- 新增 Appendix B（Individual Contribution Statements, ICS）。
- 保留并更新 Appendix C（Supplementary Figures and Data）。
- 将 References 和 Appendices 加入目录。
- 更新 `report.tex`，使其成为完整报告的统一编译入口。
- 当前完整报告包含 Abstract、Sections 1--5、References 和 Appendices A--C。
- 当前编译后的 `report.pdf` 共 32 页。

## v3 文档与版本整理

- 新建并更新 `report_v3/README.md`，说明当前完整报告的文件结构、
  八张图和编译/复现方式。
- 更新项目根目录 `README.md`，将 `report_v3/` 设为当前完整报告。
- 更新 `README_EN.md` 和 `README_ZH.md` 中的当前报告路径和版本说明。
- 更新 `checklist/README.md`，补充 Section 1、Section 5、AI Log 和 ICS
  已纳入 v3，并更新 PDF 页数。
- 更新 `notes/REPORT_VERSIONS.md`，将 v3 记录为当前完整报告版本。
- `report_v1/` 和 `report_v2/` 继续保留为历史快照。
- `manifest.json` 将在 v3 文件最终冻结后重新生成，以更新页数和 SHA-256。
- `report-v3` Git 标签将在最终版本确定后再建立。

## v3 数值内容

- Topic ⑤ 模型和三种数值方法未改变。
- 保留 Explicit Euler、经典 RK4 和带阻尼 Newton 的 Implicit Euler。
- 保留有限时间 SVD 精确解和 SciPy Radau 独立参考解。
- 保留原有八张图、六份 CSV 和 `summary.json`。
- 保留原有收敛、稳定性、自适应、成本、几何和秩亏实验结果。
- 从旧 PR #1 按当前目录迁移容差敏感性、大步长奇异值越界和 Newton
  失败后缩步重试三项边界测试；没有恢复旧版测试路径。
- 14 项测试全部通过；中英文入口在新环境中均完成。
- 新增 [2026-10-03 独立复现记录](checklist/VALIDATION_RUN_2026-10-03.md)，
  记录实际环境、命令、关键数字、图表/CSV 对应关系及版本差异。
- Section 4 源码中的验证数量已更新；现有 32 页 PDF 未在本次代码验证环境中重编，
  最终提交前需由报告整合者编译更新后的源码。
- 观测收敛阶保持为 1.010 / 3.927 / 1.014。
- SVD/Radau 终点差保持为 1.16e-13。
- 三项补充测试没有改变报告中的数值实验结果。

---

## v2 历史记录 / Previous v2 record

日期：2026-09-28。基线：Git `371cb73` 和保留的 `report_v1`。

### 交付范围与理论

- v2 只交付第 2、3、4 节和附录 C，拆成独立章节供整合；当时未写第 1、5 节。
- 原样保留 `report_v1`；v2 未更新 slides，代码 ZIP 按当时分工暂缓。
- 第 2 节继承 v1 已修正的隐式 Euler：精确端点代入格式得到残差，
  隐式单步值是残差方程的根，通过逆映射分析联系两者。
- Newton 使用完整残差和 `I-hJ_f`，只接受残差下降的候选；阈值、初值、
  回溯及固定/自适应失败处理与代码对应。
- 保留 RK4 负实轴稳定区间详细证明、局部光滑性/有界导数条件、
  平衡点切向/法向分析；不把冻结谱写成全局稳定保证。
- 第 3 节更新实现路径与复现；第 4 节更新实际结果、秩亏数值和验证覆盖。
- Newton 伪代码：`sections/section2.tex`，Algorithm 1。
- 自适应伪代码：`sections/section3.tex`，Algorithm 2。
- 补充 Higham 极分解背景引用，没有更换 Topic ⑤ 模型或三个方法。

### 附录 C

- v2 的 `data/` 保存六份完整 CSV 和 `summary.json`。
- 提供文件—图映射、行数、逐列定义、缺失值、排序约定、数值摘录、
  软件环境、复现命令与版本溯源；长轨迹完整放 CSV，PDF 放可读摘录。

### 作图指南修复

- 稳定性扫描的误差—步长面板改为 log-log。
- Lyapunov 残差面板补明确图例。
- RK4 最细网格标注接近舍入量级，不声称已观测到平台。
- 八图保留单位、理论参考、caption 和 220 DPI。
- v1 历史清单不改；v2 对其“全部符合”结论补记上述两项遗漏。

### 验证补充

- 自适应和双语测试覆盖三方法；新增三方法小步长的奇异值趋近 1、
  不越过 1 与能量单调检查；秩亏测试补非零模态与部分等距极限检查。
- RK4 自动验阶使用 `N=640/1280`，避开最细实验网格的舍入风险。
- 11 项测试通过，两版入口完成；六 CSV、JSON 与八 PNG 的双语输出一致。
- 六份 CSV 与 v1 数值证据相同；观测阶保持为 1.010 / 3.927 / 1.014。
- SVD/Radau 终点差保持为 1.16e-13。

### 仓库整理

- 输出移出 `code/` 与 `code_zh/`；源码目录只放代码。
- 工作图位于 `figures/`，数据位于 `data/`；中文输出位于 `outputs_zh/`。
- 正式图和数据随 `report_v2/` 保存；测试保留在与 `code/` 平级的 `test/`。
- 旧 report 草稿与历史审查移到 `notes/archive/`。
- 版本索引与 manifest 对应 v2；`report-v1` 和 `report-v2`
  标签分别指向对应项目状态。
- `report_v1` 文件保持未修改。

页数、复现命令与验收证据见 [checklist](checklist/README.md)。
