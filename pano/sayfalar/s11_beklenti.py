import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from analiz import beklenti  # noqa: E402

SIRALAMA_AD_1 = {
    "olasilik_farki": "Olasılık farkı (ΔP, puan)",
    "medyan_farki": "Medyan getiri farkı",
    "yukari_orani": "Koşullu yukarı olasılığı (%)",
    "medyan": "Koşullu medyan getiri",
}
SIRALAMA_AD_2 = {
    "olasilik_farki": "Olasılık farkı (ΔP, puan)",
    "medyan_fark": "Medyan getiri farkı",
    "yukari_olasiligi": "Koşullu yukarı olasılığı (%)",
    "medyan_kosullu": "Koşullu medyan getiri",
}
YON_AD = {"yukari": "Yukarı (+)", "asagi": "Aşağı (−)"}


def _fmt(v, nd=2):
    if v is None or not np.isfinite(v):
        return "-"
    return f"{v:.{nd}f}"


ortak.sayfa_basi(
    "11 Koşullu Beklenti ve Şoklar",
    "Koşullu olasılıklar ve medyanlar geçmiş olaylara dayanır; örneklem sayısı (n) küçük olduğunda "
    "farklar tesadüf olabilir. Tüm volatilite ve eşik hesapları yalnız o güne kadarki geçmişle (ex-ante) yapılır.",
)
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
g = ortak.getiri(a)
et = ortak.kod_etiket(kat)
kodlar = list(g.columns)

if len(kodlar) == 0:
    st.warning("Seçili kategorilerde görüntülenecek varlık yok.")
    st.stop()

tab1, tab2 = st.tabs([
    "1. Son Günlerin Canlı Şok Tarayıcısı ve Beklentileri",
    "2. Çoklu Koşullu Olasılık Motoru (Eğer X ve Y Olursa)",
])

