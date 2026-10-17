import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from analiz import makas  # noqa: E402


def _fmt(v, nd=2):
    if v is None or not np.isfinite(v):
        return "-"
    return f"{v:.{nd}f}"


@st.cache_data(show_spinner="İkili makaslar taranıyor...")
def _tarama_onbellek(dmg, baz, kategoriler, uzun_pencere, kisa_pencere, min_corr, ufuk, z_esik, yontem, makas_turu):
    kat, _ = ortak.yukle(dmg)
    g_tum = ortak.getiri_tum(dmg, baz)
    kt = kat.set_index("kod")["kategori"]
    g = g_tum[[c for c in g_tum.columns if kt.get(c) in kategoriler]]
    return makas.makas_tarama(
        g, uzun_pencere=uzun_pencere, kisa_pencere=kisa_pencere,
        min_corr=min_corr, ufuk=ufuk, z_esik=z_esik,
        yontem=yontem, makas_turu=makas_turu, katalog=kat,
    )


ortak.sayfa_basi(
    "12 İkili Makas ve Göreli Değer",
    "İki varlığın kısa vadede ayrışması (yüksek |z|) her zaman ortalamaya döneceği anlamına gelmez; yapısal "
    "rejim kırılmalarında makas kalıcı olarak açılabilir. Geçmiş kapanma oranını ve örneklem sayısını (n) birlikte değerlendirin.",
)
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
g = ortak.getiri(a)
et = ortak.kod_etiket(kat)
kodlar = list(g.columns)

if len(kodlar) < 2:
    st.warning("Makas analizi için en az iki varlık gereklidir.")
    st.stop()

# =====================================================================
# BÖLÜM 1: OTOMATİK MAKAS TARAYICISI
# =====================================================================
st.subheader("1. Otomatik Makas Tarayıcısı (Yüksek Korelasyonlu Çiftler)")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    min_corr = st.slider("Minimum |r| (250g korelasyon)", 0.40, 0.85, 0.55, 0.05, key="s12_mc")
with c2:
    kisa_pencere = st.selectbox("Kısa makas penceresi (iş günü)", list(makas.KISA_PENCERELER), index=2, key="s12_kp")
with c3:
    makas_turu = st.selectbox("Makas hesabı", list(makas.MAKAS_TURLERI), format_func=makas.MAKAS_TURLERI.get, key="s12_mt")
with c4:
    z_esik = st.slider("Aşırılık eşiği (k × σ)", 1.5, 3.0, 2.0, 0.1, key="s12_ze")
with c5:
    ufuk_tarama = st.selectbox("Kapanma testi ufku (iş günü)", list(makas.GERI_DONUS_UFUKLAR), index=1, key="s12_uf")

tarama_df = _tarama_onbellek(
    a.dmg, a.baz, a.kategoriler, 250, int(kisa_pencere),
    float(min_corr), int(ufuk_tarama), float(z_esik), a.yontem, makas_turu,
)

if len(tarama_df) == 0:
    st.info(f"Son 250 iş gününde |r| ≥ {min_corr:.2f} koşulunu sağlayan varlık çifti bulunamadı. Korelasyon eşiğini düşürmeyi deneyin.")
