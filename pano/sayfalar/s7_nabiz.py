import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import korelasyon  # noqa: E402
from toplayici import oku  # noqa: E402

YAHOO = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "DXY": "DX-Y.NYB", "USD/TRY": "TRY=X", "EUR/USD": "EURUSD=X",
         "VIX": "^VIX", "ABD 10y (^TNX)": "^TNX", "Altın (GC=F)": "GC=F", "Brent (BZ=F)": "BZ=F", "BIST 100": "XU100.IS"}


@st.cache_data(ttl=300, show_spinner="Yahoo'dan gecikmeli değerler çekiliyor...")
def yahoo_anlik():
    """Yahoo'dan o an cekilen gecikmeli degerler. Veri tabanina YAZILMAZ."""
    import yfinance as yf
    out, hata = [], None
    try:
        d = yf.download(list(YAHOO.values()), period="5d", interval="15m", progress=False, group_by="ticker",
                        threads=True, auto_adjust=False, timeout=10)
        for ad, t in YAHOO.items():
            try:
                s = d[t]["Close"].dropna()
                if s.empty:
                    continue
                son_gun = s.index[-1].date()
                onceki = s[[i.date() < son_gun for i in s.index]]
                out.append(dict(varlık=ad, ticker=t, değer=float(s.iloc[-1]), zaman=s.index[-1].tz_convert("UTC").strftime("%Y-%m-%d %H:%M UTC"),
                                gün_değişim=(float(s.iloc[-1] / onceki.iloc[-1] - 1) * 100 if len(onceki) else np.nan)))
            except Exception:
                continue
    except Exception as e:
        hata = str(e)[:200]
    return pd.DataFrame(out), hata, datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


@st.cache_data(show_spinner="Tarihsel dağılım hesaplanıyor...")
def ort_kor_gecmisi(dmg, baz, pencere, yontem, adim=21, yil=8):
    g = ortak.getiri_tum(dmg, baz)
    bas = max(pencere + 10, len(g) - 252 * yil)
    out = {}
    for e in range(len(g), bas, -adim):
        c, _ = korelasyon.korelasyon_matrisi(g.iloc[:e], pencere, None, yontem)
        out[g.index[e - 1]] = korelasyon.ortalama_ikili_korelasyon(c)
    return pd.Series(out).sort_index().dropna()


def yuzdelik(seri, deger):
    s = seri.dropna()
    return float((s <= deger).mean() * 100) if len(s) and np.isfinite(deger) else np.nan


def bayrak(p):
    if not np.isfinite(p):
        return "-"
    return "olağan dışı" if (p <= 5 or p >= 95) else "olağan"


ortak.sayfa_basi("7 Piyasa Nabzı",
                 "Kripto dışındaki fiyatlar ~15 dk gecikmeli ve yalnız seans saatlerinde güncellenir. 'Olağan dışı' bayrağı bir "
                 "işlem sinyali değildir.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Yenile (canlı veriyi yeniden çek)"):
        yahoo_anlik.clear()
with c2:
    para = st.radio("Görüntü para birimi (fiyat kutuları)", ["USD", "TL"], horizontal=True)

# ---- tarihsel özet kutuları
st.subheader("Tarihsel özet (günlük kapanış verisinden)")
g = ortak.getiri_tum(a.dmg, a.baz)
h60 = ort_kor_gecmisi(a.dmg, a.baz, 60, a.yontem)
h250 = ort_kor_gecmisi(a.dmg, a.baz, 250, a.yontem)
ort_now = {}
for p in (60, 250):
    c, _ = korelasyon.korelasyon_matrisi(g, p, None, a.yontem)
    ort_now[p] = korelasyon.ortalama_ikili_korelasyon(c)
bs = korelasyon.ikili_rolling(g, "BTC", "SPX", pencere=60, yontem=a.yontem)
bs_son = bs.dropna(subset=["korelasyon"]).tail(1)
vix = panel["VIX"].dropna()
dxy = panel["DXY"].dropna()
try_ = panel["USDTRY"].dropna()
usdtry_ch = np.log(try_).diff(60).dropna()
dxy_ch = np.log(dxy).diff(60).dropna()

kutular = [
    ("Ort. ikili korelasyon 60g", ort_now[60], yuzdelik(h60, ort_now[60]), "%.3f", "tarihsel dağılım: son ~8 yıl, aylık örnek"),
    ("Ort. ikili korelasyon 250g", ort_now[250], yuzdelik(h250, ort_now[250]), "%.3f", "tarihsel dağılım: son ~8 yıl, aylık örnek"),
    ("VIX (seviye)", vix.iloc[-1], yuzdelik(vix, vix.iloc[-1]), "%.1f", "seviye, 2010'dan bugüne yüzdelik"),
    ("DXY (seviye)", dxy.iloc[-1], yuzdelik(dxy, dxy.iloc[-1]), "%.2f", "yüzdelik: 60g log değişimin dağılımına göre (DXY değişim %%%.1f)" % (100 * dxy_ch.iloc[-1])),
    ("USD/TRY (seviye)", try_.iloc[-1], yuzdelik(usdtry_ch, usdtry_ch.iloc[-1]), "%.2f", "yüzdelik: 60g log değişimin dağılımına göre (değişim %%%.1f)" % (100 * usdtry_ch.iloc[-1])),
    ("BTC-S&P500 60g korelasyon", bs_son["korelasyon"].iloc[0] if len(bs_son) else np.nan,
     yuzdelik(bs["korelasyon"], bs_son["korelasyon"].iloc[0]) if len(bs_son) else np.nan, "%.2f", "kendi 60g geçmişine göre"),
]
cols = st.columns(3)
for i, (ad, deger, p, fmt, aciklama) in enumerate(kutular):
    with cols[i % 3]:
        st.metric(ad, "-" if not np.isfinite(deger) else fmt % deger,
                  "yüzdelik %.0f - %s" % (p, bayrak(p)) if np.isfinite(p) else "yüzdelik hesaplanamadı", delta_color="off")
        n_txt = ("n=%d" % int(bs_son["n"].iloc[0])) if ad.startswith("BTC") and len(bs_son) else ""
        st.caption("%s %s | son veri: %s" % (aciklama, n_txt, panel.index.max().date() if not ad.startswith("BTC") else g.index[-1].date()))
