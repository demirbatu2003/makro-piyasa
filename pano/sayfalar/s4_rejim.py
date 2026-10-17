import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import korelasyon, kriz, rejim  # noqa: E402

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

kodlar = list(g.columns)
# ---- kriz anı ilişkisi
st.subheader("(b) Kriz anı ilişkisi: sert düşüş günlerinde ne oluyor?")
kc1, kc2, kc3 = st.columns(3)
with kc1:
    kref = st.selectbox("Referans varlık", kodlar, index=kodlar.index("SPX") if "SPX" in kodlar else 0, format_func=et, key="s4_kriz_ref")
with kc2:
    kesik = st.select_slider("Kuyruk eşiği (referansın en kötü günleri)", [0.05, 0.10, 0.15, 0.20], value=0.10,
                            format_func=lambda v: "alt %%%d" % round(v * 100), key="s4_kriz_esik")
with kc3:
    kmin = st.number_input("Güvenilir sayılması için en az kuyruk günü", 10, 200, 30, 5, key="s4_kriz_min")
kt = kriz.kuyruk_iliskisi(g, kref, kuyruk=kesik, yontem=a.yontem, min_kuyruk=int(kmin))
kt = kt.join(kat.set_index("kod")[["kategori"]])
kg = kt.dropna(subset=["ortak_dusus"]).sort_values("ortak_dusus", ascending=False)
if len(kg):
    renk = [ortak.KAT_RENK.get(k, "#999") if y else "#cccccc" for k, y in zip(kg["kategori"], kg["yeterli"])]
    fk = go.Figure(go.Bar(x=kg.index, y=kg["ortak_dusus"] * 100, marker_color=renk, customdata=np.column_stack([kg["n_kuyruk"], kg["kor_kuyruk"], kg["kor_normal"]]),
                          hovertemplate="%{x}<br>ortak düşüş %{y:.0f}%<br>kuyruk günü n=%{customdata[0]}<br>kuyruk kor=%{customdata[1]:.2f}, normal kor=%{customdata[2]:.2f}<extra></extra>"))
    fk.add_hline(y=kesik * 100, line_dash="dash", line_color="#d62728",
                 annotation_text="bağımsızlıkta beklenen: %%%d" % round(kesik * 100), annotation_position="top right")
    fk.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                     title=dict(text="%s en kötü %%%d günündeyken diğerinin de kendi en kötü %%%d'inde olma payı (gri: az gözlem)" % (
                         kref, round(kesik * 100), round(kesik * 100)), font=dict(size=13)),
                     yaxis_title="ortak düşüş oranı (%)")
    fk.update_xaxes(tickangle=90, tickfont=dict(size=9))
    ortak.goster(fk)
kgos = kt[["kor_kuyruk", "kor_normal", "ortak_dusus", "beklenen", "n_kuyruk", "n_normal", "yeterli"]].copy()
kgos["ortak_dusus"] = kgos["ortak_dusus"] * 100
kgos["beklenen"] = kgos["beklenen"] * 100
kgos["kor_fark"] = kgos["kor_kuyruk"] - kgos["kor_normal"]
kgos = kgos.sort_values("ortak_dusus", ascending=False)
kgos.columns = ["kuyruk korelasyonu", "normal gün korelasyonu", "ortak düşüş (%)", "beklenen (%)", "n kuyruk", "n normal", "yeterli", "fark"]
kstil = kgos.style.apply(lambda r: ["color: #999999" if not r["yeterli"] else "" for _ in r], axis=1).format(
    {"kuyruk korelasyonu": "{:.2f}", "normal gün korelasyonu": "{:.2f}", "ortak düşüş (%)": "{:.0f}", "beklenen (%)": "{:.0f}", "fark": "{:+.2f}"}, na_rep="-")
ortak.tablo(kstil)
st.caption("Gri satırlar: kuyruk günü sayısı %d'in altında, sonuç güvenilmez. Eşikler her serinin kendi geçmiş dağılımındandır (tüm örnek, sonradan bakış). "
           "Kuyruk korelasyonu aralığı daraltılmış veride hesaplandığı için mekanik olarak düşük çıkma eğilimindedir; asıl okunacak kısım "
           "ortak düşüş oranının beklenen orandan ne kadar büyük olduğudur." % int(kmin))
with st.expander("Nasıl okunur? (kriz anı ilişkisi)"):
    st.markdown(
        "Soru: **çeşitlendirme en çok gerektiğinde işe yarıyor mu?** Referans varlığın (ör. SPX) en kötü günlerini ayırıyoruz."
        "\n\n- **Ortak düşüş oranı:** referans en kötü %10'luk dilimindeyken, diğer varlığın da kendi en kötü %10'luk diliminde olduğu günlerin payı. "
        "İki varlık birbirinden bağımsız olsaydı bu pay yaklaşık %10 çıkardı (kırmızı kesikli çizgi). %10'a yakınsa o varlık krizde sizi korur gibi davranıyor; "
        "%40-50 gibi yüksek bir değer, o varlığın referansla birlikte çöktüğünü, yani tam gerektiğinde çeşitlendirme sağlamadığını gösterir."
        "\n- **Kuyruk ve normal gün korelasyonu:** kuyruk günlerindeki korelasyon normal günlerdekinden belirgin büyükse, ilişki kriz anında güçleniyor demektir. "
        "Küçük bir kuyruk örneğinde bu sayılar oynaktır; gri satırlara güvenmeyin."
        "\n- Ortak düşüş oranı %10'un belirgin altındaysa ve korelasyon negatifse, bu varlık düşüşlerde tersine hareket ediyor olabilir.")

# ---- beta tablosu
st.subheader("(c) Beta tablosu")
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
