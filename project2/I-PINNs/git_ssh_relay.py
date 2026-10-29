"""Git SSH transport over a local-only forwarded stream; stores no credentials."""
import json
import os
from pathlib import Path
import shlex
import socket
import sys
import threading

command=shlex.split(sys.argv[-1])
if len(command)!=2 or command[0] not in {'git-upload-pack','git-receive-pack'} or command[1]!='TTJTR/MTH321_TeamQ.git':
    raise SystemExit('Relay permits only the authorized repository Git services')
config=json.loads((Path(__file__).resolve().parent.parent/'github_relay_endpoint.json').read_text())
sock=socket.create_connection(('127.0.0.1',config['port']),timeout=30)
sock.settimeout(None)
sock.sendall((json.dumps({'service':command[0]})+'\n').encode())


def send():
    try:
        while True:
            data=os.read(0,65536)
            if not data: break
            sock.sendall(data)
    finally:
        try: sock.shutdown(socket.SHUT_WR)
        except OSError: pass


threading.Thread(target=send,daemon=True).start()
while True:
    data=sock.recv(65536)
    if not data: break
    sys.stdout.buffer.write(data); sys.stdout.buffer.flush()
sock.close()
