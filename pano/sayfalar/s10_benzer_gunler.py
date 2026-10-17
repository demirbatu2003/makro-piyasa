import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from analiz import benzer  # noqa: E402

RENK_A = "#3b6fd4"
RENK_T = "#9e9e9e"
ETIKET_OZ = benzer.OZELLIK_AD


@st.cache_data(show_spinner="Özellikler ve ileri getiriler hazırlanıyor...")
def hazirla(dmg):
    kat, panel = ortak.yukle(dmg)
    oz = benzer.ozellik_tablosu(panel)
    z = benzer.zskor(oz)
    sev = benzer.hedef_seviyeleri(panel, kat)
    ileri = {h: benzer.ileri_getiriler(sev, h) for h in benzer.UFUKLAR}
    return oz, z, ileri


@st.cache_data(show_spinner="Walk-forward kontrolü hesaplanıyor (bir kez)...")
def wf_hesapla(dmg):
    oz, z, ileri = hazirla(dmg)
    wf = benzer.walk_forward(z, ileri[20], ufuk=20, k=benzer.VARSAYILAN_K)
    ozet = benzer.walk_forward_ozet(wf)
    return wf, ozet, benzer.walk_forward_yorum(ozet)


def tr(x, nd=1):
    """Türkçe ondalık virgül."""
    if x is None or not np.isfinite(x):
        return "-"
    return ("%.*f" % (nd, x)).replace(".", ",")


def birim_kat(h):
    """Log getiri -> %; US10Y -> bp."""
    return 1.0 if benzer.HEDEFLER[h][1] == "bp" else 100.0


def birim_ad(h):
    return "bp" if benzer.HEDEFLER[h][1] == "bp" else "%"


ortak.sayfa_basi("10 Benzer Günler")
a = ortak.kenar_cubugu()
oz, z, ileri = hazirla(a.dmg)

with st.expander("Nasıl okunur", expanded=True):
    st.markdown(
        "- Bu bir **tahmin değil**, bir **taban oranıdır**: bugüne benzeyen geçmiş günlerde, sonraki N iş gününde sonuçların "
        "nasıl dağıldığını gösterir.\n"
        "- Asıl bilgi **koşulsuz farktır**: analog medyanı ile *tüm günlerin* medyanı arasındaki fark. Piyasalar zaten çoğu dönemde "
        "yükselme eğiliminde olduğundan, tek başına 'analoglarda %60 yükseldi' bir şey söylemez.\n"
        "- **n küçükse** ya da kutu/aralık genişse belirsizlik büyüktür; fark aralığın içinde kalıyorsa tesadüf olabilir. "
        "Sayfanın altındaki 'geçmişte işe yaradı mı?' bölümü bu yöntemin gerçek zamanlı ne kadar bilgi taşıdığını ölçer.")

# ------------------------------------------------------------ bugünün durumu
t_poz = len(oz) - 1
bugun = oz.index[t_poz]
st.subheader("Bugünün durumu (%s)" % bugun.strftime("%Y-%m-%d"))
dur = benzer.bugunun_durumu(oz, t_poz)
gor = pd.DataFrame({
    "özellik": [ETIKET_OZ[c] for c in dur["ozellik"]],
    "değer": [tr(v, 2) for v in dur["deger"]],
    "persentil (geçmişe göre)": [("%%%d" % round(p * 100)) if np.isfinite(p) else "-" for p in dur["persentil"]],
    "okuma": list(dur["okuma"]),
})
ortak.tablo(gor, hide_index=True)
st.caption("Persentil: bu değerin, bugüne kadarki tüm geçmiş değerlerin yüzde kaçından büyük/eşit olduğu. Özellikler yalnız bugün bilinen "
           "veriyle hesaplanır; eksik gün olursa son gözlem en fazla 5 takvim günü taşınır.")

# ------------------------------------------------------------ kontroller
st.subheader("Ayarlar")
c1, c2 = st.columns([1, 1])
with c1:
    ufuk = st.radio("Ufuk (iş günü)", list(benzer.UFUKLAR), index=1, horizontal=True)
