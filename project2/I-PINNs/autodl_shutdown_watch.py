"""Server-local shutdown after the experiment finishes; no downloads or GitHub uploads."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
PID=int(sys.argv[1])
RECEIPT=ROOT/'shutdown_receipt.json'


def pipeline_alive():
    try:
        command=Path(f'/proc/{PID}/cmdline').read_bytes()
        return b'server_pipeline.py' in command
    except FileNotFoundError:
        return False


print(f'Waiting for pipeline PID {PID}; results remain on this server.',flush=True)
while True:
    try:
        status=json.loads((ROOT/'pipeline_status.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):
        status={}
    if status.get('stage')=='finished':
        reason='pipeline finished; results packaged locally'
        break
    if not pipeline_alive():
        reason='pipeline exited unexpectedly; preserve existing artifacts and power off'
        break
    time.sleep(30)

receipt=dict(utc=datetime.now(timezone.utc).isoformat(),reason=reason,
             pipeline_status=status,results_path=str(ROOT),
             automatic_download=False,github_upload=False,shutdown_requested=True)
RECEIPT.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
os.sync()
print(json.dumps(receipt),flush=True)
# This is the provider's shutdown script inspected on this instance.
subprocess.run(['/bin/bash','/usr/bin/shutdown'],check=True)
