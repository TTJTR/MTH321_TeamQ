"""Publish experiment artifacts to the user-authorized repository, then power off."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
CHECKOUT=ROOT.parent/'github_publish_checkout'
TARGET=CHECKOUT/'project2'/'I-PINNs'
REPO='git@github.com:TTJTR/MTH321_TeamQ.git'
PREFIX='project2/I-PINNs/'
ENV=os.environ.copy()
ENV['GIT_SSH_COMMAND']=f'{sys.executable} {ROOT / "git_ssh_relay.py"}'
ENV['GIT_SSH_VARIANT']='simple'
EXCLUDED_NAMES={'github_relay_endpoint.json','github_publish_receipt.json','shutdown_receipt.json',
                'github_publish.log','shutdown_watch.log','pipeline.log'}


def git(*args,timeout=600):
    result=subprocess.run(['git',*args],cwd=CHECKOUT if CHECKOUT.exists() else ROOT,
                          env=ENV,text=True,capture_output=True,timeout=timeout)
    if result.returncode: raise RuntimeError(f'git {args[0]} failed: {result.stderr[-3000:]}')
    return result.stdout.strip()


def save_status(stage,**extra):
    p=ROOT/'github_publish_status.json'
    temp=p.with_suffix('.tmp')
    temp.write_text(json.dumps(dict(stage=stage,utc=datetime.now(timezone.utc).isoformat(),**extra),indent=2),encoding='utf-8')
    temp.replace(p)


def snapshot(final):
    if not CHECKOUT.exists():
        git('clone','--depth','1','--branch','main',REPO,str(CHECKOUT))
    else:
        git('fetch','origin','main')
        git('merge','--ff-only','origin/main')
    git('config','user.name','TTJTR')
    git('config','user.email','151983196+TTJTR@users.noreply.github.com')
    TARGET.mkdir(parents=True,exist_ok=True)
    manifest={}
    # Include all experiment source/data/models/results, exclude credentials, caches and live-control metadata.
    for source in sorted(ROOT.rglob('*')):
        rel=source.relative_to(ROOT)
        if not source.is_file() or any(p in {'__pycache__','.git'} for p in rel.parts): continue
        if source.name in EXCLUDED_NAMES or source.name.startswith('github_publish_status.'): continue
        if not final and rel.parts[0]=='runs':
            # Include completed PINN runs only; never copy a partially written checkpoint/array.
            parent=source.parent
            if source.suffix in {'.pt','.png','.npz','.csv'} and parent.parent.name.startswith('server_'):
                if not (parent/'metrics.json').exists(): continue
        if source.stat().st_size >= 95*1024*1024:
            raise RuntimeError(f'File needs a separate large-file strategy: {rel}')
        destination=TARGET/rel
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
        manifest[rel.as_posix()]=hashlib.sha256(destination.read_bytes()).hexdigest()
    # Preserve original experiment README verbatim, expose a concise repository landing page.
    shutil.copy2(ROOT/'README.md',TARGET/'EXPERIMENT_README.md')
    readme=f'''# I-PINNs — Project 2 interface experiments

Directory requested by the team: `project2/I-PINNs/`.

**Execution status: {"complete" if final else "running — this is an interim snapshot"}.**

This implementation is a generic interface-aware PINN baseline with two subdomain networks and soft solution/flux constraints. It is **not yet verified as a full reproduction of the published I-PINNs architecture**.

- `src/`, `tests/`, `configs/`: numerical methods, independent checks and reproducible configurations.
- `runs/`: original configurations, environment/source hashes, raw NPZ arrays, model checkpoints, training logs, metrics and plots.
- `local_validation/`: original CPU smoke-test data and controls.
- `comparison.csv`, `comparison_summary.json`, `comparison.png`, `SERVER_REPORT.md`: final cross-seed summaries (available after completion).
- `server_results.zip`, `download_manifest.json`: packaged server artifacts and checksums (available after completion).
- `EXPERIMENT_README.md`: detailed equations, norm definitions, commands and limitations.

Actual server GPU reported by CUDA: NVIDIA A100-PCIE-40GB. The team initially described the rental as V100; metadata records the detected hardware.

The standard smooth FDM benchmark checks second-order convergence. The layered benchmark is piecewise linear and y-independent; harmonic FDM can reach round-off. PINN completion is not a convergence certificate. Failed accuracy checks are retained. The single-network baseline has fewer parameters, so equal training budgets are not equal model capacities.

All generated experiment artifacts are included; caches and connection/authentication metadata are excluded. Original course PDFs are not part of this code/results package.
'''
    (TARGET/'README.md').write_text(readme,encoding='utf-8')
    manifest['README.md']=hashlib.sha256((TARGET/'README.md').read_bytes()).hexdigest()
    manifest['EXPERIMENT_README.md']=hashlib.sha256((TARGET/'EXPERIMENT_README.md').read_bytes()).hexdigest()
    (TARGET/'GITHUB_FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    git('add','-f','--','project2/I-PINNs')
    changed=git('diff','--cached','--name-only').splitlines()
    if any(not p.startswith(PREFIX) for p in changed): raise RuntimeError('Refusing to modify files outside authorized folder')
    if changed:
        git('commit','-m','Add I-PINNs experiment '+('results and data' if final else 'framework and interim results'))
    commit=git('rev-parse','HEAD')
    for attempt in range(4):
        try:
            git('push','origin','HEAD:main')
            break
        except RuntimeError:
            if attempt==3: raise
            git('fetch','origin','main')
            git('rebase','origin/main')
            commit=git('rev-parse','HEAD')
    remote=git('ls-remote','origin','refs/heads/main').split()[0]
    if remote!=commit: raise RuntimeError('Remote branch did not confirm pushed commit')
    save_status('uploaded_final' if final else 'uploaded_interim',commit=commit,files=len(manifest),
                url='https://github.com/TTJTR/MTH321_TeamQ/tree/main/project2/I-PINNs')
    print('PUSH VERIFIED',commit,'files',len(manifest),flush=True)
    return commit


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--snapshot',action='store_true')
    args=parser.parse_args()
    if args.snapshot:
        snapshot(False); return
    save_status('waiting_for_experiment')
    while True:
        try: state=json.loads((ROOT/'pipeline_status.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError): state={}
        if state.get('stage')=='finished': break
        time.sleep(30)
    for attempt in range(10):
        try:
            commit=snapshot(True); break
        except Exception as error:
            save_status('upload_retry',attempt=attempt+1,error=str(error))
            print('UPLOAD RETRY',attempt+1,str(error),flush=True)
            if attempt==9: raise
            time.sleep(60)
    receipt=dict(utc=datetime.now(timezone.utc).isoformat(),github_commit=commit,
                 experiment_status=state,automatic_download=False,github_upload_verified=True,
                 shutdown_requested=True)
    (ROOT/'github_publish_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    os.sync()
    subprocess.run(['/bin/bash','/usr/bin/shutdown'],check=True)


if __name__=='__main__': main()
