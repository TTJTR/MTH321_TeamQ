"""Portable experiment entry point. Run tests before interpreting outputs."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np
import scipy
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.fdm import solve
from src.pinn import train,evaluate


def write_json(path,data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False),encoding="utf-8")


def plot(out,arrays):
    fig,axes=plt.subplots(1,3,figsize=(12,3.4),constrained_layout=True)
    for ax,key in zip(axes,["exact","u","error"]):
        mesh=ax.pcolormesh(arrays["x"],arrays["y"],arrays[key],shading="auto",cmap="viridis")
        ax.axvline(.5,color="white",linestyle="--",linewidth=.8)
        ax.set(xlabel="x",ylabel="y",title=key,aspect="equal"); fig.colorbar(mesh,ax=ax)
    fig.savefig(out/"solution.png",dpi=150); plt.close(fig)
    fig,ax=plt.subplots(figsize=(5,3),constrained_layout=True)
    ax.plot(arrays["interface_y"],arrays["flux_left"],label="left trace")
    ax.plot(arrays["interface_y"],arrays["flux_right"],label="right trace")
    ax.set(xlabel="y at x=0.5",ylabel="physical flux -a du/dx"); ax.legend()
    fig.savefig(out/"interface_flux.png",dpi=150); plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/smoke.json")
    parser.add_argument("--output",default=None)
    parser.add_argument("--method",choices=["interface","single"])
    parser.add_argument("--case",choices=["layered","smooth"])
    parser.add_argument("--device",default=None)
    parser.add_argument("--fdm-only",action="store_true")
    parser.add_argument("--require-acceptance",action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    config_path=Path(args.config)
    if not config_path.is_absolute(): config_path=root/config_path
    cfg=json.loads(config_path.read_text(encoding="utf-8"))
    for k in ["method","case","device"]:
        if getattr(args,k) is not None: cfg[k]=getattr(args,k)
    if cfg["adam_steps"]<1 or cfg["lbfgs_steps"]<0: raise ValueError("Invalid optimizer budgets")
    if any(c<=0 for c in cfg["contrasts"]): raise ValueError("Contrasts must be positive")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    out=Path(args.output) if args.output else root/"runs"/stamp
    # Never silently overwrite old predictions or results.
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/"config.json",cfg)
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py")) if "runs" not in p.relative_to(root).parts}
    write_json(out/"environment.json",dict(python=sys.version,platform=platform.platform(),
                torch=torch.__version__,numpy=np.__version__,scipy=scipy.__version__,
                cuda_available=torch.cuda.is_available(),torch_cuda=torch.version.cuda,
                gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                created_utc=stamp,source_sha256=hashes))
    write_json(out/"predictions_before_run.json",dict(
        author="AI-generated predictions; team must independently audit before coursework use",
        smooth="Arithmetic shared-face FDM should approach order 2 in interior h-weighted L2 and nodal Linf.",
        layered="For odd N, harmonic faces should reproduce piecewise-linear exact nodal values up to solver error, with constant -2c/(1+c) interface flux. Arithmetic faces should be less accurate for c>1.",
        matrix="After Dirichlet elimination, shared positive faces imply SPD; numerical symmetry and a small-grid eigenvalue estimate corroborate this.",
        pinn="Two subdomain networks can represent the derivative jump. A globally smooth single network cannot exactly reproduce nonzero continuous flux at a coefficient jump. No PINN accuracy or superiority is guaranteed.",
        acceptance=cfg["acceptance"],
        runs=[dict(contrast=c,seeds=cfg["seeds"],meshes=cfg["fdm_intervals"]) for c in cfg["contrasts"]]))
    fdm_rows=[]; pinn_rows=[]; passed=True
    contrasts=cfg["contrasts"] if cfg["case"]=="layered" else [1.]
    for contrast in contrasts:
        for average in (["arithmetic","harmonic"] if cfg["case"]=="layered" else ["arithmetic"]):
            previous=None
            for n in cfg["fdm_intervals"]:
                row,U=solve(n,cfg["case"],contrast,average,independent=(n==cfg["fdm_intervals"][0]))
                row["order_l2"]=None
                if previous and row["l2"]>1e-12 and previous["l2"]>1e-12:
                    row["order_l2"]=float(np.log(previous["l2"]/row["l2"])/np.log(previous["h"]/row["h"]))
                fdm_rows.append(row); previous=row
                np.savez_compressed(out/f"fdm_c{contrast:g}_{average}_N{n}.npz",u=U)
                print(f"FDM c={contrast:g} {average} N={n} Linf={row['linf']:.3e}",flush=True)
        if args.fdm_only: continue
        for seed in cfg["seeds"]:
            run=out/f"{cfg['method']}_c{contrast:g}_seed{seed}"; run.mkdir()
            model,metadata=train(cfg,contrast,seed,run)
            metrics,arrays=evaluate(model,cfg,contrast)
            checks={k:metrics[k]<=threshold for k,threshold in cfg["acceptance"].items()}
            row=dict(**metadata,**metrics,acceptance_checks=checks,accepted=all(checks.values()))
            passed=passed and row["accepted"]
            pinn_rows.append(row); write_json(run/"metrics.json",row)
            np.savez_compressed(run/"predictions.npz",**arrays); plot(run,arrays)
            print(f"PINN accepted={row['accepted']} relative_L2={metrics['relative_l2']:.3e} flux_jump_rel={metrics['interface_flux_relative_max']:.3e}",flush=True)
    write_json(out/"fdm_results.json",fdm_rows)
    keys=sorted(set().union(*(r.keys() for r in fdm_rows)))
    with (out/"fdm_results.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,keys); w.writeheader(); w.writerows(fdm_rows)
    write_json(out/"summary.json",dict(fdm=fdm_rows,pinn=pinn_rows,
                pinn_acceptance_passed=passed if pinn_rows else None,
                scope="Smoke/framework results are not a full PINN convergence or superiority study."))
    print(f"Outputs: {out.resolve()}",flush=True)
    if args.require_acceptance and (not pinn_rows or not passed): return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