with c2:
    k = st.slider("Analog sayısı K", 10, 50, benzer.VARSAYILAN_K, 5)
st.markdown("**Özellikler**")
cols = st.columns(4)
secili = []
for i, o in enumerate(benzer.OZELLIKLER):
    with cols[i % 4]:
        if st.checkbox(ETIKET_OZ[o], value=True, key="bz_oz_" + o):
            secili.append(o)
hedefler = st.multiselect("Hedefler", list(benzer.HEDEFLER), default=list(benzer.HEDEFLER), key="bz_hedef")

if not secili:
    st.warning("En az bir özellik seçin.")
    st.stop()
if not hedefler:
    st.warning("En az bir hedef seçin.")
    st.stop()

ih = ileri[ufuk]
an, tab = benzer.analiz(z, ih, t_poz, ufuk, k, secili)
if len(an) == 0:
    st.warning("Bugün için seçili özelliklerden biri eksik ya da yeterli geçmiş yok; analog bulunamadı.")
    st.stop()
tab = tab.set_index("hedef").loc[hedefler].reset_index()
ilk_aday = z.index[benzer.aday_pozisyonlari(z, t_poz, ufuk, secili)[0]]
st.caption("Analog havuzu: %s ile %s arası (bugünden en az %d iş günü önce, z-skor ısınması 500 gün). Bulunan bağımsız analog: %d "
           "(her biri ±%d iş günü dışlamalı)." % (ilk_aday.strftime("%Y-%m"), z.index[t_poz - (ufuk + 5)].strftime("%Y-%m"),
                                                  ufuk + 5, len(an), benzer.ARALIK))

# ------------------------------------------------------------ ana grafik
st.subheader("Sonraki %d iş günü: analog dağılımı ve koşulsuz dağılım" % ufuk)
nh = len(hedefler)
nc = min(5, nh)
nr = int(np.ceil(nh / nc))
fig = make_subplots(rows=nr, cols=nc, subplot_titles=[
    "%s (%s)" % (h, birim_ad(h)) for h in tab["hedef"]], vertical_spacing=0.16, horizontal_spacing=0.05)
for i, r in tab.iterrows():
    s = birim_kat(r["hedef"])
    row, col = i // nc + 1, i % nc + 1
    for ad, sfx, renk in (("Analog", "_a", RENK_A), ("Koşulsuz", "_t", RENK_T)):
        n = int(r["n" + sfx])
        etiket = "%s n=%d" % (ad, n)
        if n == 0:
            continue
        fig.add_trace(go.Box(x=[etiket], q1=[r["q25" + sfx] * s], median=[r["medyan" + sfx] * s], q3=[r["q75" + sfx] * s],
                             lowerfence=[r["p10" + sfx] * s], upperfence=[r["p90" + sfx] * s], marker_color=renk,
                             name=etiket, showlegend=False,
                             hovertemplate="%s<br>medyan %.2f<extra></extra>" % (etiket, r["medyan" + sfx] * s)), row=row, col=col)
    fig.add_hline(y=0, line=dict(color="#555", width=1, dash="dot"), row=row, col=col)