else:
    asiri_sayisi = int((tarama_df["mutlak_z"] >= 2.0).sum())
    acilan_sayisi = int(((tarama_df["mutlak_z"] >= 1.5) & (tarama_df["mutlak_z"] < 2.0)).sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Taranan Yüksek Korelasyonlu Çift", len(tarama_df))
    m2.metric("Aşırı Ayrışan Çift (|z| ≥ 2.0σ)", asiri_sayisi)
    m3.metric("Makası Açılan Çift (1.5σ ≤ |z| < 2.0σ)", acilan_sayisi)

    gor_tarama = pd.DataFrame({
        "A": tarama_df["A"],
        "B": tarama_df["B"],
        "r_250": [_fmt(v, 2) for v in tarama_df["r_250"]],
        "beta": [_fmt(v, 2) for v in tarama_df["beta"]],
        f"A_{kisa_pencere}g_getiri": [f"{v:+.2f} {b}" if np.isfinite(v) else "-" for v, b in zip(tarama_df["A_kisa_getiri"], tarama_df["birim_a"])],
        f"B_{kisa_pencere}g_getiri": [f"{v:+.2f} {b}" if np.isfinite(v) else "-" for v, b in zip(tarama_df["B_kisa_getiri"], tarama_df["birim_b"])],
        "makas_z": [f"{v:+.2f}σ" if np.isfinite(v) else "-" for v in tarama_df["makas_z"]],
        "durum": tarama_df["durum"],
        f"kapanma_orani (t+{ufuk_tarama}g, %)": [f"%{v:.1f}" if np.isfinite(v) else "-" for v in tarama_df["kapanma_orani"]],
        "n (geçmiş |z|≥k)": tarama_df["n_olay"].astype(int),
        "Not": np.where(tarama_df["yetersiz"], "yetersiz veri (n<10)", ""),
    })
    st.markdown(f"**Makas Tarama Tablosu** (`|z|` büyüklüğüne göre sıralı, makas türü: *{makas.MAKAS_TURLERI[makas_turu]}*)")
    ortak.tablo(gor_tarama, hide_index=True)
    st.caption(
        "Tüm z-skor, volatilite ve OLS beta parametreleri yalnız o güne kadarki geçmişle (ex-ante, .shift(1)) hesaplanır. "
        "Birimleri farklı çiftlerde (fiyat log-getirisi vs faiz bp) 'Doğrudan Getiri Farkı' seçilse bile otomatik olarak "
        "60g volatilite-standardize makas kullanılır."
    )

# =====================================================================
# BÖLÜM 2: SEÇİLİ ÇİFT İÇİN DETAYLI MAKAS & ORTALAMAYA DÖNÜŞ ANALİZİ
# =====================================================================
st.divider()
st.subheader("2. Seçili Çift İçin Detaylı Makas ve Ortalamaya Dönüş (Mean-Reversion) Analizi")

sec_mod = st.radio(
    "Çift seçim yöntemi",
    ["Tarama tablosundan seç", "Tüm varlıklardan serbest seç"],
    horizontal=True,
    key="s12_sec_mod",
)

if sec_mod == "Tarama tablosundan seç" and len(tarama_df) > 0:
    cift_etiketleri = [
        f"{r['A']} / {r['B']}  |  z = {r['makas_z']:+.2f}σ  |  r_250 = {r['r_250']:.2f}  |  {r['durum']}"
        for _, r in tarama_df.iterrows()
    ]
    sec_i = st.selectbox("Taranan çiftlerden seçin", range(len(cift_etiketleri)), format_func=lambda i: cift_etiketleri[i], key="s12_cift_idx")
    sec_a = str(tarama_df.iloc[sec_i]["A"])
    sec_b = str(tarama_df.iloc[sec_i]["B"])
else:
    sc1, sc2 = st.columns(2)
    def_a = kodlar.index("SPX") if "SPX" in kodlar else 0
    def_b = kodlar.index("NASDAQ") if "NASDAQ" in kodlar and def_a != kodlar.index("NASDAQ") else (1 if len(kodlar) > 1 else 0)
    with sc1:
        sec_a = st.selectbox("Varlık A", kodlar, index=def_a, format_func=et, key="s12_ser_a")
    with sc2:
        sec_b = st.selectbox("Varlık B", kodlar, index=def_b, format_func=et, key="s12_ser_b")

if sec_a == sec_b:
    st.info("Lütfen birbirinden farklı iki varlık seçin.")
    st.stop()

perf_tipi = st.radio(
    "Grafik 1 performans gösterimi (son 250 iş günü)",
    ["norm100", "kum_std"],
    horizontal=True,
    format_func={
        "norm100": "Normalize Kümülatif Performans (Başlangıç = 100)",
        "kum_std": "Kümülatif Standartlaştırılmış Getiri (Σ r / σ_60g)",
    }.get,
    key="s12_perf_tipi",
)

seri_df = makas.ikili_makas_serisi(
    g, sec_a, sec_b, kisa_pencere=int(kisa_pencere), uzun_pencere=250,
    makas_turu=makas_turu, katalog=kat,
)
gd_df = makas.makas_geri_donus_testi(
    g, sec_a, sec_b, kisa_pencere=int(kisa_pencere), uzun_pencere=250,
    k=float(z_esik), ufuklar=makas.GERI_DONUS_UFUKLAR,
    makas_turu=makas_turu, katalog=kat, _seri_df=seri_df,
)

z_gecerli = seri_df["makas_z"].dropna()
if len(z_gecerli) == 0:
    st.warning("Seçili çift için makas Z-skoru hesaplanacak yeterli ortak geçmiş gözlem yok.")
    st.stop()

son_z = float(z_gecerli.iloc[-1])
son_beta_s = seri_df["beta"].dropna()
son_beta = float(son_beta_s.iloc[-1]) if len(son_beta_s) else np.nan
etkin_tur = seri_df.attrs.get("etkin_tur", makas_turu)

dm1, dm2, dm3, dm4 = st.columns(4)
dm1.metric(f"Güncel Makas Z-Skoru ({kisa_pencere}g)", f"{son_z:+.2f}σ")
dm2.metric("Güncel Durum", makas.makas_durumu(son_z, esik_asiri=float(z_esik)))
dm3.metric("Ex-Ante OLS Beta (A ~ B)", _fmt(son_beta, 2))
dm4.metric("Etkin Makas Türü", makas.MAKAS_TURLERI.get(etkin_tur, etkin_tur))

# Grafik 1 & Grafik 2
son_250 = seri_df.dropna(subset=["norm_a", "norm_b"], how="all")
z_cizim = seri_df.dropna(subset=["makas_z"]).iloc[-750:]  # son ~3 yıl Z-skoru

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.12,
    subplot_titles=(
        f"Grafik 1 — Son 250 İş Gününde {sec_a} ve {sec_b} Performansı "
        f"({'Başlangıç = 100' if perf_tipi == 'norm100' else 'Kümülatif σ Birimi'})",
        f"Grafik 2 — {sec_a} / {sec_b} {kisa_pencere} Günlük Makas Z-Skoru ve ±{z_esik:g}σ Eşik Çizgileri",
    ),
)

