"""题目 ⑤ 的可复现实验与可直接用于英文报告的图表。

每张图均由实际数值输出生成；同名 CSV 保存绘图数据，summary.json
保存参数与主要诊断指标。图中的英文标签与英文版保持一致，方便两版结果核对。
"""

from __future__ import annotations

import csv
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.integrate import solve_ivp

from model import (benchmark, energy, exact_matrix, jacobian, lyapunov_rate,
                   matrix_rhs, orthogonality_defect, rhs, rotation,
                   singular_values, unvectorize, vectorize)
from solvers import StepFailure, solve_adaptive, solve_fixed


METHODS = ("euler", "rk4", "implicit_euler")
COLORS = {"euler": "#d95f02", "rk4": "#1b9e77", "implicit_euler": "#7570b3"}
LABELS = {"euler": "Explicit Euler", "rk4": "RK4", "implicit_euler": "Implicit Euler"}
MARKERS = {"euler": "o", "rk4": "s", "implicit_euler": "^"}
LINESTYLES = {"euler": "-", "rk4": "--", "implicit_euler": ":"}
T_END = 2.0
NEWTON_TOL = 1e-12
MATCHED_STEPS = {"euler": 160, "rk4": 17, "implicit_euler": 160}


def _csv(path: Path, rows: list[dict]) -> None:
    """将字典列表写入带表头的 UTF-8 CSV。"""
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _save(fig: plt.Figure, path: Path) -> None:
    """保存并关闭 Matplotlib 图，避免批量绘图时积累窗口。"""
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _style() -> None:
    """设置所有图共用的字号、网格和输出分辨率。"""
    plt.rcParams.update({"font.size": 10, "axes.grid": True,
                         "grid.alpha": 0.2, "figure.dpi": 120,
                         "axes.spines.top": False, "axes.spines.right": False})


def convergence(out: Path, x0: np.ndarray) -> dict:
    """比较三种方法在 t=2 的完整矩阵误差，计算细网格收敛斜率。"""
    y0 = vectorize(x0)
    exact = exact_matrix(T_END, x0)
    rows = []
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 8.6), sharex=True)
    summary = {}
    for ax, method in zip(axes, METHODS):
        steps = (40, 80, 160, 320, 640, 1280, 2560) if method == "rk4" else (40, 80, 160, 320)
        errors = []
        for n in steps:
            sol = solve_fixed(method, rhs, jacobian, y0, (0, T_END), n,
                              newton_tol=NEWTON_TOL)
            error = float(np.linalg.norm(unvectorize(sol.y[-1]) - exact, "fro"))
            errors.append(error)
            rows.append({"method": method, "n_steps": n, "h": T_END / n,
                         "terminal_frobenius_error": error,
                         "observed_order": "" if len(errors) == 1 else
                         np.log2(errors[-2] / errors[-1]),
                         "rhs_evaluations": sol.nfev,
                         "jacobian_evaluations": sol.njev,
                         "newton_iterations": sol.newton_iterations})
        h = T_END / np.asarray(steps)
        fit_count = 3 if method == "rk4" else len(steps)
        log_h = np.log(h[-fit_count:])
        log_error = np.log(errors[-fit_count:])
        (slope, intercept), covariance = np.polyfit(log_h, log_error, 1, cov=True)
        slope = float(slope)
        slope_se = float(np.sqrt(covariance[0, 0]))
        expected_order = 4 if method == "rk4" else 1
        summary[method] = {"asymptotic_fit_slope": slope,
                           "slope_standard_error": slope_se,
                           "theoretical_order": expected_order,
                           "fit_step_sizes": h[-fit_count:].tolist(),
                           "finest_error": errors[-1]}
        ax.loglog(h, errors, color=COLORS[method], marker=MARKERS[method],
                  linestyle=LINESTYLES[method], label="computed error")
        h_line = np.geomspace(min(h), max(h), 100)
        anchor_h, anchor_error = h[-1], errors[-1]
        ax.loglog(h_line, anchor_error * (h_line / anchor_h)**expected_order,
                  color="0.3", linestyle="--", linewidth=1.2,
                  label=fr"reference $h^{expected_order}$")
        x_line = np.log(h_line)
        design = np.column_stack((x_line, np.ones_like(x_line)))
        log_fit = slope * x_line + intercept
        log_se = np.sqrt(np.einsum("ij,jk,ik->i", design, covariance, design))
        ax.loglog(h_line, np.exp(log_fit), color=COLORS[method],
                  linestyle=":", linewidth=1.1, label="log-log fit")
        ax.fill_between(h_line, np.exp(log_fit - 1.96 * log_se),
                        np.exp(log_fit + 1.96 * log_se), color=COLORS[method],
                        alpha=0.13, label="95% regression band")
        ax.set(ylabel=r"$\|X_h(2)-X(2)\|_F$", title=f"{LABELS[method]}: fitted slope {slope:.3f} ± {slope_se:.3f}")
        ax.legend(fontsize=8, loc="upper left")
    axes[-1].set_xlabel("Step size h (dimensionless)")
    fig.suptitle("Full-matrix error follows the predicted orders", fontsize=12)
    fig.tight_layout()
    _save(fig, out / "convergence.png")
    _csv(out / "convergence.csv", rows)
    return summary