ortak.goster(go.Figure([go.Scatter(x=h60.index, y=h60.values, name="60g", line=dict(color="#d95f02")),
                        go.Scatter(x=h250.index, y=h250.values, name="250g", line=dict(color="#1b5fb5"))]).update_layout(
    height=260, margin=dict(l=10, r=10, t=30, b=10), title=dict(text="Ortalama ikili korelasyon (aylık örneklenmiş)", font=dict(size=13))))
st.caption("Yüzdelik: bugünkü değerin kendi tarihsel dağılımındaki yeri (<=5 ya da >=95 'olağan dışı'). Bu bayrak bir sinyal değildir.")

# ---- kripto nabzı (veritabanı)
st.subheader("Kripto nabzı (Binance, veri tabanından)")
nb = oku.nabiz(["BTC", "ETH", "SOL"], son_saat=24, periyot="1m")
usdtry_son = float(try_.iloc[-1])
kur = usdtry_son if para == "TL" else 1.0
if nb.empty:
    st.warning("Son 24 saatte kripto nabız verisi yok; 'python -m toplayici nabiz' görevinin çalıştığını kontrol edin.")
else:
    simdi = pd.Timestamp.now("UTC").tz_localize(None)
    cc = st.columns(3)
    for col, s in zip(cc, ["BTC", "ETH", "SOL"]):
        d = nb[nb["sembol"] == s]
        if d.empty:
            col.metric(s, "veri yok")
            continue
        son = d.iloc[-1]
        ilk = d.iloc[0]
        yas = (simdi - son["zaman_utc"]).total_seconds() / 60
        col.metric("%s (%s)" % (s, para), "{:,.2f}".format(son["fiyat"] * kur), "%+.2f%% / 24s" % ((son["fiyat"] / ilk["fiyat"] - 1) * 100))
        col.caption("son nokta: %s (%.0f dk önce)%s" % (son["zaman_utc"].strftime("%m-%d %H:%M") + "Z (TR " + son["zaman_utc"].tz_localize("UTC").astimezone(ortak.TR).strftime("%H:%M") + ")", yas, " - STALE" if yas > 180 else ""))
    f = go.Figure()
    for s in ["BTC", "ETH", "SOL"]:
        d = nb[nb["sembol"] == s]
        if len(d):
            f.add_trace(go.Scatter(x=d["zaman_utc"], y=100 * d["fiyat"] / d["fiyat"].iloc[0], name=s, line=dict(width=1.2)))
    f.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), title=dict(text="Son 24 saat (1 dk mum, başlangıç=100)", font=dict(size=13)))
    ortak.goster(f)
    if para == "TL":
        st.caption("TL değeri son günlük USDTRY kapanışı (%.4f, %s) ile çarpılarak hesaplanır; saatlik kur değildir." % (usdtry_son, try_.index[-1].date()))

# ---- gecikmeli Yahoo
st.subheader("Gecikmeli piyasa değerleri (Yahoo, anlık çekim)")
df, hata, saat = yahoo_anlik()
if df.empty:
    st.warning("Yahoo'dan değer alınamadı%s. Tarihsel kutular ve kripto nabzı etkilenmez." % (": " + hata if hata else ""))
else:
    gos = df.copy()
    if para == "TL":
        try_canli = df.loc[df["ticker"] == "TRY=X", "değer"]
        k = float(try_canli.iloc[0]) if len(try_canli) else usdtry_son
        usd_kal = df["ticker"].isin(["^GSPC", "^IXIC", "GC=F", "BZ=F"])
        gos.loc[usd_kal, "değer"] = gos.loc[usd_kal, "değer"] * k
        st.caption("TL görünümü: ABD endeksleri, altın ve Brent canlı USD/TRY (%.4f) ile çarpıldı; diğer satırlar kendi biriminde." % k)
    gos["etiket"] = "gecikmeli (~15 dk), veri tabanına yazılmaz"
    gos = gos.rename(columns={"gün_değişim": "gün değişim %"})
    ortak.tablo(gos, hide_index=True, column_config={
        "değer": st.column_config.NumberColumn(format="%.4f"), "gün değişim %": st.column_config.NumberColumn(format="%+.2f")})
    st.caption("Çekim saati: %s (5 dk önbellek). Seans dışında son kapanış görünür. Bu değerler tarihsel verinin parçası değildir ve "
               "hiçbir hesaba girmez." % saat)

st.info("Metodoloji: canlı/gecikmeli değerler ile tarihsel günlük veri aynı tabloda karıştırılmaz; canlı değer veri tabanına yazılmaz. "
        "Kripto 21:00 UTC referansı günlük analizde kullanılır, burada ise anlık 1 dk fiyat gösterilir.")
ortak.sayfa_sonu("Üst kutular bugünün özetidir ve her biri kendi tarihsel dağılımına göre yüzdelik konumunu gösterir: yüzdelik 95 ise geçmişteki "
                 "değerlerin %95'i bugünden küçüktür. 'Olağan dışı' yalnızca uç bir konumu anlatır. Alttaki tablolar canlı/gecikmeli veridir.")
