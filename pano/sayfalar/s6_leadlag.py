import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import leadlag  # noqa: E402

# Ekonomik olarak mantikli, onceden tanimli ciftler (X -> Y: X, Y'yi onden gider mi?)
ONERILEN = [("SPX", "NIKKEI"), ("SPX", "HANGSENG"), ("SPX", "SHANGHAI"), ("SPX", "DAX"), ("SPX", "FTSE"),
            ("SPX", "BIST100"), ("SPX", "BOVESPA"), ("SPX", "NIFTY"), ("DXY", "USDTRY"), ("DXY", "USDBRL"),
            ("DXY", "USDZAR"), ("DXY", "USDINR"), ("DXY", "USDCNY"), ("BTC", "NASDAQ"), ("NASDAQ", "BTC"),
            ("VIX", "BTC"), ("XAUUSD", "DXY")]

ortak.sayfa_basi("6 Lead-Lag (sınırlı)",
                 "Asya ABD'den önce kapandığı için 'ABD bugün, Asya yarın' görünümü çoğu zaman saat farkından kaynaklanır, "
                 "öngörü değildir.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
ev = ortak.evren_kodlari(kat)
et = ortak.kod_etiket(kat)

mevcut = [p for p in ONERILEN if p[0] in ev and p[1] in ev]
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    secim = st.selectbox("Çift (X -> Y)", ["%s -> %s" % p for p in mevcut] + ["Özel çift..."])
with c2:
    frek = st.radio("Frekans", ["günlük", "haftalık"], horizontal=True)
with c3:
    maxk = st.slider("Gecikme aralığı (±)", 1, 5, 3)
if secim == "Özel çift...":
    cc1, cc2 = st.columns(2)
    x = cc1.selectbox("X", ev, index=ev.index("SPX"), format_func=et)
    y = cc2.selectbox("Y", ev, index=ev.index("NIKKEI"), format_func=et)
    st.caption("Özel çift: tüm çiftleri tarayıp 'en iyi lead-lag'ı aramak bu ekranın amacı değildir; önceden mantıklı bir hipotez seçin.")
else:
    x, y = secim.split(" -> ")
if x == y:
    st.info("Farklı iki varlık seçin.")
    st.stop()

g = ortak.getiri_tum(a.dmg, a.baz) if frek == "günlük" else ortak.haftalik_tum(a.dmg, a.baz)
birim = "gün" if frek == "günlük" else "hafta"
cc = leadlag.capraz_korelasyon(g, x, y, gecikmeler=tuple(range(-maxk, maxk + 1)), yontem=a.yontem, katalog=kat,
                               min_gozlem=30)
renk = ["#bdbdbd" if not np.isfinite(r) else ("#1b5fb5" if an else "#7fa7d9") for r, an in zip(cc["r"], cc["anlamli"])]
fig = go.Figure(go.Bar(x=cc["gecikme"], y=cc["r"], marker_color=renk,
                       error_y=dict(type="data", symmetric=False, array=(cc["ust"] - cc["r"]).fillna(0), arrayminus=(cc["r"] - cc["alt"]).fillna(0)),
                       customdata=np.c_[cc["n"], cc["p"]],
                       hovertemplate="k=%{x}<br>r=%{y:.3f}<br>n=%{customdata[0]}<br>p=%{customdata[1]:.3f}<extra></extra>"))
fig.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10),
                  title=dict(text="corr(%s(t-k), %s(t)) - k>0: %s, %s'yi k %s önden gider (%s, %s)" % (
                      x, y, x, y, birim, frek, a.baz), font=dict(size=13)),
                  xaxis=dict(title="gecikme k (%s)" % birim, dtick=1), yaxis_title="korelasyon")
ortak.goster(fig)
st.caption("Koyu mavi: p<0,05 (çoklu test düzeltmesiz; %d gecikme birlikte bakıldığı için bir kısmı tesadüf olabilir). Açık mavi: anlamlı değil. "
           "Gri: yetersiz gözlem. Hata çubuğu yaklaşık %%95 Fisher aralığıdır." % len(cc))
t = cc.rename(columns={"gecikme": "k", "alt": "alt %95", "ust": "üst %95", "anlamli": "p<0,05"}).drop(columns=["uyari"])
ortak.tablo(t, hide_index=True)

st.subheader("Kapanış saatleri")
k = kat.set_index("kod")["kapanis_notu"]
ca, cb = st.columns(2)
ca.markdown("**%s**: %s" % (x, k.get(x)))
cb.markdown("**%s**: %s" % (y, k.get(y)))
st.info(leadlag.kapanis_uyarisi(kat, x, y))
if frek == "günlük":
    st.caption("Haftalık (örtüşmeyen 5 günlük) seçeneği saat farkı etkisini büyük ölçüde azaltır.")
st.info("Metodoloji: yalnız gecikmeli çapraz korelasyon (Granger testi v1'de yok); t-k...t+k her zaman birlikte gösterilir; "
        "bulgu sonraki dönemde tekrar test edilmeden 'kural' sayılmaz.")
ortak.sayfa_sonu("k=0 eşzamanlı ilişkidir. k>0 çubukları, X'in geçmiş getirisinin Y'nin bugünkü getirisiyle ilişkisini; k<0 çubukları "
                 "tersini gösterir. Piyasalar farklı saatlerde kapandığı için k=±1'deki ilişkinin büyük kısmı saat farkıdır. "
                 "Güçlü bir k≠0 çubuğunu yalnızca haftalık veride de görüyorsanız ciddiye alın.")