def oracle(out: Path, x0: np.ndarray) -> dict:
    """用高精度 SciPy Radau 对 SVD 精确解进行独立交叉验证。"""
    y0 = vectorize(x0)
    reference = solve_ivp(rhs, (0, T_END), y0, method="Radau", jac=jacobian,
                          rtol=1e-12, atol=1e-14)
    if not reference.success:
        raise RuntimeError(f"Radau 参考求解失败：{reference.message}")
    disagreement = float(np.linalg.norm(unvectorize(reference.y[:, -1]) -
                                        exact_matrix(T_END, x0), "fro"))
    return {"method": "scipy.integrate.solve_ivp / Radau",
            "rtol": 1e-12, "atol": 1e-14,
            "exact_svd_disagreement": disagreement,
            "rhs_evaluations": reference.nfev}


def trajectory(out: Path, x0: np.ndarray) -> dict:
    """绘制奇异值、Lyapunov 能量和正交性缺陷的时间轨迹。"""
    y0 = vectorize(x0)
    n = 400
    sol = solve_fixed("rk4", rhs, jacobian, y0, (0, T_END), n)
    matrices = np.asarray([unvectorize(y) for y in sol.y])
    exact = exact_matrix(sol.t, x0)
    sv = np.asarray([singular_values(x) for x in matrices])
    sv_exact = np.asarray([singular_values(x) for x in exact])
    phi = np.asarray([energy(x) for x in matrices])
    exact_phi = np.asarray([energy(x) for x in exact])
    defect = np.asarray([orthogonality_defect(x) for x in matrices])
    exact_defect = np.asarray([orthogonality_defect(x) for x in exact])
    # 沿数值轨迹用中心化差分检查 Lyapunov 恒等式；非零残差包含时间离散误差，
    # 不能解释为连续方程违反了该恒等式。
    midpoint = (matrices[1:] + matrices[:-1]) / 2
    identity_residual = np.diff(phi) / np.diff(sol.t) - np.asarray(
        [lyapunov_rate(x) for x in midpoint])

    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.5))
    axes = axes.ravel()
    sv_colors = (COLORS["euler"], COLORS["rk4"], COLORS["implicit_euler"])
    for i in range(3):
        axes[0].plot(sol.t, sv[:, i], color=sv_colors[i], label=fr"computed $s_{i+1}$")
        axes[0].plot(sol.t, sv_exact[:, i], color=sv_colors[i], linestyle="--",
                     linewidth=1.0, label="finite-time exact (dashed)" if i == 0 else None)
    axes[0].axhline(1, color="gray", linewidth=0.8)
    axes[0].set(xlabel="Time t (dimensionless)", ylabel="Singular value (dimensionless)", title="Each singular value moves toward 1")
    axes[0].legend(fontsize=8)
    axes[1].semilogy(sol.t, phi, color=COLORS["rk4"], label="RK4")
    axes[1].semilogy(sol.t, exact_phi, "k--", linewidth=1, label="finite-time exact")
    axes[1].set(xlabel="Time t (dimensionless)", ylabel=r"$\Phi(X)$ (dimensionless)", title="Energy decreases along the trajectory")
    axes[1].legend(fontsize=8)
    axes[2].semilogy(sol.t, defect, color=COLORS["rk4"], label="RK4")
    axes[2].semilogy(sol.t, exact_defect, "k--", label="finite-time exact")
    axes[2].set(xlabel="Time t (dimensionless)", ylabel=r"$\|X^T X-I\|_F$ (dimensionless)", title="Finite-time defect is nonzero")
    axes[2].legend(fontsize=8)
    axes[3].semilogy((sol.t[1:] + sol.t[:-1]) / 2,
                    np.maximum(np.abs(identity_residual), np.finfo(float).tiny),
                    color=COLORS["rk4"])
    axes[3].set(xlabel="Time t (dimensionless)", ylabel="Absolute residual (dimensionless)",
                title="Discrete Lyapunov residual stays small")
    fig.tight_layout()
    _save(fig, out / "trajectory_diagnostics.png")
    _csv(out / "trajectory.csv", [
        {"t": t, "s1": s[0], "s2": s[1], "s3": s[2],
         "energy": e, "exact_energy": ee, "orthogonality_defect": d,
         "exact_orthogonality_defect": de,
         "lyapunov_identity_residual_next_interval":
             identity_residual[k] if k < len(identity_residual) else ""}
        for k, (t, s, e, ee, d, de) in enumerate(zip(sol.t, sv, phi, exact_phi, defect, exact_defect))])
    return {"method": "rk4", "h": T_END / n,
            "energy_monotone": bool(np.all(np.diff(phi) <= 1e-12)),
            "singular_values_move_toward_one": bool(np.all(
                np.diff(np.abs(sv - 1.0), axis=0) <= 1e-10)),
            "singular_value_crossing": bool(np.any((sv - 1) * (sv[0] - 1) < -1e-10)),
            "max_discrete_lyapunov_identity_residual": float(np.max(np.abs(identity_residual))),
            "max_scaled_discrete_identity_residual": float(np.max(np.abs(identity_residual) /
                np.maximum(1.0, np.abs([lyapunov_rate(x) for x in midpoint])))),
            "final_orthogonality_defect": float(defect[-1]),
            "exact_final_orthogonality_defect": float(exact_defect[-1])}