if perf_tipi == "norm100":
    ya_col, yb_col = "norm_a", "norm_b"
else:
    ya_col, yb_col = "kum_std_a", "kum_std_b"

fig.add_trace(
    go.Scatter(x=son_250.index, y=son_250[ya_col], name=sec_a, line=dict(color="#2a9d8f", width=2.0)),
    row=1, col=1,
)
fig.add_trace(
    go.Scatter(x=son_250.index, y=son_250[yb_col], name=sec_b, line=dict(color="#8e44ad", width=2.0)),
    row=1, col=1,
)

fig.add_trace(
    go.Scatter(
        x=z_cizim.index, y=z_cizim["makas_z"], name=f"Makas Z ({kisa_pencere}g)",
        line=dict(color="#1b5fb5", width=1.8),
        hovertemplate="%{x|%Y-%m-%d}<br>z = %{y:+.2f}σ<extra></extra>",
    ),
    row=2, col=1,
)
fig.add_hline(y=0.0, line=dict(color="#555", width=1, dash="dot"), row=2, col=1)
fig.add_hline(y=float(z_esik), line=dict(color="#d62728", width=1.5, dash="dash"), row=2, col=1)
fig.add_hline(y=-float(z_esik), line=dict(color="#2a9d8f", width=1.5, dash="dash"), row=2, col=1)