# =====================================================================
# BÖLÜM 1: CANLI ŞOK TARAYICISI VE BEKLENTİLERİ
# =====================================================================
with tab1:
    st.subheader("Son İş Günlerindeki Canlı Şoklar ve Tarihsel Tepki Dağılımı")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        pencere_gun = st.slider("Tarama penceresi (son N iş günü)", 3, 30, 10, 1, key="s11_pg")
    with c2:
        k_esik = st.slider("Şok eşiği (k × σ, ex-ante 60g)", 1.5, 3.0, 1.8, 0.1, key="s11_k")
    with c3:
        ufuk1 = st.radio("Takip eden ufuk (iş günü)", list(beklenti.SOK_UFUKLAR), index=1, horizontal=True, key="s11_uf1")
    with c4:
        sira1 = st.selectbox("Sıralama ölçütü", list(SIRALAMA_AD_1), format_func=SIRALAMA_AD_1.get, key="s11_sira1")

    soklar = beklenti.son_soklari_bul(g, pencere_gun=pencere_gun, k=k_esik, katalog=kat)

    if len(soklar) == 0:
        st.info(f"Son {pencere_gun} iş gününde |z| ≥ {k_esik:.1f}σ büyüklüğünde hareket eden varlık bulunamadı. "
                "Aşağıdan manuel varlık ve yön seçerek tarihsel şok beklentisini inceleyebilirsiniz.")
        mc1, mc2 = st.columns(2)
        with mc1:
            sec_tetik = st.selectbox("Tetikleyici varlık", kodlar, format_func=et, key="s11_man_tetik")
        with mc2:
            sec_yon = st.selectbox("Şok yönü", ["yukari", "asagi"], format_func=YON_AD.get, key="s11_man_yon")
    else:
        st.markdown(f"**Son {pencere_gun} iş gününde tespit edilen canlı şoklar** (`|z| ≥ {k_esik:.1f}σ`, toplam **{len(soklar)}** olay)")
        sok_gor = pd.DataFrame({
            "Tarih": soklar["tarih"].dt.strftime("%Y-%m-%d"),
            "Varlık": [et(k) for k in soklar["kod"]],
            "Yön": [YON_AD.get(y, y) for y in soklar["yon"]],
            "Günlük Hareket": [f"{v:+.2f} {b}" for v, b in zip(soklar["getiri_olcekli"], soklar["birim"])],
            "60g Ex-Ante σ": [f"{s:.2f} {b}" for s, b in zip(soklar["sigma"], soklar["birim"])],
            "Z-Skoru": [f"{z:+.2f}σ" for z in soklar["z"]],
        })
        ortak.tablo(sok_gor, hide_index=True)

        secenekler = [
            f"{r['tarih'].strftime('%Y-%m-%d')} | {et(r['kod'])} | {YON_AD[r['yon']]} ({r['z']:+.2f}σ)"
            for _, r in soklar.iterrows()
        ]
        sec_idx = st.selectbox(
            "Beklentisi incelenecek canlı şoku seçin (varsayılan: en son gerçekleşen şok)",
            range(len(secenekler)),
            format_func=lambda i: secenekler[i],
            key="s11_sec_sok",
        )
        sec_tetik = str(soklar.iloc[sec_idx]["kod"])
        sec_yon = str(soklar.iloc[sec_idx]["yon"])

    _, bek = beklenti.son_soklar_ve_beklentiler(
        g, pencere_gun=pencere_gun, k=k_esik, ufuk=ufuk1,
        tetik=sec_tetik, yon=sec_yon, siralama=sira1, katalog=kat,
    )
    n_gecmis = bek.attrs.get("n_olay", 0)
    olay_tar = bek.attrs.get("olay_tarihleri", pd.DatetimeIndex([]))

    m1, m2, m3 = st.columns(3)
    m1.metric("İncelenen Şok", f"{sec_tetik} ({YON_AD.get(sec_yon, sec_yon)})")
    m2.metric(f"Geçmiş Bağımsız Olay (|z| ≥ {k_esik:.1f}σ)", int(n_gecmis))
    m3.metric("Takip Eden Ufuk", f"{ufuk1} iş günü")

    if n_gecmis == 0 or len(bek) == 0:
        st.warning("Bu şok tanımı için geçmişte tamamlanmış yeterli olay bulunamadı.")
    else:
        if n_gecmis < 15:
            st.warning(f"Geçmişte bu büyüklükte yalnızca n={n_gecmis} bağımsız olay bulundu (n < 15); sonuçlar yüksek belirsizlik taşır.")

        d_plot = bek.dropna(subset=["medyan", "yukari_orani"]).copy()
        if len(d_plot):
            d_plot = d_plot.iloc[::-1]  # yatay barda en üstte birinci sıra görünsün
            renk_p = ["#bdbdbd" if y else ("#2a9d8f" if v >= 0 else "#d62728")
                      for y, v in zip(d_plot["yetersiz"], d_plot["olasilik_farki"])]
            fig1 = make_subplots(
                rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                subplot_titles=(
                    f"Olasılık Farkı ΔP = P(Yukarı|Şok) − P(Yukarı) (puan, t+{ufuk1}g)",
                    f"Koşullu Medyan vs Koşulsuz Medyan (t+{ufuk1}g, % / bp)",
                ),
            )
            fig1.add_trace(
                go.Bar(
                    y=d_plot["hedef"], x=d_plot["olasilik_farki"], orientation="h",
                    marker_color=renk_p, name="ΔP (puan)",
                    customdata=np.c_[d_plot["yukari_orani"], d_plot["kosulsuz_yukari_orani"], d_plot["n"]],
                    hovertemplate="%{y}<br>ΔP: %{x:+.1f} puan<br>Koşullu: %%{customdata[0]:.1f} | Koşulsuz: %%{customdata[1]:.1f}<br>n=%{customdata[2]:.0f}<extra></extra>",
                ),
                row=1, col=1,
            )
            fig1.add_vline(x=0, line=dict(color="#555", width=1, dash="dot"), row=1, col=1)

            fig1.add_trace(
                go.Bar(
                    y=d_plot["hedef"], x=d_plot["medyan"], orientation="h",
                    marker_color="#3b6fd4", name="Koşullu Medyan",
                    customdata=np.c_[d_plot["q25"], d_plot["q75"], d_plot["birim"]],
                    hovertemplate="%{y}<br>Koşullu Medyan: %{x:+.2f} %{customdata[2]}<br>Çeyrekler: [%{customdata[0]:+.2f}, %{customdata[1]:+.2f}]<extra></extra>",
                ),
                row=1, col=2,
            )
            fig1.add_trace(
                go.Scatter(
                    y=d_plot["hedef"], x=d_plot["kosulsuz_medyan"], mode="markers",
                    marker=dict(color="#111111", size=7, symbol="diamond"), name="Koşulsuz Medyan",
                    hovertemplate="%{y}<br>Koşulsuz Medyan: %{x:+.2f}<extra></extra>",
                ),
                row=1, col=2,
            )
            fig1.add_vline(x=0, line=dict(color="#555", width=1, dash="dot"), row=1, col=2)
            fig1.update_layout(
                height=max(420, 24 * len(d_plot) + 100),
                margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(orientation="h", y=1.06),
            )
            ortak.goster(fig1)

        bek_gor = pd.DataFrame({
            "Hedef": bek["hedef"],
            "Birim": bek["birim"],
            "n": bek["n"].astype(int),
            "Medyan": [_fmt(v, 2) for v in bek["medyan"]],
            "Q25": [_fmt(v, 2) for v in bek["q25"]],
            "Q75": [_fmt(v, 2) for v in bek["q75"]],
            "Koşulsuz Medyan": [_fmt(v, 2) for v in bek["kosulsuz_medyan"]],
            "Medyan Farkı": [_fmt(v, 2) for v in bek["medyan_farki"]],
            "Yukarı Oranı (%)": [_fmt(v, 1) for v in bek["yukari_orani"]],
            "Koşulsuz Yukarı (%)": [_fmt(v, 1) for v in bek["kosulsuz_yukari_orani"]],
            "Olasılık Farkı (ΔP, puan)": [_fmt(v, 1) for v in bek["olasilik_farki"]],
            "Not": np.where(bek["yetersiz"], "yetersiz veri (n<15)", ""),
        })
        st.markdown(f"**{et(sec_tetik)} ({YON_AD.get(sec_yon, sec_yon)}, |z| ≥ {k_esik:.1f}σ) sonrası t+{ufuk1} iş günü beklenti tablosu**")
        ortak.tablo(bek_gor, hide_index=True)

        with st.expander(f"Geçmişteki bağımsız olay tarihleri ({len(olay_tar)} gün, ±5 iş günü ayıklamalı)"):
            st.write(", ".join(t.strftime("%Y-%m-%d") for t in olay_tar))

