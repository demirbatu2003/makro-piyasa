import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from analiz import getiriler  # noqa: E402

AYLIK_FAIZ = ["DE10Y", "JP10Y", "ZA10Y"]
ULKE = {  # ulke: (politika, fx, borsa, ad)
    "ABD": ("FED", "DXY", "SPX"), "Euro Bölgesi": ("ECB", "EURUSD", "DAX"), "Birleşik Krallık": ("BOE", "GBPUSD", "FTSE"),
    "Japonya": ("BOJ", "USDJPY", "NIKKEI"), "Çin": ("PBOC", "USDCNY", "SHANGHAI"), "Türkiye": ("TCMB", "USDTRY", "BIST100"),
    "Brezilya": ("SELIC", "USDBRL", "BOVESPA"), "Hindistan": ("INDIA_REPO", "USDINR", "NIFTY"),
    "Güney Afrika": ("ZA_REPO", "USDZAR", "JSE")}
ULKE_FAIZ = {"Almanya (aylık 10y)": "DE10Y", "Japonya (aylık 10y)": "JP10Y", "G. Afrika (aylık 10y)": "ZA10Y"}

ortak.sayfa_basi("8 Yavaş / Bağlam",
                 "Aylık seriler günlük serilerle doğrudan karşılaştırılamaz. Örnek sayısı küçüktür.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)

# ---------------------------------------------------------------- aylık 10y faizler
st.subheader("Aylık 10 yıllık faizler (DE / JP / ZA)")
bas_t, bit_t = panel.index.min().date(), panel.index.max().date()
aralik = st.date_input("Tarih aralığı", (pd.Timestamp("2015-01-01").date(), bit_t), min_value=bas_t, max_value=bit_t)
bas = pd.Timestamp(aralik[0]) if len(aralik) == 2 else pd.Timestamp(bas_t)
bit = pd.Timestamp(aralik[1]) if len(aralik) == 2 else pd.Timestamp(bit_t)

aylik = panel[AYLIK_FAIZ].dropna(how="all")
f = go.Figure()
for k in AYLIK_FAIZ:
    s = aylik[k].dropna().loc[bas:bit]
    f.add_trace(go.Scatter(x=s.index, y=s.values, name=k, mode="lines+markers", marker=dict(size=3)))
f.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10), yaxis_title="%", title=dict(text="10y getiri (aylık ortalama, ay başı tarihli)", font=dict(size=13)))
ortak.goster(f)
son = {k: aylik[k].dropna().index.max() for k in AYLIK_FAIZ}
st.caption("Son gözlem: " + ", ".join("%s %s" % (k, v.date()) for k, v in son.items()))

# aylık değişim korelasyonu: aylık faiz bp değişimi + aynı ay log getirisi (ay sonu / önceki ay sonu)
ay_seviye = panel.copy()
ay_seviye = ay_seviye.resample("MS").last()
ay_seviye.loc[:, AYLIK_FAIZ] = panel[AYLIK_FAIZ].resample("MS").last()
ref = ["SPX", "DXY", "USDTRY", "BTC", "VIX", "US10Y"]
sec = AYLIK_FAIZ + [r for r in ref if r in panel.columns]
ay = getiriler.getiri_hesapla(ay_seviye[sec].loc[bas:bit], kat, max_bosluk_gun=40, hafta_sonu_at=False)
yontem = a.yontem
n = ay.notna().astype(int).T @ ay.notna().astype(int)
c = ay.corr(method=yontem, min_periods=12)
c = c.where(n >= 24)
fh = go.Figure(go.Heatmap(z=c.to_numpy(float), x=list(c.columns), y=list(c.index), zmin=-1, zmax=1, zmid=0, colorscale="RdBu",
                          customdata=n.to_numpy(), hovertemplate="%{y} / %{x}<br>r=%{z:.2f}<br>n=%{customdata} ay<extra></extra>"))