def stability_regions(out: Path, x0: np.ndarray) -> dict:
    """绘制三种方法的绝对稳定域和初值 Jacobian 的缩放谱。"""
    real = np.linspace(-4, 2, 500)
    imag = np.linspace(-3, 3, 500)
    z = real[:, None] + 1j * imag[None, :]
    amplification = {
        "euler": 1 + z,
        "rk4": 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24,
        "implicit_euler": 1 / (1 - z),
    }
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.6), sharex=True, sharey=True)
    for ax, method in zip(axes, METHODS):
        values = np.abs(amplification[method]).T
        ax.contourf(real, imag, (values <= 1).astype(float),
                    levels=[-0.5, 0.5, 1.5], colors=["white", COLORS[method]], alpha=0.45)
        ax.contour(real, imag, values, levels=[1], colors=[COLORS[method]], linewidths=1.5)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axvline(0, color="black", linewidth=0.5)
        ax.set(title=LABELS[method], xlabel=r"Re($z$)", xlim=(-4, 2), ylim=(-3, 3))
    axes[0].set_ylabel(r"Im($z$)")
    fig.suptitle(r"Scalar absolute stability: shaded where $|R(z)|\leq 1$, $z=h\lambda$", fontsize=11)
    fig.tight_layout()
    _save(fig, out / "stability_regions.png")

    spectrum = np.sort(np.linalg.eigvalsh(jacobian(0, vectorize(x0))))
    equilibrium = np.sort(np.linalg.eigvalsh(jacobian(0, vectorize(rotation(0.4) @ rotation(-0.7).T))))
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for h, row_y, marker in ((0.05, 1, "o"), (0.10, 0, "s")):
        ax.scatter(h * spectrum, np.full_like(spectrum, row_y),
                   marker=marker, s=48, color=COLORS["rk4" if h == 0.05 else "euler"],
                   edgecolor="white", linewidth=0.5, label=f"h = {h:.2f}", zorder=3)
    ax.axvspan(-2, 0, color=COLORS["euler"], alpha=0.12, label="Euler negative-real interval")
    ax.axvline(-2.785293563, color=COLORS["rk4"], linestyle="--", label="RK4 boundary")
    ax.axvline(0, color="0.2", linewidth=0.8)
    ax.annotate("physical growth mode", xy=(0.088, 0), xytext=(0.23, 0.45),
                arrowprops={"arrowstyle": "->", "color": "0.25"}, fontsize=8)
    ax.set(xlabel=r"Re($h\lambda$) for initial Jacobian", ylabel="Step size h",
           yticks=[0, 1], yticklabels=["0.10", "0.05"], ylim=(-0.45, 1.5),
           title="Frozen initial spectrum predicts local step restrictions")
    ax.legend(fontsize=8, loc="lower left", ncol=2)
    _save(fig, out / "frozen_spectrum.png")
    return {"initial_jacobian_spectrum": spectrum.tolist(),
            "orthogonal_equilibrium_spectrum": equilibrium.tolist(),
            "euler_local_h_limit": 2 / 26,
            "rk4_local_h_limit": 2.785293563 / 26}


