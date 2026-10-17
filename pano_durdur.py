"""Makro Pano sunucusunu durdurur: yalniz bu portu dinleyen sunucuyu ve onun baslaticisini (pid dosyasi) oldurur.
Baska python surecleri (statarb, zamanlanmis gorevler) etkilenmez. Kullanim: pano_durdur.py [port]"""
import re
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
port = sys.argv[1] if len(sys.argv) > 1 else "8502"
NW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
pids = []
pf = KOK / "veri" / ("pano_%s.pid" % port)
if pf.exists():
    try:
        pids.append(int(pf.read_text().strip()))  # baslatici once: yoksa sunucuyu yeniden baslatir
    except ValueError:
        pass
out = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, creationflags=NW).stdout
for ln in out.splitlines():
    m = re.search(r"127\.0\.0\.1:%s\s+\S+\s+LISTENING\s+(\d+)" % port, ln) or re.search(r"\[::1\]:%s\s+\S+\s+LISTENING\s+(\d+)" % port, ln)
    if m:
        pids.append(int(m.group(1)))
for p in pids:
    subprocess.run(["taskkill", "/PID", str(p), "/T", "/F"], capture_output=True, creationflags=NW)
try:
    pf.unlink()
except OSError:
    pass
