"""Okuma arayuzu (diger moduller buna bagimli; imzalar sabit)."""
import pandas as pd
from . import yapilandirma as Y, db


def _c():
    return db.baglan_oku()


def katalog() -> pd.DataFrame:
    """Seri katalogu. usd_kur_ters: False = kur USD-basina-yerel (USD deger = yerel / kur);
    True = kur yerel-basina-USD (USD deger = yerel * kur)."""
    c = _c()
    if c.execute("SELECT COUNT(*) FROM seri_katalog").fetchone()[0] != len(Y.KATALOG):
        # yalniz eksikse (toplayici henuz calismamis): tek seferlik senkron, ayri yazma baglantisiyla
        c.close()
        w = db.baglan()
        db.katalogu_yaz(w)
        w.close()
        c = _c()
    d = pd.read_sql("SELECT kod, ad, kategori, birim, kaynak, frekans, kapanis_notu, para_birimi, "
                    "usd_kur_kodu, usd_kur_ters, v1, kaynak_kodu FROM seri_katalog ORDER BY rowid", c)
    c.close()
    d = d.astype(object).where(d.notna(), None)
    d["usd_kur_ters"] = d["usd_kur_ters"].astype(bool)
    d["v1"] = d["v1"].astype(bool)
    return d


def gunluk_panel(kodlar=None, baslangic=None, bitis=None) -> pd.DataFrame:
    """Genis tablo: index = tz'siz gunluk tarih, sutun = seri kodu, deger = ham kapanis/seviye. Ileri doldurma yok."""
    c = _c()
    if kodlar is None:
        kodlar = [r[0] for r in c.execute("SELECT kod FROM seri_katalog WHERE v1=1 ORDER BY rowid")]
    kodlar = list(kodlar)
    q = "SELECT kod, tarih, kapanis FROM gunluk WHERE kod IN (%s)" % ",".join("?" * len(kodlar))
    p = list(kodlar)
    if baslangic is not None:
        q += " AND tarih >= ?"
        p.append(pd.Timestamp(baslangic).strftime("%Y-%m-%d"))
    if bitis is not None:
        q += " AND tarih <= ?"
        p.append(pd.Timestamp(bitis).strftime("%Y-%m-%d"))
    d = pd.read_sql(q, c, params=p)
    c.close()
    w = d.pivot(index="tarih", columns="kod", values="kapanis")
    w.index = pd.DatetimeIndex(pd.to_datetime(w.index), name="tarih")
    w.columns.name = None
    return w.reindex(columns=kodlar).sort_index()


def nabiz(semboller=None, son_saat=24, periyot="1m") -> pd.DataFrame:
    """Uzun format: zaman_utc, sembol, fiyat. periyot '1m' (varsayilan) ya da '1h'."""
    c = _c()
    esik = (pd.Timestamp.now("UTC").tz_localize(None) - pd.Timedelta(hours=son_saat)).strftime("%Y-%m-%dT%H:%M:%S")
    q = "SELECT zaman_utc, sembol, fiyat FROM kripto_nabiz WHERE periyot=? AND zaman_utc>=?"
    p = [periyot, esik]
    if semboller is not None:
        semboller = list(semboller)
        q += " AND sembol IN (%s)" % ",".join("?" * len(semboller))
        p += semboller
    d = pd.read_sql(q + " ORDER BY zaman_utc, sembol", c, params=p)
    c.close()
    d["zaman_utc"] = pd.to_datetime(d["zaman_utc"])
    return d


def saglik() -> pd.DataFrame:
    """v1 serileri icin: kod, son_tarih, son_basarili_cekim, son_hata, durum (ok|gecikmis|hata)."""
    c = _c()
    kat = pd.read_sql("SELECT kod, frekans FROM seri_katalog WHERE v1=1 ORDER BY rowid", c)
    son = pd.read_sql("SELECT kod, MAX(tarih) AS son_tarih FROM gunluk GROUP BY kod", c).set_index("kod")["son_tarih"]
    lg = pd.read_sql("SELECT id, zaman_utc, kod, sonuc, hata FROM cekim_gunlugu ORDER BY id", c)
    c.close()
    bugun = pd.Timestamp.now().normalize()
    satir = []
    for _, k in kat.iterrows():
        g = lg[lg["kod"] == k["kod"]]
        basarili = g[g["sonuc"] == "ok"]
        hata = g[g["sonuc"] == "hata"]
        son_basarili = basarili["zaman_utc"].iloc[-1] if len(basarili) else None
        son_hata = hata["hata"].iloc[-1] if len(hata) else None
        sonuc_son = g["sonuc"].iloc[-1] if len(g) else None
        st = son.get(k["kod"])
        if sonuc_son == "hata" or st is None:
            durum = "hata"
        elif (bugun - pd.Timestamp(st)).days > Y.BAYAT_GUN[k["frekans"]]:
            durum = "gecikmis"
        else:
            durum = "ok"
        satir.append((k["kod"], st, son_basarili, son_hata, durum))
    return pd.DataFrame(satir, columns=["kod", "son_tarih", "son_basarili_cekim", "son_hata", "durum"])
