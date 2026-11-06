"""Recompute the numerical evidence and all algorithm-section figures on the CPU."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

import numpy as np
import scipy
from threadpoolctl import threadpool_limits, threadpool_info
from src.discretisation import (assemble_fdm, assemble_fem, solution_grid, error_norms,
                                 interface_diagnostics, fdm_fluxes)
from src.solvers import direct, conjugate_gradient, residuals, structure, spectrum


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(name, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with (RESULTS / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def measured_run(method, intervals, case, cfg, contrast=10.0, average="arithmetic"):
    timing_rows = []
    for _ in range(cfg["timing_repeats"]):
        started = time.perf_counter()
        if method == "FDM":
            matrix, rhs, metadata = assemble_fdm(intervals, case, contrast, average)
        else:
            matrix, rhs, metadata = assemble_fem(intervals, case, contrast, cfg["quadrature_order"])
        assembly_seconds = time.perf_counter() - started
        reference, times = direct(matrix, rhs)
        if case == "smooth":
            values, cg_metrics, _ = conjugate_gradient(matrix, rhs, cfg["cg_rtol"])
            times.update({key: value for key, value in cg_metrics.items() if "seconds" in key})
        else:
            values = reference
        timing_rows.append(dict(assembly_seconds=assembly_seconds, **times))
    metrics = {key: statistics.median(row[key] for row in timing_rows) for key in timing_rows[0]}
    metrics.update(structure(matrix))
    metrics.update(residuals(matrix, rhs, values))
    solution = solution_grid(values, metadata)
    metrics.update(error_norms(solution, case, contrast))
    metrics.update(method=method, N=intervals, h=1/intervals, case=case,
                   contrast=contrast, face_rule=average if method == "FDM" else "element_integral",
                   min_u=float(solution.min()), max_u=float(solution.max()))
    if case == "smooth":
        metrics["cg_iterations"] = cg_metrics["cg_iterations"]
        metrics["residual_refinements"] = cg_metrics["residual_refinements"]
        metrics["algebraic_linf"] = float(np.max(np.abs(values-reference)))
        metrics["cg_rtol"] = cfg["cg_rtol"]
        metrics["algebraic_to_discretisation"] = metrics["algebraic_linf"]/metrics["linf_nodal"]
        assert metrics["algebraic_to_discretisation"] < 1e-3
        metrics["total_cg_seconds"] = metrics["assembly_seconds"] + metrics["cg_setup_seconds"] + metrics["cg_seconds"]
    else:
        metrics.update(interface_diagnostics(solution, metadata, method, contrast))
    assert metrics["symmetry_relative"] < 1e-12
    assert metrics["min_diagonal"] > 0
    return metrics, solution, metadata, timing_rows


def run(cfg):
    RESULTS.mkdir(exist_ok=True)
    write_json(RESULTS / "run_status.json", dict(complete=False))
    smooth, layered, timing = [], [], []
    for method in ["FDM", "FEM"]:
        previous = None
        for intervals in cfg["smooth_intervals"]:
            row, solution, meta, repeated = measured_run(method, intervals, "smooth", cfg)
            for metric in ["l2_nodal", "linf_nodal", "l2_common"]:
                row["order_"+metric] = None if previous is None else np.log(previous[metric]/row[metric])/np.log(previous["h"]/row["h"])
            smooth.append(row)
            timing.extend(dict(method=method, N=intervals, case="smooth", repeat=i+1, **t) for i,t in enumerate(repeated))
            previous = row
            print(f"smooth {method} N={intervals} L2={row['l2_common']:.4e}", flush=True)
            if intervals == 32:
                np.savez_compressed(RESULTS/f"smooth_{method}_N32.npz", u=solution, x=meta["x"], y=meta["y"])
        for intervals in cfg["layered_fdm_intervals"] if method == "FDM" else cfg["layered_fem_intervals"]:
            for average in ["arithmetic", "harmonic"] if method == "FDM" else ["element_integral"]:
                row, solution, meta, repeated = measured_run(method, intervals, "layered", cfg, average=average)
                layered.append(row)
                timing.extend(dict(method=method, N=intervals, case="layered", face_rule=average, repeat=i+1, **t) for i,t in enumerate(repeated))
                assert row["min_u"] >= -1e-10 and row["max_u"] <= 1+1e-10
                if average != "arithmetic":
                    assert row["linf_nodal"] < 1e-10 and row["interface_flux_error"] < 1e-8
                if method == "FDM" and intervals == 63:
                    qx, qy, balance = fdm_fluxes(solution, meta)
                    np.savez_compressed(RESULTS/f"layered_{average}_N63.npz", u=solution, qx=qx, qy=qy, balance=balance, x=meta["x"], y=meta["y"])
                print(f"layered {method} {average} N={intervals} Linf={row['linf_nodal']:.3e}", flush=True)

    tolerances = []
    for method, assemble in [("FDM", assemble_fdm), ("FEM", assemble_fem)]:
        matrix, rhs, meta = assemble(32)
        reference, _ = direct(matrix, rhs)
        for tolerance in cfg["tolerance_sweep"]:
            values, metrics, history = conjugate_gradient(matrix, rhs, tolerance, record=True)
            error = error_norms(solution_grid(values, meta))
            tolerances.append(dict(method=method, N=32, rtol=tolerance,
                                   algebraic_linf=float(np.max(np.abs(values-reference))), **metrics, **error))
            write_json(RESULTS/f"residual_{method}_{tolerance:g}.json", history)

    conditioning = []
    for contrast in cfg["contrasts"]:
        for intervals in cfg["conditioning_intervals"]:
            matrix, rhs, _ = assemble_fdm(intervals, "layered", contrast, "harmonic")
            row = dict(N=intervals, h=1/intervals, contrast=contrast, **spectrum(matrix))
            for jacobi, label in [(False, "plain"), (True, "jacobi")]:
                _, metrics, _ = conjugate_gradient(matrix, rhs, cfg["cg_rtol"], jacobi=jacobi)
                row[label+"_iterations"] = metrics["cg_iterations"]
                row[label+"_relative_residual"] = metrics["relative_residual"]
            assert row["lambda_min"] > 0 and row["eigen_residual_low"] < 1e-6
            conditioning.append(row)
            print(f"conditioning c={contrast:g} N={intervals} kappa={row['condition_estimate']:.3e}", flush=True)

    write_csv("smooth.csv", smooth)
    write_csv("layered.csv", layered)
    write_csv("tolerance_sweep.csv", tolerances)
    write_csv("conditioning.csv", conditioning)
    write_csv("timing_repeats.csv", timing)
    write_json(RESULTS/"environment.json", dict(
        created_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
        platform=platform.platform(), processor=platform.processor(),
        numpy=np.__version__, scipy=scipy.__version__, numerical_threads=1,
        threadpools=threadpool_info(), config=cfg,
        source_sha256={str(p.relative_to(ROOT)).replace("\\", "/"):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(ROOT.rglob("*.py"))},
    ))
    write_json(RESULTS/"run_status.json", dict(complete=True, smooth_runs=len(smooth), layered_runs=len(layered)))


def main():
    RESULTS.mkdir(exist_ok=True)
    write_json(RESULTS / "run_status.json", dict(complete=False))
    tests = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT, capture_output=True, text=True,
    )
    output = tests.stdout + tests.stderr
    (RESULTS / "tests.log").write_text(output, encoding="utf-8")
    print(output, end="", flush=True)
    tests.check_returncode()
    cfg = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    with threadpool_limits(limits=1):
        run(cfg)
    subprocess.run([sys.executable, "-B", "make_figures.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