def cost_accuracy(out: Path, x0: np.ndarray) -> dict:
    """在几乎相同的有限时间完整矩阵误差下比较可计数的工作量。"""
    y0 = vectorize(x0)
    exact = exact_matrix(T_END, x0)
    rows = []
    matched_rows = []
    curve_steps = {"euler": (40, 80, 120, 160, 240, 320),
                   "rk4": (12, 14, 17, 20, 24, 32, 40),
                   "implicit_euler": (40, 80, 120, 160, 240, 320)}
    for method in METHODS:
        for steps in curve_steps[method]:
            sol = solve_fixed(method, rhs, jacobian, y0, (0, T_END), steps,
                              newton_tol=NEWTON_TOL)
            row = {"method": method, "n_steps": steps, "h": T_END / steps,
                   "terminal_frobenius_error": float(np.linalg.norm(
                       unvectorize(sol.y[-1]) - exact, "fro")),
                   "rhs_evaluations": sol.nfev,
                   "jacobian_evaluations": sol.njev,
                   "newton_iterations": sol.newton_iterations,
                   "matched_point": steps == MATCHED_STEPS[method]}
            rows.append(row)
            if row["matched_point"]:
                matched_rows.append(row)
    _csv(out / "cost_accuracy.csv", rows)
    fig, ax = plt.subplots(figsize=(7.3, 4.5))
    for method in METHODS:
        subset = [row for row in rows if row["method"] == method]
        ax.loglog([row["rhs_evaluations"] for row in subset],
                  [row["terminal_frobenius_error"] for row in subset],
                  color=COLORS[method], marker=MARKERS[method],
                  linestyle=LINESTYLES[method], label=LABELS[method])
        matched = next(row for row in subset if row["matched_point"])
        ax.scatter(matched["rhs_evaluations"], matched["terminal_frobenius_error"],
                   marker="*", s=180, color=COLORS[method], edgecolor="black",
                   linewidth=0.5, zorder=5)
    lower = min(row["terminal_frobenius_error"] for row in matched_rows)
    upper = max(row["terminal_frobenius_error"] for row in matched_rows)
    ax.axhspan(lower, upper, color="0.5", alpha=0.14, label="matched-error band")
    ax.set(xlabel="RHS evaluations (count)",
           ylabel=r"Terminal error $\|X_h(2)-X(2)\|_F$ (dimensionless)",
           title=r"RK4 uses fewer RHS calls near $9\times10^{-4}$ error")
    ax.legend(fontsize=8)
    fig.tight_layout()
    _save(fig, out / "cost_accuracy.png")
    return {"selection": "fixed step counts chosen to match terminal error",
            "cost_metric": "RHS evaluations; Jacobian and Newton counts reported separately",
            "not_counted": ["Jacobian assembly cost", "linear factorization cost",
                            "Python overhead", "plotting"],
            "curve_steps": curve_steps, "rows": matched_rows,
            "max_to_min_error_ratio": upper / lower}