fig.update_layout(
    height=680,
    margin=dict(l=10, r=10, t=50, b=10),
    legend=dict(orientation="h", y=1.06),
)
ortak.goster(fig)

# Tarihsel Ortalamaya Dönüş (Mean-Reversion) Özeti
st.markdown(f"**Tarihsel Ortalamaya Dönüş (Mean-Reversion) Özeti (`|z| ≥ {z_esik:g}σ`, bağımsız olaylar, ±5 iş günü ayıklamalı)**")
gd_gor = pd.DataFrame({
    "Aşırılık Yönü": gd_df["yon_etiket"],
    "Takip Eden Ufuk": [f"t+{u} iş günü" for u in gd_df["ufuk"]],
    "Örneklem (n)": gd_df["n"].astype(int),
    "Kapanma (Ortalamaya Dönme) Oranı (%)": [f"%{v:.1f}" if np.isfinite(v) else "-" for v in gd_df["kapanma_orani"]],
    "Medyan Kapanma Miktarı": [f"{v:+.2f} {b}" if np.isfinite(v) else "-" for v, b in zip(gd_df["medyan_kapanma"], gd_df["birim"])],
    "Çeyrekler Arası (Q25 .. Q75)": [
        f"[{q1:+.2f}, {q3:+.2f}] {b}" if (np.isfinite(q1) and np.isfinite(q3)) else "-"
        for q1, q3, b in zip(gd_df["q25_kapanma"], gd_df["q75_kapanma"], gd_df["birim"])
    ],
    "Medyan Z-Skoru Kapanması (σ)": [f"{v:+.2f}σ" if np.isfinite(v) else "-" for v in gd_df["medyan_z_degisim"]],
    "Not": np.where(gd_df["yetersiz"], "yetersiz veri (n<10)", ""),
})
ortak.tablo(gd_gor, hide_index=True)
st.caption(
    "Kapanma (ortalamaya dönme) hesabı: Olay günü t'den sonraki t+1 .. t+ufuk iş günlerindeki gelecek kümülatif makas "
    "hareketinin, t günündeki aşırılığın tersi yönde olup olmadığı ölçülür (mekanik pencere kayması etkisi içermez)."
)

olay_sozluk = gd_df.attrs.get("olay_tarihleri", {})
tum_olay_tar = olay_sozluk.get("tum", pd.DatetimeIndex([]))
with st.expander(f"Geçmişte |z| ≥ {z_esik:g}σ aşımı yaşanan bağımsız tarihler ({len(tum_olay_tar)} olay)"):
    if len(tum_olay_tar):
        st.write(", ".join(t.strftime("%Y-%m-%d") for t in tum_olay_tar))
    else:
        st.write("Olay bulunamadı.")

ortak.sayfa_sonu(
    "- **Makas Z-Skoru ($z_{\\text{makas}}$):** İki ilişkili varlığın son `kisa_pencere` (5, 10, 20, 60) iş günündeki "
    "birikimli makas değişiminin, kendi geçmiş 250 günlük (ex-ante) ortalamasından kaç standart sapma uzaklaştığını gösterir.\n"
    "- **$z \\ge +2\\sigma$:** A varlığı B'ye göre tarihsel normunun üzerinde önden gitmiştir ('A aşırı önde / B geride').\n"
    "- **$z \\le -2\\sigma$:** A varlığı B'ye göre geride kalmıştır ('A geride kaldı / B önde').\n"
    "- **Tarihsel Ortalamaya Dönüş Testi:** Geçmişte makas $\\pm k\\sigma$'yı aştığında sonraki 5, 10 ve 20 iş gününde "
    "makasın gerçekten ters yönde kapanıp kapanmadığını ölçer. Örneklem sayısı `n < 10` olduğunda sonuçlar güvenilir değildir."
)
