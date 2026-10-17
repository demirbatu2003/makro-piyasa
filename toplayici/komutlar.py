"""Komutlar: gunluk, nabiz, durum."""
import time
import traceback
import pandas as pd
from . import yapilandirma as Y, db, kaynaklar as K, oku


def _baslangic(c, kod):
    son = db.son_tarih(c, kod)
    if son is None:
        return Y.BASLANGIC
    b = pd.Timestamp(son) - pd.Timedelta(days=Y.GERI_BINDIRME_GUN)
    return max(b, pd.Timestamp(Y.BASLANGIC)).strftime("%Y-%m-%d")


def _kripto_gunluk(sembol, baslangic):
    bas_ms = int(pd.Timestamp(baslangic, tz="UTC").timestamp() * 1000)
    if baslangic == Y.BASLANGIC:
        bas_ms = int(pd.Timestamp("2017-08-01", tz="UTC").timestamp() * 1000)
    d = K.binance_klines(sembol, "1h", bas_ms)
    if d.empty:
        raise ValueError("Binance bos yanit: " + sembol)
    d = d[d["zaman"].dt.hour == Y.KRIPTO_REFERANS_SAAT_UTC]
    s = pd.Series(d["acilis"].values, index=d["zaman"].dt.normalize())   # 21:00:00 anindaki fiyat
    return s[s.index >= pd.Timestamp(Y.BASLANGIC)]


def _seri_cek(k, baslangic):
    kay, kk = k["kaynak"], k["kaynak_kodu"]
    if kay == "yahoo":
        return K.yahoo(kk, baslangic)
    if kay == "fred":
        return K.fred(kk, baslangic)
    if kay == "bis":
        return K.bis(kk.split(".")[-1], baslangic)
    if kay == "binance":
        return _kripto_gunluk(kk, baslangic)
    if kay == "evds":
        return K.evds(kk, baslangic)
    raise ValueError("bilinmeyen kaynak " + kay)


def _turetilmis(c):
    """Gram altin ve altcoin sepeti; DB'deki ham serilerden tamamen yeniden hesaplanir."""
    try:
        g = pd.read_sql("SELECT kod,tarih,kapanis FROM gunluk WHERE kod IN ('XAUUSD','USDTRY')", c)
        w = g.pivot(index="tarih", columns="kod", values="kapanis").dropna()
        gram = pd.Series((w["XAUUSD"] * w["USDTRY"] / 31.1035).values, index=pd.to_datetime(w.index))
        n = db.yaz_gunluk(c, "GRAMALTIN", gram, "fiyat")
        db.log_yaz(c, "turetilmis", "GRAMALTIN", "tum", "ok", n[0])
    except Exception as e:
        db.log_yaz(c, "turetilmis", "GRAMALTIN", "tum", "hata", 0, repr(e))
    try:
        g = pd.read_sql("SELECT kod,tarih,kapanis FROM gunluk WHERE kod LIKE 'ALT!_%' ESCAPE '!'", c)
        w = g.pivot(index="tarih", columns="kod", values="kapanis")
        w.index = pd.to_datetime(w.index)
        w = w.reindex(pd.date_range(w.index.min(), w.index.max(), freq="D"))
        r = w.pct_change(fill_method=None)
        sayi = r.notna().sum(axis=1)
        ort = r.mean(axis=1)
        ort[sayi < Y.ALTSEPET_MIN_COIN] = float("nan")
        ilk = ort.first_valid_index()
        sepet = 100 * (1 + ort.loc[ilk:].fillna(0)).cumprod()
        sepet = sepet[sepet.index.isin(w.index[w.notna().any(axis=1)])]
        n = db.yaz_gunluk(c, "ALTSEPET", sepet, "fiyat")
        db.log_yaz(c, "turetilmis", "ALTSEPET", "tum", "ok", n[0])
    except Exception as e:
        db.log_yaz(c, "turetilmis", "ALTSEPET", "tum", "hata", 0, repr(e))


def _politika_olaylari(c):
    c.execute("DELETE FROM politika_olaylari")
    for k in Y.KATALOG:
        if k["kategori"] != "politika":
            continue
        d = pd.read_sql("SELECT tarih,kapanis FROM gunluk WHERE kod=? ORDER BY tarih", c, params=(k["kod"],))
        if len(d) < 2:
            continue
        fark = d["kapanis"].diff()
        ol = d[fark.abs() > 1e-9]
        c.executemany("INSERT OR REPLACE INTO politika_olaylari VALUES (?,?,?,?,?)",
                      [(k["kod"], d.loc[i, "tarih"], float(d.loc[i, "kapanis"] - fark[i]), float(d.loc[i, "kapanis"]), float(fark[i]))
                       for i in ol.index])
    c.commit()


