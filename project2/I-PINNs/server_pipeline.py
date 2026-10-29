"""Server batch runner. Shutdown is deliberately left to the downloader after verification."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import traceback
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent


def write(path, data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False),encoding="utf-8")


def status(stage, **extra):
    write(ROOT/"pipeline_status.json",dict(stage=stage,utc=datetime.now(timezone.utc).isoformat(),**extra))


def run(name, args):
    status("running",current=name)
    with (ROOT/f"{name}.log").open("w",encoding="utf-8") as log:
        result=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"{name}: exit {result.returncode}; see {name}.log")


def aggregate():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows=[]
    for method in ["interface","single"]:
        summary=json.loads((ROOT/"runs"/f"server_{method}"/"summary.json").read_text())
        for r in summary["pinn"]:
            rows.append({k:r[k] for k in ["contrast","seed","relative_l2","linf","interface_value_max",
                    "interface_flux_relative_max","interface_flux_error_max","train_seconds","parameters","accepted"]}|{"method":method})
    with (ROOT/"comparison.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
    groups=[]
    for method in ["interface","single"]:
        for c in sorted({r["contrast"] for r in rows}):
            selected=[r for r in rows if r["method"]==method and r["contrast"]==c]
            group=dict(method=method,contrast=c,seeds=len(selected),accepted=sum(r["accepted"] for r in selected))
            for metric in ["relative_l2","interface_flux_relative_max","train_seconds"]:
                values=[r[metric] for r in selected]
                group[metric+"_mean"]=statistics.mean(values)
                group[metric+"_std"]=statistics.stdev(values) if len(values)>1 else 0.
            groups.append(group)
    write(ROOT/"comparison_summary.json",groups)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for method in ["interface","single"]:
        selected=[g for g in groups if g["method"]==method]
        for ax,metric in zip(axes,["relative_l2","interface_flux_relative_max"]):
            ax.errorbar([g["contrast"] for g in selected],
                        [g[metric+"_mean"] for g in selected],
                        yerr=[g[metric+"_std"] for g in selected],marker="o",capsize=3,label=method)
            ax.set(xscale="log",yscale="symlog",xlabel="coefficient ratio",ylabel=metric)
            ax.legend(); ax.grid(alpha=.25)
    fig.savefig(ROOT/"comparison.png",dpi=160); plt.close(fig)
    lines=["# Server experiment summary","", "Mean +/- sample standard deviation across seeds.","",
           "| Method | Contrast | Relative L2 | Relative flux jump | Passed configured checks |",
           "|---|---:|---:|---:|---:|"]
    for g in groups:
        lines.append(f"|{g['method']}|{g['contrast']:g}|{g['relative_l2_mean']:.4g} +/- {g['relative_l2_std']:.3g}|{g['interface_flux_relative_max_mean']:.4g} +/- {g['interface_flux_relative_max_std']:.3g}|{g['accepted']}/{g['seeds']}|")
    lines += ["", "These are generic interface PINN baselines, not a verified reproduction of the named I-PINNs paper.",
              "Single networks have half the parameters. Equal optimizer/sample budgets are not equal parameter budgets.",
              "Configured check failures are retained; optimizer completion is not a convergence certificate.",
              "The exact layered benchmark is y-independent and piecewise linear. It does not establish performance on general curved interfaces."]
    (ROOT/"SERVER_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def bundle(success, error):
    status("packaging",success=success,error=error)
    files=[p for p in sorted(ROOT.rglob("*")) if p.is_file()
           and not any(s in {"__pycache__",".git"} for s in p.relative_to(ROOT).parts)
           and p.name not in {"server_results.zip","download_manifest.json","pipeline_status.json","pipeline.log"}]
    manifest={str(p.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    write(ROOT/"download_manifest.json",dict(success=success,error=error,files=manifest))
    archive=ROOT/"server_results.zip"
    with ZipFile(archive,"w",ZIP_DEFLATED) as z:
        for p in files+[ROOT/"download_manifest.json"]:
            z.write(p,str(p.relative_to(ROOT)))
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    status("finished",success=success,error=error,archive=str(archive),sha256=digest,bytes=archive.stat().st_size)


def main():
    success=False; error=None
    try:
        run("tests",["-m","unittest","discover","-s","tests","-v"])
        run("gpu_smoke",["run_experiment.py","--config","configs/smoke.json","--device","cuda",
                         "--output","runs/gpu_smoke","--require-acceptance"])
        run("smooth_fdm",["run_experiment.py","--config","configs/server.json","--case","smooth",
                          "--fdm-only","--output","runs/server_smooth_fdm"])
        for method in ["interface","single"]:
            run(f"server_{method}",["run_experiment.py","--config","configs/server.json",
                "--device","cuda","--method",method,"--output",f"runs/server_{method}"])
        aggregate(); success=True
    except Exception:
        error=traceback.format_exc()
        (ROOT/"pipeline_error.txt").write_text(error,encoding="utf-8")
    bundle(success,error)


if __name__=="__main__": main()
