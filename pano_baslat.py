"""Makro Pano baslatici: Streamlit'i calistirir, ciktisini hem konsola hem veri\pano_log.txt'ye (tarih damgali,
2 MB'ta donen) yazar; sunucu beklenmedik sekilde kapanirsa 3 sn sonra yeniden baslatir.
Konsolsuz calisir (pythonw + CREATE_NO_WINDOW); ayni portta sunucu zaten varsa yenisini baslatmaz, yalniz tarayiciyi acar.
Durdurma: pano_durdur.py. Kullanim: pythonw pano_baslat.py [port] [--tarayici]"""
import os
import socket
import threading
import webbrowser
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
LOG = KOK / "veri" / "pano_log.txt"
LIMIT = 2 * 1024 * 1024
ARG = [a for a in sys.argv[1:] if not a.startswith("--")]
port = ARG[0] if ARG else "8502"
TARAYICI = "--tarayici" in sys.argv
PID = KOK / "veri" / ("pano_%s.pid" % port)


def dinliyor():
    s = socket.socket()
    s.settimeout(1)
    try:
        return s.connect_ex(("127.0.0.1", int(port))) == 0
    finally:
        s.close()


def tarayici_ac():
    for _ in range(60):
        if dinliyor():
            break
        time.sleep(1)
    webbrowser.open("http://localhost:%s" % port)


def yaz(f, metin):
    satir = "%s | %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), metin.rstrip("\r\n"))
    f.write(satir)
    f.flush()


def ac():
    LOG.parent.mkdir(exist_ok=True)
    if LOG.exists() and LOG.stat().st_size > LIMIT:
        eski = LOG.with_suffix(".txt.1")
        if eski.exists():
            eski.unlink()
        LOG.rename(eski)
    return open(LOG, "a", encoding="utf-8", errors="replace")


def main():
    if dinliyor():
        if TARAYICI:
            webbrowser.open("http://localhost:%s" % port)
        return
    PID.parent.mkdir(exist_ok=True)
    PID.write_text(str(os.getpid()))
    if TARAYICI:
        threading.Thread(target=tarayici_ac, daemon=True).start()
    cmd = [sys.executable, "-u", "-m", "streamlit", "run", "pano/app.py", "--server.address", "localhost",
           "--server.port", port, "--server.headless", "true", "--browser.gatherUsageStats", "false"]
    while True:
        f = ac()
        yaz(f, "=== baslatiliyor (port %s) ===" % port)
        p = subprocess.Popen(cmd, cwd=str(KOK), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace", bufsize=1,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            for satir in p.stdout:
                if sys.stdout:
                    sys.stdout.write(satir)
                    sys.stdout.flush()
                yaz(f, satir)
                if f.tell() > LIMIT:
                    f.close()
                    f = ac()
            kod = p.wait()
        except KeyboardInterrupt:
            p.terminate()
            yaz(f, "=== Ctrl+C ile durduruldu ===")
            return
        yaz(f, "=== sunucu kapandi (cikis kodu %s); 3 sn sonra yeniden baslatilacak ===" % kod)
        f.close()
        time.sleep(3)


main()
