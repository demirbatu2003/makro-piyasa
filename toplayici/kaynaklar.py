"""Kaynak istemcileri: Yahoo, FRED, BIS, Binance, EVDS. Hepsi pandas Series / DataFrame doner."""
import io
import time
import requests
import pandas as pd
from . import yapilandirma as Y

def _tekrar(fn, *a, **k):
    son = None
    for i in range(Y.DENEME):
        try:
            return fn(*a, **k)
        except Exception as e:  # noqa
            son = e
            time.sleep(2 * (i + 1) ** 2)
    raise son

FX_KAYMA_BASLANGIC = pd.Timestamp("2010-07-30")

def fx_tarih_duzelt(s):
    """Yahoo "=X" gunluk cubuklari 2010-08'den beri bir is gunu ileri etiketli (etiket D'deki deger
    D'den onceki is gununun ABD kapanisidir). Kural: etiket >= 2010-08-02 ise onceki is gunune kaydir
    (Pzt->Cum, Cts/Paz->Cum; cakisirsa sonraki cubuk kazanir). 2010-07-30 cubugu gecis cakismasi
    oldugu icin atilir; daha eski etiketler dogru (hafta sonu olanlar atilir)."""
    eski = s[s.index < FX_KAYMA_BASLANGIC]
    eski = eski[eski.index.dayofweek < 5]
    yeni = s[s.index > FX_KAYMA_BASLANGIC].copy()
    yeni.index = yeni.index - pd.offsets.BDay(1)
    out = pd.concat([eski, yeni])
    return out[~out.index.duplicated(keep="last")].sort_index()

def yahoo(ticker, baslangic):
    import yfinance as yf
    def f():
        h = yf.Ticker(ticker).history(start=baslangic, interval="1d", auto_adjust=False, actions=False, timeout=Y.ZAMAN_ASIMI)
        if h is None or h.empty:
            raise ValueError("Yahoo bos yanit: " + ticker)
        s = h["Close"].copy()
        s.index = pd.DatetimeIndex(s.index).tz_localize(None).normalize()
        if ticker.endswith("=X"):
            s = fx_tarih_duzelt(s)
        else:
            s = s[s.index.dayofweek < 5]   # hafta sonu Yahoo cubuklari (kismi/sahte) atilir
        return s
    return _tekrar(f)

def fred(seri_id, baslangic):
    def f():
        r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": seri_id, "cosd": baslangic},
                         timeout=Y.ZAMAN_ASIMI)
        r.raise_for_status()
        d = pd.read_csv(io.StringIO(r.text))
        if d.shape[1] != 2:
            raise ValueError("FRED beklenmeyen bicim: " + seri_id)
        s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0]))
        if s.dropna().empty:
            raise ValueError("FRED bos: " + seri_id)
        return s
    return _tekrar(f)

def bis(ulke, baslangic):
    def f():
        r = requests.get("https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/M." + ulke,
                         params={"format": "csv", "startPeriod": baslangic[:7]}, timeout=Y.ZAMAN_ASIMI)
        r.raise_for_status()
        d = pd.read_csv(io.StringIO(r.text))
        if "TIME_PERIOD" not in d or d.empty:
            raise ValueError("BIS bos/bicim hatasi: " + ulke)
        s = pd.Series(pd.to_numeric(d["OBS_VALUE"], errors="coerce").values, index=pd.to_datetime(d["TIME_PERIOD"] + "-01"))
        return s
    return _tekrar(f)

def evds(seri, baslangic):
    """EVDS (dogrulanmadi; key gerekir)."""
    def f():
        bas = pd.Timestamp(baslangic).strftime("%d-%m-%Y")
        bit = pd.Timestamp.now().strftime("%d-%m-%Y")
        r = requests.get("https://evds2.tcmb.gov.tr/service/evds/", headers={"key": Y.EVDS_KEY},
                         params={"series": seri, "startDate": bas, "endDate": bit, "type": "json"}, timeout=Y.ZAMAN_ASIMI)
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            raise ValueError("EVDS bos yanit")
        d = pd.DataFrame(items)
        col = [c for c in d.columns if c != "Tarih" and not c.startswith("UNIXTIME")][0]
        return pd.Series(pd.to_numeric(d[col], errors="coerce").values, index=pd.to_datetime(d["Tarih"], format="%d-%m-%Y"))
    return _tekrar(f)

def _binance_get(yol, params):
    son = None
    for taban in Y.BINANCE_TABANLAR:
        try:
            r = requests.get(taban + yol, params=params, timeout=Y.ZAMAN_ASIMI)
            if r.status_code == 200:
                return r.json()
            son = RuntimeError("Binance %s %s" % (r.status_code, r.text[:120]))
        except Exception as e:  # noqa
            son = e
    raise son

def binance_klines(sembol, aralik, bas_ms, bit_ms=None):
    """Sayfalayarak kline ceker. DataFrame: zaman (UTC, tz'siz), acilis, kapanis."""
    ara = {"1m": 60_000, "1h": 3_600_000}[aralik]
    satirlar = []
    imlec = int(bas_ms)
    while True:
        p = {"symbol": sembol, "interval": aralik, "startTime": imlec, "limit": 1000}
        if bit_ms:
            p["endTime"] = int(bit_ms)
        veri = _tekrar(_binance_get, "/api/v3/klines", p)
        if not veri:
            break
        satirlar += [(x[0], float(x[1]), float(x[4])) for x in veri]
        imlec = veri[-1][0] + ara
        if len(veri) < 1000:
            break
        time.sleep(0.05)
    if not satirlar:
        return pd.DataFrame(columns=["zaman", "acilis", "kapanis"])
    d = pd.DataFrame(satirlar, columns=["ms", "acilis", "kapanis"])
    d["zaman"] = pd.to_datetime(d["ms"], unit="ms")
    return d[["zaman", "acilis", "kapanis"]].drop_duplicates("zaman")