fig.update_layout(height=330 * nr, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
fig.update_xaxes(tickfont=dict(size=10))
fig.update_annotations(font_size=12)
ortak.goster(fig)
st.caption("Kutu = çeyrekler arası (25.-75.), çizgi = medyan, bıyık = 10. ve 90. persentil. Mavi: analog günler; gri: koşulsuz (havuzdaki tüm günler). "
           "Faizde birim bp, diğerlerinde log getiri %.")

# ------------------------------------------------------------ tablo
tb = pd.DataFrame({
    "hedef": tab["hedef"],
    "birim": [birim_ad(h) for h in tab["hedef"]],
    "analog medyanı": [tr(m * birim_kat(h), 2) for h, m in zip(tab["hedef"], tab["medyan_a"])],
    "koşulsuz medyan": [tr(m * birim_kat(h), 2) for h, m in zip(tab["hedef"], tab["medyan_t"])],
    "fark": [tr(m * birim_kat(h), 2) for h, m in zip(tab["hedef"], tab["fark"])],
    "yukarı isabet (analog)": [("%%%d" % round(v * 100)) if np.isfinite(v) else "-" for v in tab["yukari_a"]],
    "yukarı isabet (koşulsuz)": [("%%%d" % round(v * 100)) if np.isfinite(v) else "-" for v in tab["yukari_t"]],
    "10.-90. aralığı (analog)": ["%s ... %s" % (tr(lo * birim_kat(h), 1), tr(hi * birim_kat(h), 1))
                                  for h, lo, hi in zip(tab["hedef"], tab["p10_a"], tab["p90_a"])],
    "n (analog)": tab["n_a"].astype(int),
    "n (koşulsuz)": tab["n_t"].astype(int),
})
st.markdown("**Hedef tablosu** (medyan ileri getiri; fark = analog medyanı - koşulsuz medyan)")
ortak.tablo(tb, hide_index=True)
kucuk = [h for h, n in zip(tab["hedef"], tab["n_a"]) if n < 15]
if kucuk:
    st.caption("Analog n'i 15'in altında olan hedefler: %s (BTC verisi 2017-08'de başlar; eksik sonuçlu analoglar n'e girmez)." % ", ".join(kucuk))

# ------------------------------------------------------------ analog dönem listesi
st.subheader("Analog dönemler")
ls = oz.iloc[an["poz"].to_numpy()][secili].copy()
ls.insert(0, "uzaklık", an["uzaklik"].to_numpy())
ls.insert(0, "tarih", z.index[an["poz"].to_numpy()].strftime("%Y-%m-%d"))
ls = ls.rename(columns={o: ETIKET_OZ[o] for o in secili})
ortak.tablo(ls.round(2), hide_index=True)

# ------------------------------------------------------------ walk-forward
st.subheader("Bu yöntem geçmişte işe yaradı mı?")
wf, ozet, yorum = wf_hesapla(a.dmg)
st.caption("Walk-forward: 2016-01'den itibaren her ay başı için analoglar YALNIZ o tarihe kadarki veriyle bulundu (varsayılan ayarlar: tüm özellikler, "
           "K=%d, ufuk 20 iş günü), analog medyanı sonradan gerçekleşen 20g getiriyle karşılaştırıldı. Hedef başına en az 8 analog "
           "sonuçlu ay şartı var." % benzer.VARSAYILAN_K)
ok = ozet[~ozet["yetersiz"].astype(bool)].copy()
if len(ok):
    wt = pd.DataFrame({
        "hedef": ok["hedef"],
        "gözlem (ay)": ok["n"].astype(int),
        "yön isabeti: analog": ["%%%d" % round(v * 100) for v in ok["yon_analog"]],
        "yön isabeti: koşulsuz medyan yönü": ["%%%d" % round(v * 100) for v in ok["yon_taban"]],
        "hep yukarı (kıyas)": ["%%%d" % round(v * 100) for v in ok["hep_yukari"]],
        "Spearman (analog medyan ~ gerçekleşen)": [tr(v, 2) for v in ok["spearman"]],
        "p": [tr(v, 2) for v in ok["spearman_p"]],
        "ort. mutlak hata: analog": [tr(m * birim_kat(h), 2) for h, m in zip(ok["hedef"], ok["mae_analog"])],
        "ort. mutlak hata: koşulsuz": [tr(m * birim_kat(h), 2) for h, m in zip(ok["hedef"], ok["mae_taban"])],
        "avantaj": np.where(ok["avantaj"], "evet", "hayır"),
    })
    ortak.tablo(wt, hide_index=True)
    st.caption("Hata birimi: log getiri için %, US10Y için bp. 'Avantaj' = Spearman>0 ve p<0,05 ve hata analogda daha küçük ve yön isabeti "
               "analogda daha yüksek (hepsi birlikte). Aylık gözlemler örtüşmez ama hedefler birbiriyle ilişkilidir; p değerleri çoklu "
               "test düzeltmesizdir.")
    (st.success if "görünüyor (ama" in yorum else st.info)(yorum)
else:
    st.info(yorum)
