"""SQLite semasi ve yardimcilar."""
import sqlite3
from datetime import datetime, timezone
from . import yapilandirma as Y

SEMA = """
CREATE TABLE IF NOT EXISTS seri_katalog (
  kod TEXT PRIMARY KEY, ad TEXT, kategori TEXT, birim TEXT, kaynak TEXT, kaynak_kodu TEXT,
  frekans TEXT, kapanis_notu TEXT, para_birimi TEXT, usd_kur_kodu TEXT, usd_kur_ters INTEGER, v1 INTEGER);
CREATE TABLE IF NOT EXISTS gunluk (
  kod TEXT NOT NULL, tarih TEXT NOT NULL, kapanis REAL NOT NULL, cekim_zamani TEXT,
  suphe INTEGER DEFAULT 0, PRIMARY KEY (kod, tarih));
CREATE TABLE IF NOT EXISTS kripto_nabiz (
  sembol TEXT NOT NULL, periyot TEXT NOT NULL, zaman_utc TEXT NOT NULL, fiyat REAL NOT NULL,
  PRIMARY KEY (sembol, periyot, zaman_utc));
CREATE TABLE IF NOT EXISTS cekim_gunlugu (
  id INTEGER PRIMARY KEY AUTOINCREMENT, zaman_utc TEXT, kaynak TEXT, kod TEXT, baslangic TEXT,
  sonuc TEXT, satir INTEGER, hata TEXT);
CREATE TABLE IF NOT EXISTS politika_olaylari (
  kod TEXT NOT NULL, tarih TEXT NOT NULL, onceki REAL, yeni REAL, degisim REAL,
  PRIMARY KEY (kod, tarih));
CREATE INDEX IF NOT EXISTS ix_log_kod ON cekim_gunlugu(kod, id);
"""

def simdi():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def baglan():
    Y.VERI_DIZINI.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(Y.DB_YOLU), timeout=60)
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript(SEMA)
    return c

def baglan_oku():
    """Salt okunur baglanti (pano icin): hicbir sey yazmaz, sema/katalog senkronu yapmaz, yazanlari beklemez.
    Veritabani yoksa/bozuksa normal baglantiya duser."""
    try:
        c = sqlite3.connect("file:%s?mode=ro" % Y.DB_YOLU.as_posix(), uri=True, timeout=30)
        c.execute("PRAGMA busy_timeout=30000")
        c.execute("SELECT 1 FROM seri_katalog LIMIT 1")
        return c
    except sqlite3.Error:
        return baglan()

def katalogu_yaz(c):
    cols = ["kod", "ad", "kategori", "birim", "kaynak", "kaynak_kodu", "frekans", "kapanis_notu",
            "para_birimi", "usd_kur_kodu", "usd_kur_ters", "v1"]
    c.executemany("INSERT OR REPLACE INTO seri_katalog (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))),
                  [tuple(k[x] for x in cols) for k in Y.KATALOG])
    c.commit()

def log_yaz(c, kaynak, kod, baslangic, sonuc, satir=0, hata=None):
    c.execute("INSERT INTO cekim_gunlugu (zaman_utc,kaynak,kod,baslangic,sonuc,satir,hata) VALUES (?,?,?,?,?,?,?)",
              (simdi(), kaynak, kod, baslangic, sonuc, satir, hata))
    c.commit()
    satir_txt = "%s | %s | %s | %s | satir=%s%s" % (simdi(), kaynak, kod, sonuc, satir, (" | " + str(hata)[:300]) if hata else "")
    with open(Y.LOG_YOLU, "a", encoding="utf-8") as f:
        f.write(satir_txt + "\n")

def son_tarih(c, kod):
    r = c.execute("SELECT MAX(tarih) FROM gunluk WHERE kod=?", (kod,)).fetchone()[0]
    return r

def yaz_gunluk(c, kod, seri, birim):
    """seri: index=tarih (tz'siz), deger=float. Dogrulayip upsert eder. (yazilan, atilan, suphe) doner."""
    import pandas as pd
    s = seri.dropna()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    bugun = pd.Timestamp(datetime.now(timezone.utc).date()) + pd.Timedelta(days=1)
    atilan = int((s.index > bugun).sum())
    s = s[s.index <= bugun]
    if birim == "fiyat":
        atilan += int((s <= 0).sum())
        s = s[s > 0]
    suphe = pd.Series(0, index=s.index)
    if birim == "fiyat" and len(s) > 1:
        suphe = ((s.pct_change().abs() > Y.SUPHE_GETIRI)).astype(int)
    z = simdi()
    c.executemany("INSERT OR REPLACE INTO gunluk (kod,tarih,kapanis,cekim_zamani,suphe) VALUES (?,?,?,?,?)",
                  [(kod, d.strftime("%Y-%m-%d"), float(v), z, int(suphe[d])) for d, v in s.items()])
    c.commit()
    return len(s), atilan, int(suphe.sum())
