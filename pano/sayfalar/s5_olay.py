import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import olay  # noqa: E402

UFUKLAR = (0, 1, 5)
POLITIKA_GUNLUK = ("FED", "ECB")

ortak.sayfa_basi("5 Büyük Hareket (Event Study)",
                 "Olay sayısı küçükse medyan anlamsızdır. Tek bir olaydan genelleme yapılmaz; sonuçlar sonraki dönemde tekrar "
                 "doğrulanmadan 'kural' sayılmamalıdır.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
g = ortak.getiri(a)
et = ortak.kod_etiket(kat)
tab1, tab2 = st.tabs(["Büyük hareket (σ)", "Politika faizi karar günleri"])

with tab1:
    kodlar = list(g.columns)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        tetik = st.selectbox("Tetikleyici varlık", kodlar, index=kodlar.index("BTC") if "BTC" in kodlar else 0, format_func=et)
    with c2:
        yon = st.selectbox("Yön", ["her_ikisi", "yukari", "asagi"], format_func={"her_ikisi": "Her ikisi", "yukari": "Yukarı", "asagi": "Aşağı"}.get)
    with c3:
        k = st.number_input("Eşik (σ katı)", 1.0, 5.0, 2.0, 0.5)
    with c4:
        sp = st.number_input("σ penceresi (gün)", 20, 250, 60, 10)
    with c5:
        ayikla = st.number_input("Ardışık olay ayıklama (gün)", 0, 30, 5)
    olaylar, ozet = olay.olay_tepkileri(g, tetik, k=k, ufuklar=UFUKLAR, sigma_pencere=int(sp), yon=yon, ayikla_gun=int(ayikla))
    st.subheader("%s için ±%gσ olayları" % (tetik, k))
    if len(olaylar) == 0:
        st.info("Bu ayarlarla olay bulunamadı.")
    else:
        sayim = olaylar.groupby("yon").size()
        m = st.columns(3)
        m[0].metric("Toplam olay (n)", len(olaylar))
        m[1].metric("Yukarı", int(sayim.get("yukari", 0)))
        m[2].metric("Aşağı", int(sayim.get("asagi", 0)))
        st.caption("σ yalnız geçmiş %d gün (bugün hariç, ex-ante); bir olaydan sonraki %d gözlem içindeki olaylar atılır. "
                   "n < 20 ise 'yetersiz veri' etiketi konur ve satır gri gösterilir." % (sp, ayikla))
        with st.expander("Olay günleri"):
            ortak.tablo(olaylar.rename(columns={"getiri": "getiri (log)", "sigma": "σ (önceki gün)", "z": "z"}))

        ozet = ozet.copy()
        ozet["durum"] = np.where(ozet["yetersiz"], "yetersiz veri", "")
        yonler = [y for y in ("yukari", "asagi") if y in set(ozet["yon"])]
        yn = st.radio("Gösterilecek yön", yonler, horizontal=True, format_func={"yukari": "Yukarı olaylar", "asagi": "Aşağı olaylar"}.get)
        uf = st.radio("Ufuk", list(UFUKLAR), horizontal=True, format_func=lambda u: "t+%d (kümülatif)" % u)
        d = ozet[(ozet["yon"] == yn) & (ozet["ufuk"] == uf)].sort_values("medyan", ascending=False)
        nol = int((olaylar["yon"] == yn).sum())
        if len(d):
            renk = ["#bdbdbd" if y else "#3b6fd4" for y in d["yetersiz"]]
            fg = go.Figure(go.Bar(x=d["hedef"], y=d["medyan"] * 100,
                                  error_y=dict(type="data", symmetric=False, array=(d["q75"] - d["medyan"]) * 100,
                                               arrayminus=(d["medyan"] - d["q25"]) * 100),
                                  marker_color=renk, customdata=np.c_[d["n"], d["durum"]],
                                  hovertemplate="%{x}<br>medyan %{y:.2f}%<br>n=%{customdata[0]} %{customdata[1]}<extra></extra>"))
            fg.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                             title=dict(text="%s %s olay (n=%d), t+%d medyan tepki (çubuk = çeyrekler arası; gri = yetersiz veri)" % (
                                 tetik, yn, nol, uf), font=dict(size=13)), yaxis_title="% (faizde bp/100)")
            fg.update_xaxes(tickangle=90, tickfont=dict(size=9))
            ortak.goster(fg)
        gor = ozet[ozet["yon"] == yn].assign(medyan=lambda d_: d_["medyan"] * 100).pivot(index="hedef", columns="ufuk", values=["medyan", "n"])
        gor.columns = ["%s t+%d" % (c, u) for c, u in gor.columns]
        gor["etiket"] = np.where(ozet[(ozet["yon"] == yn) & (ozet["ufuk"] == 0)].set_index("hedef")["yetersiz"].reindex(gor.index).fillna(True), "yetersiz veri", "")
        st.markdown("**Hedef varlıklar** (medyan kümülatif getiri, %; faizlerde bp/100)")
        ortak.tablo(gor.sort_values("medyan t+0", ascending=False))
        st.caption("Eşzamanlı (t+0) tepki çoğu zaman kapanış saati farkını da içerir: Asya, ABD hareketinden önce kapandığı için "
                   "Asya getirisi t+1'de görünür. t+0 ile t+1 ayrı gösterilir.")

