# Advanced comparison: fourth-order implicit Runge--Kutta / 高级方法比较

This folder is an **optional, separate extension**. It imports the original
model and three solvers from `../code/`, but does not edit or overwrite them.
It writes only to `../figures/advanced_irk4/` and `../data/advanced_irk4/`.
The integrated report `report_v3/` is unchanged.

本目录是**独立的可选扩展**：调用 `../code/` 的原模型和三种方法，不覆盖原代码。
运行结果只写入 `../figures/advanced_irk4/` 与 `../data/advanced_irk4/`，
不修改 `report_v3/`。

## Method / 方法

“Implicit RK4” here means the **two-stage, fourth-order Gauss--Legendre
implicit Runge--Kutta method**, not a four-stage implicit version of classical
explicit RK4. The two stages are solved together by damped Newton on an
18-dimensional system for the 9-dimensional vectorised matrix state.

这里的“隐式 RK4”明确指**两阶段、四阶 Gauss--Legendre 隐式 Runge--Kutta 法**。
每一步同时求解两个 9 维阶段状态，故 Newton 线性系统为 18 维。

The Butcher tableau is

```text
1/2 - sqrt(3)/6 | 1/4                 1/4 - sqrt(3)/6
1/2 + sqrt(3)/6 | 1/4 + sqrt(3)/6   1/4
----------------+---------------------------------------
                | 1/2                 1/2
```

The scalar stability function is
`R(z)=(1+z/2+z²/12)/(1-z/2+z²/12)`.
Gauss IRK4 is A-stable, but **not L-stable**: `R(z) → 1` as real `z → -∞`.
Thus stability at large negative `z` does not imply strong fast-mode damping.

## Sources / 书本出处

- J. C. Butcher, *Numerical Methods for Ordinary Differential Equations*,
  3rd ed., Wiley, 2016, Chapter 3, §34.2 “Methods based on Gaussian
  quadrature,” pp. 228–232: Gauss collocation method; §35.3,
  “A-stability of Gauss and related methods,” p. 252 onward; §36.0,
  “Implementation of implicit Runge--Kutta methods,” p. 272.
  [Publisher chapter](https://onlinelibrary.wiley.com/doi/10.1002/9781119121534.ch3),
  [author's implicit RK tutorial](https://www.math.auckland.ac.nz/~butcher/ODE-book-2008/Tutorials/IRK.pdf).
- D. F. Griffiths and D. J. Higham, *Numerical Methods for Ordinary
  Differential Equations: Initial Value Problems*, Springer, 2010,
  Chapters 9–11, pp. 109–143, for solving implicit methods, RK order
  conditions, and absolute stability. This is background, not the source of
  the particular tableau.
  [Publisher contents](https://link.springer.com/book/10.1007/978-0-85729-148-6).

## Files / 文件

| File | Purpose / 用途 |
|---|---|
| `gauss_irk4.py` | Gauss tableau, coupled-stage damped Newton solver, stability function, and RHS/Jacobian/Newton counts / 系数、耦合阶段 Newton 求解、稳定函数与成本计数 |
| `run_comparison.py` | Runs the four-method comparison against the same finite-time SVD solution and generates the new data and figures / 四方法比较与作图 |
| `test_gauss_irk4.py` | Checks fourth-order conditions, scalar stability, matrix convergence, Newton failure, tolerance sensitivity, energy and rank deficiency / 核对四阶条件、稳定性、矩阵收敛、求根失败、容差、能量与秩亏情形 |
| `SECTION5_ADVANCED_METHOD_PATCH.md` | Readable theory notes, code and figure evidence map, and handoff rules for a new Section 5 / 新 Section 5 的理论、代码与图片交接补丁 |

## Run / 运行

From project root, with `requirements.txt` installed:

```powershell
python -B code_advanced/run_comparison.py
python -B -m unittest discover -s code_advanced -p 'test_*.py' -v
```

The output files are:

| File | Meaning / 含义 |
|---|---|
| `figures/advanced_irk4/convergence_comparison.png` | Log-log terminal full-matrix error against step size; slopes show observed orders / 步长与终点误差的双对数图 |
| `figures/advanced_irk4/cost_comparison.png` | Error against counted RHS calls; stars mark nearly matched RK4/Gauss errors; excludes Jacobian assembly and dense linear solves / 近似同精度的成本比较 |
| `figures/advanced_irk4/stability_comparison.png` | Negative-real-axis amplification `|R(z)|`, including the initial `h=0.08` fast mode / 负实轴稳定放大因子 |
| `figures/advanced_irk4/energy_comparison.png` | Sampled energy along all four numerical trajectories at `h=0.1` / 四方法同一步长能量轨迹 |
| `data/advanced_irk4/convergence_cost.csv` | Steps, errors, RHS/Jacobian calls and Newton iterations / 步数、误差与工作量原始数据 |
| `data/advanced_irk4/energy_trajectories.csv` | Sampled energy values behind the energy figure / 能量图原始数据 |
| `data/advanced_irk4/summary.json` | Settings, fitted orders, and fast-mode amplification / 设置、拟合阶与放大因子 |

The `newton_tol=1e-12` setting controls the **stage residual**, not the
target global solution error. Cost comparisons should quote all three work
counts and avoid claiming CPU optimality from RHS calls alone.

`newton_tol=1e-12` 是**阶段方程残差容差**，不是全局解误差目标。
成本讨论应同时给出 RHS、Jacobian 和 Newton 次数，不能只凭 RHS 调用数
断言某方法的 CPU 时间更优。
