# Project 2 最新检查清单（2026-11-15）

依据用户提供的 `Project2/checklist/` 中五份 TeX：submission checklist、
visualization guide、code review checklist、report template、problem definition sheet。
补充核对了本地课程 `problem_pack.pdf` 第5–7页 Direction 3 和深度比较要求。
这是本次实际检查记录，不代替成员签署、课程提交记录或教师评分。

## 分支合并

- [x] 合并 `meichen/report-source-and-review`（8753c9c），包含
  `meichen/p2-appendix-fixes`（8fbf619）的提交。
- [x] 保留 main 新版网格、颜色、成本容差及五人 ICS；没有用旧图片覆盖。
- [x] 接入理论修订、limitations、AI 审计摘录和 canonical theory checks。
- [x] 修正新限制段落中“界面未经过网格边内部”的不准确说法：FDM界面确实平分网格边。
- [x] 旧 testing-validation / Project1 分支未整支合入：它们不是此次新P2改动。

## 截图任务 A1–A4、B1–B4

- [x] A1：`fig03_accuracy_cost.pdf` 成本面板标明 Jacobi-CG rtol=1e-12、atol=0。
- [x] A2：`fig04_interface.pdf` 保留 signed error，色标关于0对称并含正负值。
- [x] A3：`fig07_mesh.pdf` 展示实际FDM点与FEM单元边，标明 x=1/2。
- [x] A4：蓝=FDM、橙=FEM、紫=Interface PINN；绿/洋红=调和/算术面。
  曲线增加线型或点型区分；种子及反差采用灰度，不复用方法配色。
- [x] B1：fig08/fig09 保持文件名；PDF为矢量，PNG为300dpi阅读预览。
- [x] B2：`code/run_all.py` 调用 PINN 重算和绘图，所有外部图均可重建。
- [x] B3：§5.3增加三种子单网络消融表。共同采样相对误差约0.310对3.12e-5；
  明确8,577对17,154参数，不宣称参数匹配或复现论文架构。
- [x] B4：§5.4明确路径相对于`project2/report/`，重算覆盖6个checkpoint；
  附录C引用`project2/report/support/verify/`，目录及脚本均实际存在。

## 报告 / Submission checklist

- [x] 标题页含组名、五人姓名与学号；PDF超过8页。
- [x] PDE、单位方形区域、四边Dirichlet数据、离散格式、边界消元和索引已写明。
- [x] 光滑算例四网格、具名误差范数及拟合阶；代数残差、容差扫描与LU参照齐全。
- [x] 分层算例区分调和/算术面，并同时报告精确通量误差、两侧重构跳跃及边界极值。
- [x] FDM/FEM深度比较匹配光滑问题、h、DOF、共同范数与求解容差；分开报告成本。
- [x] AI Log、五人ICS、文献、可信库边界及方法局限已包含。
- [x] 参考路径的文件实际存在；新增矩阵验证从生产组装器导入。
- [ ] ICS签名、日期及Jingyan原稿注释中的DRAFT身份，仍需本人确认。
- [ ] 课前Problem Definition Sheet及个人课程平台提交记录，未提供；不补写为已完成。
- [ ] 最终演示PDF与本次报告版本的一致性、10分钟时长：本次未重新验收。

## 代码 / Code review checklist

- [x] 在本机`dl`环境实际跑通`python -B code/run_all.py`，无需GPU、无需改路径。
- [x] 默认保留归档计时；`--recompute`可重新求解经典实验；不把checkpoint回放说成重训。
- [x] `requirements.txt`及README解释依赖、命令、每张图来源与LaTeX构建方式。
- [x] 生产微测试7/7通过；独立默认测试8通过、3跳过；严格回归10通过、1跳过。
- [x] 严格检查先暴露10个失败子项，再修复：非有限系数检查、稳定调和平均、
  单对角结构诊断、最大特征值初向量。原失败日志和通过日志均保留。
- [x] 仅刷新9行conditioning的特征值/残差列；保留原计时和CG计数，重画关联图。
- [x] 三个理论检查实际运行，矩阵表的对称缺陷为0、最小特征值及Cholesky均吻合。
- [x] 稀疏组装、边界正号、网格向量映射、固定随机种子、组装/求解/验证分离有代码证据。
- [x] `.gitignore`覆盖缓存及LaTeX中间文件；脚本路径由`__file__`定位，不要求固定盘符。
- [ ] 课程题库测试本次未重跑：未找到老师的`test_problem_bank.py`，严格运行明确跳过1项。
  历史题库结果单独保留，不当成本次新运行证据。
- [ ] 独立新机器从零安装尚未实测；这里只认证当前dl环境的执行。
- 不适用：Neumann/Robin闭合、MEMS可行性与Jacobian审计，本方向四边均为Dirichlet且为线性PDE。

## 图 / Visualization guide

- [x] 九张外部PDF的嵌入图像数量均为0；文字、曲线、矩阵块和误差色块均为矢量。
- [x] 九张PNG均约300dpi；矢量PDF本身不受像素DPI限制。
- [x] 图文件名无时间戳；LaTeX `includegraphics`全部引用PDF。
- [x] 原生TikZ网络图直接由LaTeX构建，不是截图。
- [x] 收敛图为log-log数据点，标明拟合阶和范数，增加最细三网格回归线。
- [x] 残差图有log轴和停止准则横线；成本图容差、图例和色标齐全。
- [x] 本次仅渲染与合并、消融和图修改相关的页面，没有逐页重查全文。

## 证据与交付

- `evidence/reproduction.txt`：统一入口及7个微测试。
- `evidence/independent_tests.txt`：默认独立测试，含跳过原因。
- `evidence/strict_tests_initial.txt` / `strict_tests.txt`：修复前后严格回归。
- `evidence/conditioning_refresh.txt`：仅刷新谱估计。
- `evidence/interface_order.txt`、`stability.txt`、`matrix_evidence.txt`：三项理论检查。
- `evidence/artifact_check.json`：图的矢量、DPI、路径、归档哈希及AI摘录哈希。
- `evidence/checklist_sources.json`：本次使用的课程清单文件SHA-256。
- `report/Method.pdf`：本次修订报告；源码仍以`report/Method.tex`为入口。
- [x] 代码提交压缩包另存本地交付目录`Project2_Code.zip`，含README、源码、
  数据及checkpoint；ZIP完整性及关键入口文件已检查，不把ZIP反复嵌入仓库。

结论：合并与技术修订已完成；签署、课程题库新运行、演示一致性及新机器安装等
未确认项目保留为空，不宣称课程所有提交项均已完成。