# =====================================================================
# BÖLÜM 2: ÇOKLU KOŞULLU OLASILIK MOTORU
# =====================================================================
with tab2:
    st.subheader("Çoklu Koşullu Olasılık Motoru (\"Eğer X ve Y Olursa Ne Yükselir/Düşer?\")")
    st.caption("Seçilen koşulların geçmişte birlikte sağlandığı bağımsız dönemleri (±5 iş günü örtüşme ayıklamalı) bulur "
               "ve takip eden ufuktaki sonuçları aynı geçmiş havuzun koşulsuz taban oranıyla karşılaştırır.")

    k1_col1, k1_col2, k1_col3 = st.columns(3)
    varsayilan_k1 = kodlar.index("SPX") if "SPX" in kodlar else 0
    with k1_col1:
        kod1 = st.selectbox("Koşul 1 — Varlık A", kodlar, index=varsayilan_k1, format_func=et, key="s11_k1_kod")
    with k1_col2:
        pencere1 = st.selectbox("Koşul 1 — Pencere (M iş günü)", [1, 5, 10, 20, 60], index=1, key="s11_k1_pen")
    with k1_col3:
        durum1 = st.selectbox(
            "Koşul 1 — Hareket Durumu",
            list(beklenti.DURUM_AD),
            index=4,  # sert_asagi
            format_func=beklenti.DURUM_AD.get,
            key="s11_k1_dur",
        )

    k2_col1, k2_col2, k2_col3, k2_col4 = st.columns(4)
    with k2_col1:
        ikinci_tur = st.selectbox(
            "Opsiyonel Koşul 2 Türü",
            ["yok", "varlik", "vix"],
            format_func={
                "yok": "Yok (Yalnız Koşul 1)",
                "varlik": "İkinci Varlık Koşulu (Varlık B)",
                "vix": "VIX Rejimi (Sakin / Normal / Gergin)",
            }.get,
            key="s11_k2_tur",
        )

    kosullar_listesi = [{"kod": kod1, "pencere": int(pencere1), "durum": durum1, "k": 1.0}]
    vix_rejim_sec = None

    if ikinci_tur == "varlik":
        varsayilan_k2 = kodlar.index("DXY") if "DXY" in kodlar and kod1 != "DXY" else (1 if len(kodlar) > 1 else 0)
        with k2_col2:
            kod2 = st.selectbox("Koşul 2 — Varlık B", kodlar, index=varsayilan_k2, format_func=et, key="s11_k2_kod")
        with k2_col3:
            pencere2 = st.selectbox("Koşul 2 — Pencere (M iş günü)", [1, 5, 10, 20, 60], index=1, key="s11_k2_pen")
        with k2_col4:
            durum2 = st.selectbox(
                "Koşul 2 — Hareket Durumu",
                list(beklenti.DURUM_AD),
                index=1,  # sert_yukari
                format_func=beklenti.DURUM_AD.get,
                key="s11_k2_dur",
            )
        kosullar_listesi.append({"kod": kod2, "pencere": int(pencere2), "durum": durum2, "k": 1.0})
    elif ikinci_tur == "vix":
        with k2_col2:
            vix_rejim_sec = st.selectbox(
                "Koşul 2 — VIX Rejimi",
                ["sakin", "normal", "gergin"],
                index=2,
                format_func={"sakin": "Sakin (VIX < 15)", "normal": "Normal (15 ≤ VIX ≤ 25)", "gergin": "Gergin (VIX > 25)"}.get,
                key="s11_k2_vix",
            )

    u_col1, u_col2 = st.columns(2)
    with u_col1:
        ufuk2 = st.radio("Takip eden ufuk (iş günü)", list(beklenti.KOSUL_UFUKLAR), index=1, horizontal=True, key="s11_uf2")
    with u_col2:
        sira2 = st.selectbox("Sıralama ölçütü", list(SIRALAMA_AD_2), format_func=SIRALAMA_AD_2.get, key="s11_sira2")

    vix_serisi = panel["VIX"] if "VIX" in panel.columns else None
    ktab = beklenti.kosullu_olasilik_tablosu(
        g, kosullar=kosullar_listesi, ufuk=ufuk2,
        vix_seviye=vix_serisi, vix_rejim=vix_rejim_sec,
        siralama=sira2, katalog=kat,
    )

    n_kosul_olay = ktab.attrs.get("n_olay", 0)
    bugun_aktif = ktab.attrs.get("bugun_aktif", False)
    kosul_tar = ktab.attrs.get("olay_tarihleri", pd.DatetimeIndex([]))

    km1, km2, km3 = st.columns(3)
    km1.metric("Bağımsız Dönem Sayısı (n)", int(n_kosul_olay))
    km2.metric("Takip Eden Ufuk", f"{ufuk2} iş günü")
    km3.metric("Son İş Gününde Koşul Aktif mi?", "Evet (Aktif)" if bugun_aktif else "Hayır")

    if n_kosul_olay == 0 or len(ktab) == 0:
        st.warning("Seçilen koşulların birlikte sağlandığı geçmiş dönem bulunamadı. Koşulları gevşetmeyi deneyin.")
    else:
        if n_kosul_olay < 15:
            st.warning(f"Bu koşul kombinasyonu geçmişte yalnızca n={n_kosul_olay} bağımsız dönemde sağlandı (n < 15); "
                       "sonuçlar istatistiksel olarak kırılgan olabilir.")

        dk = ktab.dropna(subset=["medyan_kosullu", "yukari_olasiligi"]).copy()
        if len(dk):
            dk = dk.iloc[::-1]
            fig2 = make_subplots(
                rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                subplot_titles=(
                    f"Koşullu Medyan vs Koşulsuz Medyan (t+{ufuk2}g, % / bp)",
                    f"Yukarı Olasılığı (%) vs Koşulsuz Yukarı (%) (t+{ufuk2}g)",
                ),
            )
            renk_m = ["#bdbdbd" if y else ("#2a9d8f" if v >= 0 else "#d62728")
                      for y, v in zip(dk["yetersiz"], dk["medyan_fark"])]
            fig2.add_trace(
                go.Bar(
                    y=dk["hedef"], x=dk["medyan_kosullu"], orientation="h",
                    marker_color=renk_m, name="Koşullu Medyan",
                    customdata=np.c_[dk["medyan_kosulsuz"], dk["medyan_fark"], dk["birim"], dk["n_kosullu"]],
                    hovertemplate="%{y}<br>Koşullu Medyan: %{x:+.2f} %{customdata[2]}<br>Koşulsuz: %{customdata[0]:+.2f} (Fark: %{customdata[1]:+.2f})<br>n=%{customdata[3]:.0f}<extra></extra>",
                ),
                row=1, col=1,
            )
            fig2.add_trace(
                go.Scatter(
                    y=dk["hedef"], x=dk["medyan_kosulsuz"], mode="markers",
                    marker=dict(color="#111111", size=7, symbol="diamond"), name="Koşulsuz Medyan",
                    hovertemplate="%{y}<br>Koşulsuz Medyan: %{x:+.2f}<extra></extra>",
                ),
                row=1, col=1,
            )
            fig2.add_vline(x=0, line=dict(color="#555", width=1, dash="dot"), row=1, col=1)

            fig2.add_trace(
                go.Bar(
                    y=dk["hedef"], x=dk["yukari_olasiligi"], orientation="h",
                    marker_color="#3b6fd4", name="Koşullu Yukarı Olasılığı (%)",
                    customdata=np.c_[dk["kosulsuz_yukari"], dk["olasilik_farki"], dk["n_kosullu"]],
                    hovertemplate="%{y}<br>Koşullu Yukarı: %%{x:.1f}<br>Koşulsuz Yukarı: %%{customdata[0]:.1f} (ΔP: %{customdata[1]:+.1f} puan)<br>n=%{customdata[2]:.0f}<extra></extra>",
                ),
                row=1, col=2,
            )
            fig2.add_trace(
                go.Scatter(
                    y=dk["hedef"], x=dk["kosulsuz_yukari"], mode="markers",
                    marker=dict(color="#111111", size=7, symbol="diamond"), name="Koşulsuz Yukarı (%)",
                    hovertemplate="%{y}<br>Koşulsuz Yukarı: %%{x:.1f}<extra></extra>",
                ),
                row=1, col=2,
            )
            fig2.add_vline(x=50, line=dict(color="#555", width=1, dash="dot"), row=1, col=2)
            fig2.update_layout(
                height=max(420, 24 * len(dk) + 100),
                margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(orientation="h", y=1.06),
            )
            ortak.goster(fig2)

        ktab_gor = pd.DataFrame({
            "Hedef": ktab["hedef"],
            "Birim": ktab["birim"],
            "n (Koşullu)": ktab["n_kosullu"].astype(int),
            "n (Koşulsuz)": ktab["n_kosulsuz"].astype(int),
            "Yukarı Olasılığı (%)": [_fmt(v, 1) for v in ktab["yukari_olasiligi"]],
            "Koşulsuz Yukarı (%)": [_fmt(v, 1) for v in ktab["kosulsuz_yukari"]],
            "Olasılık Farkı (puan)": [_fmt(v, 1) for v in ktab["olasilik_farki"]],
            "Medyan (Koşullu)": [_fmt(v, 2) for v in ktab["medyan_kosullu"]],
            "Medyan (Koşulsuz)": [_fmt(v, 2) for v in ktab["medyan_kosulsuz"]],
            "Medyan Fark": [_fmt(v, 2) for v in ktab["medyan_fark"]],
            "Q25 (Koşullu)": [_fmt(v, 2) for v in ktab["q25_kosullu"]],
            "Q75 (Koşullu)": [_fmt(v, 2) for v in ktab["q75_kosullu"]],
            "Not": np.where(ktab["yetersiz"], "yetersiz veri (n<15)", ""),
        })
        st.markdown("**Çoklu Koşullu Olasılık ve Medyan Karşılaştırma Tablosu**")
        ortak.tablo(ktab_gor, hide_index=True)

        with st.expander(f"Koşulun sağlandığı bağımsız dönem tarihleri ({len(kosul_tar)} gün, ±5 iş günü ayıklamalı)"):
            st.write(", ".join(t.strftime("%Y-%m-%d") for t in kosul_tar))

ortak.sayfa_sonu(
    "- **Bölüm 1 (Canlı Şok Tarayıcısı):** Son iş günlerinde kendi geçmiş 60 günlük oynaklığının (ex-ante σ) `k` katından "
    "fazla hareket eden varlıkları tespit eder ve geçmişte aynı varlık aynı yönde benzer büyüklükte şok yaşadığında "
    "takip eden 1, 5 ve 20 iş gününde diğer varlıkların nasıl tepki verdiğini gösterir.\n"
    "- **Bölüm 2 (Çoklu Koşullu Olasılık Motoru):** Bir veya iki varlığın M günlük hareket durumu ile VIX rejimi koşulunun "
    "geçmişte birlikte gerçekleştiği bağımsız günleri (±5 iş günü örtüşme ayıklamalı) bulur. Tek başına yukarı olasılığı "
    "yerine **koşulsuz taban oranına göre farka (ΔP ve medyan farkı)** bakılmalıdır; n < 15 olduğunda örneklem küçüktür."
)
