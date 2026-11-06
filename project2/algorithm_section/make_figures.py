"""Plot measured numerical evidence and write LaTeX tables for the algorithm section."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.discretisation import assemble_fdm, assemble_fem, exact


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
BLUE, ORANGE = "#196b91", "#c7642b"
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "savefig.dpi": 200})


def read(name):
    with (RESULTS/name).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def save(fig, name):
    for extension in ["pdf", "png"]:
        fig.savefig(FIGURES/f"{name}.{extension}", bbox_inches="tight")
    plt.close(fig)


def write_tables(smooth, layered, tolerances):
    header = "\\begin{tabular}{llrrrrr}\n\\toprule\nMethod & $N$ & DOF & $E_{2,h}$ & $E_\\infty$ & $p_{2,h}$ & CG its.\\\\\n\\midrule\n"
    lines = [header]
    for row in smooth:
        order = "---" if not row["order_l2_nodal"] else f"{float(row['order_l2_nodal']):.2f}"
        lines.append(f"{row['method']} & {row['N']} & {row['dof']} & {float(row['l2_nodal']):.3e} & {float(row['linf_nodal']):.3e} & {order} & {row['cg_iterations']}\\\\\n")
    lines.append("\\bottomrule\n\\end{tabular}\n")
    (TABLES/"smooth.tex").write_text("".join(lines), encoding="utf-8")
    lines = ["\\begin{tabular}{llrrrr}\n\\toprule\nMethod & Face rule & $N$ & $E_\\infty$ & $E_q$ & $J_q$\\\\\n\\midrule\n"]
    selected = [r for r in layered if int(r["N"]) in [63, 64]]
    for row in selected:
        rule = row["face_rule"].replace("element_integral", "element integral")
        lines.append(f"{row['method']} & {rule} & {row['N']} & {float(row['linf_nodal']):.3e} & {float(row['interface_flux_error']):.3e} & {float(row['reconstructed_flux_jump']):.3e}\\\\\n")
    lines.append("\\bottomrule\n\\end{tabular}\n")
    (TABLES/"interface.tex").write_text("".join(lines), encoding="utf-8")
    lines = ["\\begin{tabular}{lrrrr}\n\\toprule\nMethod & CG rtol & $\\|U_{\\rm CG}-U_{\\rm LU}\\|_\\infty$ & $E_\\infty$ & $\\|r\\|_2/\\|b\\|_2$\\\\\n\\midrule\n"]
    for row in tolerances:
        lines.append(f"{row['method']} & {float(row['rtol']):.0e} & {float(row['algebraic_linf']):.3e} & {float(row['linf_nodal']):.3e} & {float(row['relative_residual']):.3e}\\\\\n")
    lines.append("\\bottomrule\n\\end{tabular}\n")
    (TABLES/"tolerance.tex").write_text("".join(lines), encoding="utf-8")
    lines = ["\\begin{tabular}{lrrrrr}\n\\toprule\nMethod & $N$ & nnz & Assembly (s) & CG (s) & LU (s)\\\\\n\\midrule\n"]
    for row in smooth:
        if int(row["N"]) in [64, 128]:
            lines.append(f"{row['method']} & {row['N']} & {row['nnz']} & {float(row['assembly_seconds']):.3e} & {float(row['cg_seconds']):.3e} & {float(row['direct_seconds']):.3e}\\\\\n")
    lines.append("\\bottomrule\n\\end{tabular}\n")
    (TABLES/"cost.tex").write_text("".join(lines), encoding="utf-8")


def main():
    if not json.loads((RESULTS/"run_status.json").read_text())["complete"]:
        raise RuntimeError("Numerical run is incomplete")
    FIGURES.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)
    smooth, layered, tolerances = read("smooth.csv"), read("layered.csv"), read("tolerance_sweep.csv")
    write_tables(smooth, layered, tolerances)

    fig, ax = plt.subplots(figsize=(10, 2.2))
    labels = ["Model + exact data\nchoose N and face rule", "Shared faces /\nP1 element integrals",
              "Eliminate Dirichlet\nassemble sparse A, b", "CG + Jacobi\ncheck against sparse LU",
              "Errors, flux, structure\nCSV + reproducible plots"]
    for i, label in enumerate(labels):
        box = FancyBboxPatch((i*2.05, .35), 1.8, .9, boxstyle="round,pad=.04", fc="#eff5f8", ec=BLUE)
        ax.add_patch(box)
        ax.text(i*2.05+.9, .8, label, ha="center", va="center", fontsize=8)
        if i < 4:
            ax.annotate("", xy=(i*2.05+2, .8), xytext=(i*2.05+1.85, .8), arrowprops={"arrowstyle":"->", "color":BLUE})
    ax.set(xlim=(-.1, 10.2), ylim=(.05, 1.5))
    ax.axis("off")
    save(fig, "fig01_algorithm")

    fig, axes = plt.subplots(1, 3, figsize=(9, 2.7), constrained_layout=True)
    for ax, method, assemble in [(axes[0], "FDM", assemble_fdm), (axes[1], "P1 FEM", assemble_fem)]:
        matrix, _, _ = assemble(8)
        ax.spy(matrix, markersize=1.2, color=BLUE)
        ax.set(title=f"{method}, N=8, nnz={matrix.nnz}", xlabel="Column index", ylabel="Row index")
    matrix, _, _ = assemble_fdm(3, "constant")
    image = axes[2].imshow(matrix.toarray()/9, cmap="RdBu_r", vmin=-4, vmax=4)
    for i in range(4):
        for j in range(4):
            axes[2].text(j, i, f"{matrix[i,j]/9:g}", ha="center", va="center")
    axes[2].set(title="Hand check: h² A, N=3", xticks=range(4), yticks=range(4))
    save(fig, "fig02_sparse_assembly")

    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for method, color in [("FDM", BLUE), ("FEM", ORANGE)]:
        selected = [r for r in smooth if r["method"] == method]
        h = np.array([float(r["h"]) for r in selected])
        for ax, metric, title in [(axes[0,0], "l2_nodal", "Nodal area-weighted L2"),
                                  (axes[0,1], "linf_nodal", "Common-node maximum error"),
                                  (axes[1,0], "l2_common", "Common P1-integrated L2")]:
            values = np.array([float(r[metric]) for r in selected])
            slope = np.polyfit(np.log(h[-3:]), np.log(values[-3:]), 1)[0]
            ax.loglog(h, values, "o", color=color, label=f"{method}, fitted p={slope:.3f}")
            ax.set(xlabel="h", ylabel="Error", title=title)
            ax.grid(alpha=.2, which="both")
            ax.legend(fontsize=8)
        axes[1,1].loglog([float(r["total_cg_seconds"]) for r in selected],
                        [float(r["l2_common"]) for r in selected], "o-", color=color, label=method)
    for ax, metric in [(axes[0,0], "l2_nodal"), (axes[0,1], "linf_nodal"), (axes[1,0], "l2_common")]:
        selected = [r for r in smooth if r["method"] == "FDM"]
        h = np.array([float(r["h"]) for r in selected])
        ax.loglog(h, float(selected[0][metric])*(h/h[0])**2, "--", color="#666666", alpha=.65, label="h² reference")
        ax.legend(fontsize=8)
    axes[1,1].set(xlabel="Assembly + Jacobi setup + CG (s)", ylabel="Common P1-integrated L2", title="Measured cost versus accuracy")
    axes[1,1].grid(alpha=.2, which="both")
    axes[1,1].legend()
    save(fig, "fig03_accuracy_cost")

    fig, axes = plt.subplots(2, 2, figsize=(9, 5.8), constrained_layout=True)
    for rule, color in [("arithmetic", ORANGE), ("harmonic", BLUE)]:
        with np.load(RESULTS/f"layered_{rule}_N63.npz") as data:
            u, x, y, qx = [data[k] for k in ["u", "x", "y", "qx"]]
            axes[0,0].plot(x[:, 31], u[:, 31], ".-", color=color, markersize=2, label=rule)
            axes[0,1].plot((x[:-1,31]+x[1:,31])/2, qx[:, 31], ".-", color=color, markersize=2, label=rule)
            axes[1,0].plot(y[0,1:-1], qx[31, 1:-1], color=color, label=rule)
            if rule == "arithmetic":
                error = u-exact(x, y, "layered", 10)
                im = axes[1,1].pcolormesh(x, y, error, shading="auto", cmap="RdBu_r", rasterized=True)
                fig.colorbar(im, ax=axes[1,1], label="Signed nodal error")
    axis = np.linspace(0, 1, 300)
    axes[0,0].plot(axis, exact(axis, 0, "layered", 10), "--", color="#333333", label="exact")
    axes[0,0].set(title="Solution at nearest mid-height, N=63", xlabel="x", ylabel="u")
    axes[0,1].set(title="Shared x-face physical flux", xlabel="Face x", ylabel="-a du/dx")
    axes[1,0].set(title="Interface shared-face flux", xlabel="y at x=0.5", ylabel="-a du/dx")
    axes[1,1].set(title="Arithmetic-face solution error", xlabel="x", ylabel="y", aspect="equal")
    for ax in [axes[0,1], axes[1,0]]:
        ax.axhline(-20/11, linestyle="--", color="#333333", label="exact")
    for ax in [axes[0,0], axes[0,1], axes[1,0]]:
        ax.legend(fontsize=8)
        ax.grid(alpha=.2)
    save(fig, "fig04_interface")

    conditioning = read("conditioning.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1), constrained_layout=True)
    for contrast, color in [(1, "#547c42"), (10, BLUE), (100, ORANGE)]:
        selected = [r for r in conditioning if float(r["contrast"]) == contrast]
        sizes = [int(r["N"]) for r in selected]
        axes[0].loglog(sizes, [float(r["condition_estimate"]) for r in selected], "o-", color=color, label=f"c={contrast}")
        axes[1].plot(sizes, [int(r["plain_iterations"]) for r in selected], "o-", color=color, label=f"c={contrast}, CG")
        axes[1].plot(sizes, [int(r["jacobi_iterations"]) for r in selected], "s--", color=color, label=f"c={contrast}, Jacobi-CG")
    axes[0].set(xlabel="Intervals N", ylabel="Estimated kappa2(A)", title="Unscaled harmonic FDM matrix")
    axes[1].set(xlabel="Intervals N", ylabel="Iterations to rtol=1e-12", title="Conditioning and solver work")
    for ax in axes:
        ax.grid(alpha=.2, which="both")
        ax.legend(fontsize=7)
    save(fig, "fig05_conditioning")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1), constrained_layout=True)
    for method, color in [("FDM", BLUE), ("FEM", ORANGE)]:
        history = json.loads((RESULTS/f"residual_{method}_1e-12.json").read_text())
        axes[0].semilogy(np.arange(1, len(history)+1), history, color=color, label=method)
        selected = [r for r in tolerances if r["method"] == method]
        axes[1].loglog([float(r["rtol"]) for r in selected], [float(r["algebraic_linf"]) for r in selected], "o-", color=color, label=method)
    axes[0].axhline(1e-12, color="#555555", linestyle="--", label="rtol")
    axes[0].set(xlabel="CG iteration", ylabel="Explicit relative residual", title="Diagnostic histories, smooth N=32")
    axes[1].set(xlabel="Requested CG rtol", ylabel="Max difference from sparse LU", title="Algebraic-error tolerance sweep")
    for ax in axes:
        ax.grid(alpha=.2, which="both")
        ax.legend(fontsize=8)
    save(fig, "fig06_solver_validation")
    print("Generated 6 figures (PDF/PNG) and 4 LaTeX tables.")


if __name__ == "__main__":
    main()