def stability_sweep(out: Path, x0: np.ndarray) -> dict:
    """扫过多个固定步长，记录扰动放大、能量变化、越界和终点误差。"""
    y0 = vectorize(x0)
    direction = vectorize(rotation(0.4) @ np.diag([0, 0, 1]) @ rotation(-0.7).T)
    epsilon = 1e-7
    rows = []
    n_values = (6, 7, 8, 10, 12, 16, 20, 24, 32, 40, 50, 64, 80)
    for method in METHODS:
        for n in n_values:
            h = T_END / n
            try:
                with np.errstate(over="ignore", invalid="ignore"):
                    base = solve_fixed(method, rhs, jacobian, y0, (0, T_END), n)
                    perturb = solve_fixed(method, rhs, jacobian, y0 + epsilon * direction,
                                          (0, h), 1)
                    unperturb = solve_fixed(method, rhs, jacobian, y0, (0, h), 1)
                x = [unvectorize(y) for y in base.y]
                with np.errstate(over="ignore", invalid="ignore"):
                    energies = np.asarray([energy(a) for a in x])
                if not np.all(np.isfinite(energies)):
                    raise StepFailure("Energy overflowed")
                singular = np.asarray([singular_values(a) for a in x])
                amplification = float(np.linalg.norm(perturb.y[-1] - unperturb.y[-1]) / epsilon)
                crossing = bool(np.any((singular - 1) * (singular[0] - 1) < -1e-9))
                rows.append({"method": method, "h": h, "n_steps": n,
                             "one_step_fast_perturbation_amplification": amplification,
                             "one_step_energy_change": float(energies[1] - energies[0]),
                             "max_energy_increase": float(np.max(np.diff(energies))),
                             "singular_value_crossing": crossing,
                             "terminal_exact_error": float(np.linalg.norm(x[-1] - exact_matrix(T_END, x0), "fro")),
                             "status": "ok"})
            except (StepFailure, FloatingPointError, OverflowError, ValueError):
                with np.errstate(over="ignore", invalid="ignore"):
                    try:
                        first = solve_fixed(method, rhs, jacobian, y0, (0, h), 1)
                        first_energy_change = energy(unvectorize(first.y[-1])) - energy(x0)
                    except (StepFailure, FloatingPointError, OverflowError, ValueError):
                        first_energy_change = np.nan
                rows.append({"method": method, "h": h, "n_steps": n,
                             "one_step_fast_perturbation_amplification": np.nan,
                             "one_step_energy_change": first_energy_change,
                             "max_energy_increase": np.nan,
                             "singular_value_crossing": "",
                             "terminal_exact_error": np.nan, "status": "diverged_or_failed"})
    _csv(out / "stability_sweep.csv", rows)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.9))
    for method in METHODS:
        subset = [r for r in rows if r["method"] == method and r["status"] == "ok"]
        axes[0].plot([r["h"] for r in subset],
                     [r["one_step_fast_perturbation_amplification"] for r in subset],
                     marker=MARKERS[method], linestyle=LINESTYLES[method],
                     color=COLORS[method], label=LABELS[method])
        axes[1].semilogy([r["h"] for r in subset],
                         [r["terminal_exact_error"] for r in subset],
                         marker=MARKERS[method], linestyle=LINESTYLES[method],
                         color=COLORS[method], label=LABELS[method])
    axes[0].axhline(1, color="black", linewidth=0.8)
    axes[0].axvline(2 / 26, color=COLORS["euler"], linestyle="--", linewidth=1,
                    label=r"Euler local limit $2/26$")
    axes[0].axvline(2.785293563 / 26, color=COLORS["rk4"], linestyle=":", linewidth=1.5,
                    label=r"RK4 local limit $2.785/26$")
    axes[0].set(xlabel="Step size h (dimensionless)", ylabel="One-step amplification (dimensionless)",
                title="Fast-mode damping weakens at larger h")
    axes[1].set(xlabel="Step size h (dimensionless)", ylabel="Terminal full-matrix error (dimensionless)",
                title="Large steps also increase global error")
    axes[0].legend(fontsize=7, loc="best")
    axes[1].legend(fontsize=7, loc="best")
    fig.tight_layout()
    _save(fig, out / "stability_sweep.png")
    return {"tested_step_sizes": [T_END / n for n in n_values],
            "failed_runs": [f"{r['method']} h={r['h']:.6g}" for r in rows if r["status"] != "ok"]}


