import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import korelasyon, rejim  # noqa: E402

ortak.sayfa_basi("4 Rejim ve Beta",
                 "Yüksek VIX rejiminde korelasyonların yükselmesi 'bulaşma' kanıtı değildir; kısmen volatilite artışının ölçüm "
                 "etkisidir. Rejim başına gözlem sayısı azsa sonuç güvenilmezdir.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
g = ortak.getiri(a)
et = ortak.kod_etiket(kat)

c1, c2, c3 = st.columns(3)
with c1:
    alt = st.number_input("Sakin / normal eşiği (VIX)", 5.0, 40.0, 15.0, 0.5)
with c2:
    ust = st.number_input("Normal / gergin eşiği (VIX)", 10.0, 80.0, 25.0, 0.5)
with c3:
    min_rejim = st.number_input("Rejim başına en az gün", 20, 500, 60, 10)
if ust <= alt:
    st.error("Üst eşik alt eşikten büyük olmalı.")
    st.stop()

vix = panel["VIX"].dropna()
rj = rejim.vix_rejimi(vix, esikler=(alt, ust))
sonuc, ozet = rejim.rejim_korelasyonlari(g, rj, yontem=a.yontem, min_gozlem=40, min_rejim_gun=int(min_rejim))
ozet["tanım"] = ["VIX < %g" % alt, "%g - %g" % (alt, ust), "VIX > %g" % ust]
st.subheader("(a) VIX rejimine koşullu korelasyon")
ortak.tablo(ozet.rename(columns={"gun_sayisi": "gün sayısı", "yeterli": "yeterli mi"}), hide_index=True)
if not ozet["yeterli"].all():
    st.warning("Yetersiz gözlemli rejim(ler) tamamen gri gösterilir; sonuç üretilmez.")

tum, _ = korelasyon.korelasyon_matrisi(g, None, None, a.yontem, 150)
sira = ortak.sirala(tum)
tablar = st.tabs([r.capitalize() for r in rejim.REJIMLER])
for tb, r in zip(tablar, rejim.REJIMLER):
    corr, n = sonuc[r]
    with tb:
        gs = int(ozet.set_index("rejim").loc[r, "gun_sayisi"])
        ortak.harita_goster(ortak.isi_haritasi(corr, n.astype(str), sira, "%s rejim (gün: %d)" % (r.capitalize(), gs)), "s4_" + r)
mk = st.columns(3)
for col, r in zip(mk, rejim.REJIMLER):
    ort = korelasyon.ortalama_ikili_korelasyon(sonuc[r][0])
    col.metric("Ortalama ikili korelasyon - %s" % r, "yetersiz" if not np.isfinite(ort) else "%.3f" % ort)
st.caption("Bu ortalamalar, aynı seri kümesi o rejimde yeterli ortak gözlem verdiği sürece karşılaştırılabilir; kriptonun 2017 öncesi "
           "gözlemi olmadığından rejimlerin dönemleri farklı olabilir. Forbes-Rigobon düzeltmesi uygulanmaz.")

# ---- zaman içinde VIX
fv = go.Figure(go.Scatter(x=vix.index, y=vix.values, line=dict(width=1, color="#d62728"), name="VIX"))
fv.add_hline(y=alt, line_dash="dot", line_color="gray")
fv.add_hline(y=ust, line_dash="dot", line_color="gray")
fv.update_layout(height=240, margin=dict(l=10, r=10, t=30, b=10), title=dict(text="VIX seviyesi ve rejim eşikleri", font=dict(size=13)))
ortak.goster(fv)

# ---- beta tablosu
st.subheader("(b) Beta tablosu")
kodlar = list(g.columns)
ref = st.selectbox("Referans varlık (x)", kodlar, index=kodlar.index("SPX") if "SPX" in kodlar else 0, format_func=et)
bt = rejim.beta_tablosu(g, ref, pencere=a.pencere)
bt = bt.join(kat.set_index("kod")[["kategori", "birim"]])
bt["birim"] = np.where(bt["birim"] == "faiz_yuzde", "bp / %1", "% / %1")
bt = bt.sort_values("beta", ascending=False)
gec = bt.dropna(subset=["beta"])
if len(gec):
    fb = go.Figure(go.Bar(x=gec.index, y=gec["beta"], error_y=dict(type="data", array=1.96 * gec["se"].values, visible=True),
                          marker_color=[ortak.KAT_RENK.get(k, "#999") for k in gec["kategori"]],
                          customdata=gec["n"], hovertemplate="%{x}<br>beta=%{y:.2f}<br>n=%{customdata}<extra></extra>"))
    fb.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                     title=dict(text="%s %%1 hareket ettiğinde diğerlerinin ortalama tepkisi (son %dg, ±1,96 se)" % (ref, a.pencere), font=dict(size=13)))
    fb.update_xaxes(tickangle=90, tickfont=dict(size=9))
    ortak.goster(fb)
ortak.tablo(bt[["beta", "se", "t", "r", "n", "birim"]], column_config={
    "beta": st.column_config.NumberColumn(format="%.2f"), "se": st.column_config.NumberColumn(format="%.2f"),
    "t": st.column_config.NumberColumn(format="%.1f"), "r": st.column_config.NumberColumn(format="%.2f")})
if (bt["n"] < 30).any():
    st.caption("n < 30 olan satırlar boş (NaN) bırakılmıştır: " + ", ".join(bt.index[bt["n"] < 30]))
st.info("Metodoloji: rejimler ayrı gösterilir; birleştirme ya da 'bulaşma' yorumu yok. Rejim eşikleri sabit mutlak değerdir (tam-örneklem "
        "yüzdeliği ileriye bakar). Beta için pencere kenar çubuğundaki seçimdir; faiz serilerinde birim bp'dir.")
ortak.sayfa_sonu("Üç matris aynı serileri sakin, normal ve gergin VIX günlerinde karşılaştırır. Gergin rejimde ortalama korelasyon "
                 "yükselirse bunun bir kısmı volatilitenin kendisinden gelir. Beta tablosu ilişkinin büyüklüğünü verir: "
                 "referans %1 oynarsa diğer varlık ortalama ne kadar oynar; hata çubuğu belirsizliktir.")
