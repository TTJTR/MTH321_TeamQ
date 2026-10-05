# Gauss IRK4 独立验证记录（2026-10-05）

## 验证对象

- 独立执行基线：`main` 提交 `58d691d4c7f7d737774111b8d1c3da7bd7ba011c`。
- 用户收到的压缩包：`code_advanced.zip`，SHA-256
  `57ad65ead1f8c6d6ef23a861c583951ea301bb41392cbb16ad0ddedca47aaa91`。
- 外部 `REPORT_PATCH_ZH.md` 与压缩包内同名文件逐字节相同，SHA-256
  `fd8cc674f1416a4489f9098a4a971a44ae32689d349cbba354386dbbc20b0674`。
- 压缩包共五个普通文件，无绝对路径、`..` 路径穿越、符号链接或加密条目。

验证时发现，最新 `main` 已包含该扩展的后续版本：核心
`gauss_irk4.py` 与收到的版本一致；测试由 3 项扩充到 6 项，成本图增加
RK4 `N=75` 与 Gauss IRK4 `N=64` 的近似等误差比较。远端随后删除了临时的
Section 5 交接文档，因此本次验证以最新 `main` 为准，没有恢复较早的报告
补丁，也没有用旧文件覆盖新版本。

## 环境

- Windows，Python 3.12.14
- NumPy 2.5.3
- SciPy 1.18.1
- Matplotlib 3.11.2

## 命令与结果

从 `Project1/` 运行：

```text
python -B -m unittest discover -s code_advanced -p "test_*.py" -v
python -B -m unittest discover -s test -v
python -B code/run_all.py
python -B code_zh/run_all.py
python -B code_advanced/run_comparison.py
```

结果：

- Gauss IRK4 扩展测试 **6/6 通过**。
- 原项目测试 **14/14 通过**。
- 英文、中文基础入口均以退出码 0 完成。
- 四方法比较脚本以退出码 0 完成，并生成四张 PNG、两份 CSV 和一个 JSON。
- 脚本只写入 `figures/advanced_irk4/` 与 `data/advanced_irk4/`；原基础代码和
  测试文件未被扩展代码修改。

## 独立数值核对

本环境重算的拟合阶为：

| 方法 | 拟合阶 |
|---|---:|
| Explicit Euler | 1.010116 |
| Explicit RK4 | 3.927450 |
| Implicit Euler | 1.013681 |
| Gauss IRK4 | 3.967392 |

近似等误差对照为：

- Explicit RK4，`N=75`：终点误差 `5.0944288e-8`，300 次 RHS。
- Gauss IRK4，`N=64`：终点误差 `5.0789800e-8`，720 次 RHS、264 次
  Jacobian、132 次 Newton 更新。

两者误差相差约 0.30%，但 Gauss 的工作量统计还不包括 18×18 线性系统的
组装与分解，因此不能据此声称实际运行时间更优。

在 `z=-26(0.08)=-2.08` 处，四种方法的放大因子绝对值分别为
`1.0800`、`0.3633`、`0.3247`、`0.1335`。对左半平面的独立网格抽查得到
Gauss `max |R(z)| = 1 + 2.2e-16`（舍入量级），而
`|R(-1e8)|=0.99999988`，与“A 稳定但非 L 稳定”一致。

其余交叉核对：

- Gauss `N=64` 的终点 Frobenius 误差为 `5.0789800e-8`。
- 精确 SVD 终值与独立 Radau 终值之差为 `1.1680372e-13`。
- 18 维耦合阶段块 Jacobian 的有限差分方向误差为 `2.91e-9`。
- 共同 `h=0.1` 网格上，四种方法各 21 个已采样能量值均逐步下降。
- 限制 Newton 迭代次数时，求解器按预期抛出 `StageFailure`，没有返回未收敛阶段。

不同 NumPy/Matplotlib 环境会使末位浮点数和 PNG 字节哈希不同；本次重生值与
仓库快照在报告所用精度上一致，但不应宣称跨环境逐字节一致。若最终提交要求
完全相同的文件哈希，应固定依赖版本后重新生成全部高级数据和图片。

## 验收结论与边界

**通过。** 当前高级方法代码、测试和数据口径相互一致，可以保留在项目中作为
可选高级方法扩展。仍需保持以下边界：

- Gauss IRK4 目前只有固定步长，没有自适应控制。
- A 稳定性是标量线性测试方程性质，不是非线性全时段稳定性证明。
- `1e-12` 是阶段残差阈值，不是全局解误差保证。
- 本记录提交前，`main` 已通过后续提交把 Gauss IRK4 高级方法章节和对应图片
  整合进 `report_v3`；该后续整合没有改动本次验证的 `code_advanced` 代码。
  本记录只证明上述代码与数值结果通过独立复核，不等同于对整份报告内容、
  排版或清单哈希的再次审计。