def adaptivity(out: Path, x0: np.ndarray) -> dict:
    """比较三种方法在同一局部误差容差下的实际接受步长。"""
    y0 = vectorize(x0)
    settings = {"atol": 1e-8, "rtol": 1e-6, "initial_step": 0.15}
    rows = []
    fig, ax = plt.subplots(figsize=(7, 4))
    summary = {}
    for method in ("implicit_euler", "euler", "rk4"):
        sol = solve_adaptive(method, rhs, jacobian, y0, (0, T_END),
                             settings["initial_step"], atol=settings["atol"],
                             rtol=settings["rtol"], newton_tol=NEWTON_TOL)
        h = np.diff(sol.t)
        ax.step(sol.t[:-1], h, where="post", label=LABELS[method],
                color=COLORS[method], linestyle=LINESTYLES[method],
                linewidth=1.5 if method == "implicit_euler" else 1.0)
        exact = exact_matrix(T_END, x0)
        summary[method] = {"accepted_steps": len(h), "rejected_attempts": sol.rejected,
                           "min_h": float(np.min(h)), "max_h": float(np.max(h)),
                           "max_accepted_normalized_local_error": float(np.max(sol.error_ratios)),
                           "terminal_exact_error": float(np.linalg.norm(unvectorize(sol.y[-1]) - exact, "fro")),
                           "rhs_evaluations": sol.nfev}
        rows.extend({"method": method, "t_start": t, "h": step,
                     "normalized_local_error": err}
                    for t, step, err in zip(sol.t[:-1], h, sol.error_ratios))
    ax.set(xlabel="Time t (dimensionless)", ylabel="Accepted h (dimensionless)", yscale="log",
           title="Step doubling resolves the fast initial transient")
    ax.legend()
    _save(fig, out / "adaptive_steps.png")
    _csv(out / "adaptive_steps.csv", rows)
    return {"settings": settings, "methods": summary}


def rank_deficient(out: Path) -> dict:
    """重复秩亏初值实验，验证零奇异值与部分等距极限。"""
    x0 = benchmark((0.0, 1.4, 3.0))
    sol = solve_fixed("rk4", rhs, jacobian, vectorize(x0), (0, 8.0), 1600)
    matrices = [unvectorize(y) for y in sol.y]
    singular = np.asarray([singular_values(x) for x in matrices])
    exact_singular = np.asarray([singular_values(x) for x in exact_matrix(sol.t, x0)])
    fig, ax = plt.subplots(figsize=(7, 4))
    for i in range(3):
        ax.plot(sol.t, singular[:, i], color=list(COLORS.values())[i],
                label=fr"computed $s_{i+1}$")
        ax.plot(sol.t, exact_singular[:, i], color=list(COLORS.values())[i],
                linestyle="--", linewidth=1,
                label="finite-time exact (dashed)" if i == 0 else None)
    ax.axhline(1, color="gray", linewidth=0.8)
    ax.set(xlabel="Time t (dimensionless)", ylabel="Singular value (dimensionless)",
           title="Rank-deficient initial matrix retains its zero mode")
    ax.legend()
    _save(fig, out / "rank_deficient.png")
    _csv(out / "rank_deficient.csv", [
        {"t": t, "s1": s[0], "s2": s[1], "s3": s[2],
         "exact_s1": se[0], "exact_s2": se[1], "exact_s3": se[2]}
        for t, s, se in zip(sol.t, singular, exact_singular)])
    final = matrices[-1]
    return {"initial_singular_values": singular[0].tolist(),
            "final_singular_values": singular[-1].tolist(),
            "smallest_singular_value_max": float(np.max(singular[:, -1])),
            "final_orthogonality_defect": orthogonality_defect(final),
            "exact_final_error": float(np.linalg.norm(final - exact_matrix(8.0, x0), "fro"))}


def run_all(output_dir: Path) -> dict:
    """按固定顺序执行全部实验并写入 PNG、CSV、JSON。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    _style()
    x0 = benchmark()
    result = {"interval": [0.0, T_END], "benchmark_singular_values": [0.2, 1.4, 3.0],
              "software": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
              "newton_residual_tolerance": NEWTON_TOL,
              "convergence": convergence(output_dir, x0),
              "cost_accuracy": cost_accuracy(output_dir, x0),
              "independent_oracle": oracle(output_dir, x0),
              "trajectory": trajectory(output_dir, x0),
              "stability_regions": stability_regions(output_dir, x0),
              "stability_sweep": stability_sweep(output_dir, x0),
              "adaptivity": adaptivity(output_dir, x0),
              "rank_deficient": rank_deficient(output_dir)}
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False),
                                             encoding="utf-8")
    return result
