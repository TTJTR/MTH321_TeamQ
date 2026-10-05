"""Run the optional Gauss IRK4 comparison without changing original outputs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from model import benchmark, energy, exact_matrix, jacobian, rhs, unvectorize, vectorize  # noqa: E402
from solvers import solve_fixed as solve_original  # noqa: E402
from gauss_irk4 import solve_fixed as solve_gauss, stability_function  # noqa: E402

END = 2.0
METHODS = ("euler", "rk4", "implicit_euler", "gauss_irk4")
LABELS = {"euler": "Explicit Euler", "rk4": "Explicit RK4",
          "implicit_euler": "Implicit Euler", "gauss_irk4": "Gauss IRK4"}
COLORS = {"euler": "#d95f02", "rk4": "#1b9e77",
          "implicit_euler": "#7570b3", "gauss_irk4": "#e7298a"}
STEPS = {"euler": (40, 80, 160, 320),
         "rk4": (40, 75, 80, 160, 320, 640, 1280, 2560),
         "implicit_euler": (40, 80, 160, 320),
         "gauss_irk4": (8, 16, 32, 64, 128, 256)}


def solve(method: str, y0: np.ndarray, n: int):
    if method == "gauss_irk4":
        return solve_gauss(rhs, jacobian, y0, (0.0, END), n)
    return solve_original(method, rhs, jacobian, y0, (0.0, END), n)


def main() -> None:
    figures = ROOT / "figures" / "advanced_irk4"
    data = ROOT / "data" / "advanced_irk4"
    figures.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    x0 = benchmark()
    y0 = vectorize(x0)
    exact = exact_matrix(END, x0)
    rows = []
    fits = {}
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for method in METHODS:
        errors = []
        for n in STEPS[method]:
            sol = solve(method, y0, n)
            error = float(np.linalg.norm(unvectorize(sol.y[-1]) - exact, "fro"))
            errors.append(error)
            rows.append({"method": method, "n_steps": n, "h": END / n,
                         "terminal_frobenius_error": error,
                         "rhs_evaluations": sol.nfev,
                         "jacobian_evaluations": sol.njev,
                         "newton_iterations": sol.newton_iterations,
                         "matched_pair": (method, n) in (("rk4", 75), ("gauss_irk4", 64))})
        fit_slice = slice(-3, None) if method in ("rk4", "gauss_irk4") else slice(-4, None)
        h_fit = END / np.asarray(STEPS[method], dtype=float)[fit_slice]
        slope = float(np.polyfit(np.log(h_fit), np.log(np.asarray(errors)[fit_slice]), 1)[0])
        fits[method] = slope
        ax.loglog(END / np.asarray(STEPS[method]), errors, "o-",
                  color=COLORS[method], label=f"{LABELS[method]} (slope {slope:.2f})")
    ax.set(xlabel="Step size h", ylabel=r"$\|X_h(2)-X(2)\|_F$",
           title="Finite-time full-matrix convergence")
    ax.grid(True, which="both", alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "convergence_comparison.png", dpi=220)
    plt.close(fig)
    with (data / "convergence_cost.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for method in METHODS:
        subset = [r for r in rows if r["method"] == method]
        ax.loglog([r["rhs_evaluations"] for r in subset],
                  [r["terminal_frobenius_error"] for r in subset], "o-",
                  color=COLORS[method], label=LABELS[method])
    for row in (r for r in rows if r["matched_pair"]):
        ax.scatter(row["rhs_evaluations"], row["terminal_frobenius_error"],
                   color=COLORS[row["method"]], marker="*", s=170,
                   edgecolor="black", linewidth=0.5, zorder=5)
    ax.set(xlabel="RHS evaluations (count)", ylabel=r"$\|X_h(2)-X(2)\|_F$",
           title="Accuracy versus counted RHS work")
    ax.grid(True, which="both", alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "cost_comparison.png", dpi=220)
    plt.close(fig)

    real = np.linspace(-8.0, 2.0, 800)
    amplification = {"euler": 1 + real,
                     "rk4": 1 + real + real**2 / 2 + real**3 / 6 + real**4 / 24,
                     "implicit_euler": 1 / (1 - real),
                     "gauss_irk4": stability_function(real)}
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for method in METHODS:
        ax.plot(real, np.abs(amplification[method]), color=COLORS[method],
                label=LABELS[method])
    ax.axhline(1, color="black", linewidth=0.8)
    ax.axvline(-26 * 0.08, color="gray", linestyle="--", linewidth=1,
               label=r"Initial fast mode, $h=0.08$")
    ax.set(xlim=(-8, 0), ylim=(0, 2), xlabel=r"$z=h\lambda$ (negative real axis)",
           ylabel=r"$|R(z)|$", title="Linearised fast-mode amplification")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "stability_comparison.png", dpi=220)
    plt.close(fig)

    n_energy = 20
    energy_rows = []
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for method in METHODS:
        sol = solve(method, y0, n_energy)
        values = [energy(unvectorize(y)) for y in sol.y]
        ax.plot(sol.t, values, "o-", markersize=2.5, color=COLORS[method], label=LABELS[method])
        energy_rows.extend({"method": method, "t": float(t), "energy": float(value)}
                           for t, value in zip(sol.t, values))
    ax.set(xlabel="Time t", ylabel=r"$\Phi(X_h)$", title="Energy at common step size h=0.1")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "energy_comparison.png", dpi=220)
    plt.close(fig)
    with (data / "energy_trajectories.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(energy_rows[0]))
        writer.writeheader()
        writer.writerows(energy_rows)

    summary = {"method": "two-stage Gauss-Legendre implicit RK, order 4",
               "interval": [0.0, END], "newton_residual_tolerance": 1e-12,
               "fit_slopes": fits,
               "stability_function": "(1+z/2+z^2/12)/(1-z/2+z^2/12)",
               "fast_mode_h008_amplification": {
                   method: float(abs(value)) for method, value in
                   ((method, np.interp(-26 * 0.08, real, np.abs(amplification[method])))
                   for method in METHODS)},
               "matched_pair": [r for r in rows if r["matched_pair"]],
               "cost_caveat": "RHS evaluations exclude Jacobian assembly, dense linear solves and Python overhead"}
    (data / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Figures: {figures}\nData: {data}")


if __name__ == "__main__":
    main()