fh.update_yaxes(autorange="reversed")
fh.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                 title=dict(text="Aylık değişim korelasyonu (%s, faiz: bp değişim; diğer: ay sonu log getirisi)" % yontem.capitalize(), font=dict(size=13)))
fh.update_layout(height=max(520, 60 * len(c) + 150))
ortak.harita_bicim(fh, len(c))
ortak.harita_goster(fh, "s8_aylik")
if True:
    ortak.tablo(n.rename_axis(None).rename_axis(None), height=330)
    st.caption("Tablo: ortak aylık gözlem sayısı. 24 aydan az olan hücreler gri/boş bırakılır. Birkaç yüz değil yalnız onlarca nokta olduğundan "
               "tek bir hücreye güvenilmez. Aylık faiz ay ortalamasıdır, diğer seriler ay sonu değeridir (zamanlama uyumsuzluğu).")

# ---------------------------------------------------------------- politika faizi + FX + borsa
st.subheader("Politika faizi, kur ve borsa")
ulke = st.selectbox("Ülke / bölge", list(ULKE))
pol, fx, bor = ULKE[ulke]
sp = panel[pol].dropna().loc[bas:bit]
ev = ortak.politika_olaylari(a.dmg)
ev = ev[(ev["kod"] == pol) & (ev["tarih"] >= bas) & (ev["tarih"] <= bit)]
seviye = ortak.seviye_tum(a.dmg, "Yerel")  # bağlam grafiği yerel seviyeleri gösterir
fg = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.35, 0.65], vertical_spacing=0.05,
                   specs=[[{}], [{"secondary_y": True}]])
fg.add_trace(go.Scatter(x=sp.index, y=sp.values, line_shape="hv", name=pol, line=dict(color="#555")), row=1, col=1)
for t in ev["tarih"]:
    fg.add_vline(x=t, line_width=0.6, line_dash="dot", line_color="rgba(214,39,40,0.5)")
for kod, sec_y, renk in [(fx, False, "#2a9d8f"), (bor, True, "#3b6fd4")]:
    s = seviye[kod].dropna().loc[bas:bit]
    fg.add_trace(go.Scatter(x=s.index, y=s.values, name=kod, line=dict(color=renk, width=1.2)), row=2, col=1, secondary_y=sec_y)
fg.update_layout(height=560, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.07))
fg.update_yaxes(title_text="faiz %", row=1, col=1)
fg.update_yaxes(title_text=fx, row=2, col=1, secondary_y=False)
fg.update_yaxes(title_text=bor + " (yerel)", row=2, col=1, secondary_y=True)
ortak.goster(fg)
son_pol = panel[pol].dropna()
st.caption("Kırmızı noktalı çizgiler faiz değişim tarihleri (%d adet). BIS serileri aylıktır: tarih ay başıdır, gerçek karar günü değildir; "
           "FED ve ECB günlüktür. Son %s gözlemi: %s%s" % (
               len(ev), pol, son_pol.index.max().date(),
               " - Hindistan repo verisi gecikmelidir." if pol == "INDIA_REPO" else "."))
if len(ev):
    with st.expander("Faiz değişimleri"):
        ortak.tablo(ev.rename(columns={"onceki": "önceki", "degisim": "değişim"}), hide_index=True)
st.info("TL mevduat faizi ve reel getiri paneli EVDS gerektirir (v2). Adım serilerde sürekli rolling korelasyon hesaplanmaz; olay bazlı bakılır "
        "(5. ekranda FED/ECB karar günleri).")
ortak.sayfa_sonu("Bu sayfa günlük analize giremeyen yavaş serileri bağlam olarak gösterir. Faiz basamakları ile kur ve borsa hareketini yan yana "
                 "izleyin; kırmızı çizgiler değişim tarihleridir. Aylık korelasyonlar çok az gözleme dayanır, yalnızca genel bir fikir verir.")