def gunluk(args=None):
    c = db.baglan()
    db.katalogu_yaz(c)
    hatalar = 0
    for k in Y.KATALOG:
        if k["kaynak"] == "turetilmis":
            continue
        kod = k["kod"]
        if k["kaynak"] == "evds" and not Y.EVDS_KEY:
            print("%s: EVDS key yok (MAKRO_EVDS_KEY), atlandi" % kod)
            continue
        bas = _baslangic(c, kod)
        try:
            s = _seri_cek(k, bas)
            s = s[s.index >= pd.Timestamp(bas)]
            yazilan, atilan, suphe = db.yaz_gunluk(c, kod, s, k["birim"])
            db.log_yaz(c, k["kaynak"], kod, bas, "ok", yazilan,
                       ("atilan=%d suphe=%d" % (atilan, suphe)) if (atilan or suphe) else None)
            print("%-12s ok  satir=%d" % (kod, yazilan))
        except Exception as e:
            hatalar += 1
            db.log_yaz(c, k["kaynak"], kod, bas, "hata", 0, repr(e))
            print("%-12s HATA %s" % (kod, e))
        if k["kaynak"] == "yahoo":
            time.sleep(0.3)
    _turetilmis(c)
    _politika_olaylari(c)
    print("bitti, hata sayisi: %d" % hatalar)
    return 0


def _son_zaman(c, sembol, periyot):
    return c.execute("SELECT MAX(zaman_utc) FROM kripto_nabiz WHERE sembol=? AND periyot=?", (sembol, periyot)).fetchone()[0]


def nabiz(args=None):
    c = db.baglan()
    db.katalogu_yaz(c)
    simdi = pd.Timestamp.now("UTC").tz_localize(None)
    for kod in ["BTC", "ETH", "SOL"]:
        pair = kod + "USDT"
        for per, gun in [("1h", Y.NABIZ_1H_GUN), ("1m", Y.NABIZ_1M_GUN)]:
            sinir = simdi - pd.Timedelta(days=gun)
            son = _son_zaman(c, kod, per)
            bas = sinir if son is None else max(sinir, pd.Timestamp(son) - pd.Timedelta(hours=2))
            try:
                d = K.binance_klines(pair, per, int(bas.tz_localize("UTC").timestamp() * 1000))
                c.executemany("INSERT OR REPLACE INTO kripto_nabiz VALUES (?,?,?,?)",
                              [(kod, per, z.strftime("%Y-%m-%dT%H:%M:%S"), float(p)) for z, p in zip(d["zaman"], d["kapanis"])])
                c.execute("DELETE FROM kripto_nabiz WHERE sembol=? AND periyot=? AND zaman_utc<?",
                          (kod, per, sinir.strftime("%Y-%m-%dT%H:%M:%S")))
                c.commit()
                db.log_yaz(c, "binance", "nabiz_%s_%s" % (kod, per), bas.strftime("%Y-%m-%dT%H:%M"), "ok", len(d))
                print("%s %s ok satir=%d" % (kod, per, len(d)))
            except Exception as e:
                db.log_yaz(c, "binance", "nabiz_%s_%s" % (kod, per), bas.strftime("%Y-%m-%dT%H:%M"), "hata", 0, repr(e))
                print("%s %s HATA %s" % (kod, per, e))
    return 0


def durum(args=None):
    c = db.baglan()
    db.katalogu_yaz(c)
    h = oku.saglik()
    n = pd.read_sql("SELECT kod, COUNT(*) AS satir, MIN(tarih) AS ilk FROM gunluk GROUP BY kod", c).set_index("kod")
    h = h.set_index("kod").join(n)
    h["son_hata"] = h["son_hata"].fillna("").str.slice(0, 40)
    h["son_basarili_cekim"] = h["son_basarili_cekim"].fillna("").str.slice(0, 16)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 500)
    print(h[["ilk", "son_tarih", "satir", "durum", "son_basarili_cekim", "son_hata"]].to_string())
    print("\nToplam seri: %d, toplam satir: %d" % (len(h), int(h["satir"].fillna(0).sum())))
    for r in c.execute("SELECT sembol, periyot, COUNT(*), MAX(zaman_utc) FROM kripto_nabiz GROUP BY 1,2").fetchall():
        print("nabiz %s %s: %d satir, son %s" % r)
    return 0


KOMUTLAR = {"gunluk": gunluk, "nabiz": nabiz, "durum": durum}


def main(argv):
    if not argv or argv[0] not in KOMUTLAR:
        print("kullanim: python -m toplayici [gunluk|nabiz|durum]")
        return 2
    try:
        return KOMUTLAR[argv[0]](argv[1:])
    except Exception:
        try:
            Y.VERI_DIZINI.mkdir(parents=True, exist_ok=True)
            with open(Y.LOG_YOLU, "a", encoding="utf-8") as f:
                f.write(db.simdi() + " | KOMUT HATASI | " + traceback.format_exc() + "\n")
        except Exception:
            pass
        raise