with tab2:
    pol = ortak.politika_olaylari(a.dmg)
    pol = pol[pol["kod"].isin(POLITIKA_GUNLUK)]
    st.markdown("Yalnız günlük çözünürlüklü politika serileri (**FED**, **ECB**) gösterilir. BIS serileri aylıktır (ay başı tarihli); "
                "karar günü bilinmediği için olay çalışması yapılmaz.")
    pk = st.selectbox("Politika faizi", list(POLITIKA_GUNLUK))
    yon2 = st.radio("Karar yönü", ["tümü", "artış", "indirim"], horizontal=True)
    p = pol[pol["kod"] == pk].copy()
    if yon2 == "artış":
        p = p[p["degisim"] > 0]
    elif yon2 == "indirim":
        p = p[p["degisim"] < 0]
    ortak.tablo(p.rename(columns={"tarih": "tarih", "onceki": "önceki", "yeni": "yeni", "degisim": "değişim"}), hide_index=True)
    idx = g.index
    pos = idx.searchsorted(p["tarih"].to_numpy())
    pos = pos[pos < len(idx)]
    tarih = idx[pos]
    if len(tarih) == 0:
        st.info("Olay bulunamadı.")
    else:
        rows = []
        for h in UFUKLAR:
            kum = olay._ileri_kumulatif(g, tarih, h)
            for c in g.columns:
                v = kum[c].dropna()
                if len(v):
                    rows.append(dict(hedef=c, ufuk="t+%d" % h, n=len(v), medyan=v.median() * 100, q25=v.quantile(.25) * 100, q75=v.quantile(.75) * 100))
        r = pd.DataFrame(rows)
        piv = r.pivot(index="hedef", columns="ufuk", values="medyan")
        piv["n (t+0)"] = r[r["ufuk"] == "t+0"].set_index("hedef")["n"]
        piv["etiket"] = np.where(piv["n (t+0)"] < 20, "yetersiz veri", "")
        st.markdown("**Karar gününde ve sonrasında medyan getiri** (%% ; faizlerde bp/100). Karar sayısı: %d." % len(tarih))
        ortak.tablo(piv.sort_values("t+0", ascending=False))
        st.warning("Karar sayısı çoğu zaman 20'nin altındadır; 'yetersiz veri' etiketli satırlar genelleme için kullanılamaz. FRED serisinin değişim "
                   "tarihi yürürlük günüdür, açıklama bir gün önce olabilir; ayrıca ABD ve Avrupa kapanış saatleri farklıdır.")

ortak.sayfa_sonu("Seçilen varlık, son 60 günlük oynaklığının 2 katından fazla hareket ettiğinde 'olay' sayılır. Tablo ve grafik, "
                 "diğer varlıkların aynı gün (t+0), ertesi gün (t+1) ve 5 gün sonra (t+5) kümülatif medyan getirisini verir. "
                 "Olay sayısı n her zaman yanındadır; küçük n'de medyan tesadüf olabilir.")
