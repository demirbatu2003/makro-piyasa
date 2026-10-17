import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from scipy.cluster.hierarchy import dendrogram  # noqa: E402

from analiz import ag, korelasyon  # noqa: E402


@st.cache_data(show_spinner="Kenar kararlılığı hesaplanıyor...")
def kararlilik(dmg, baz, kategoriler, pencere, yontem):
    g = ortak.getiri(ortak.Ayar(baz, pencere, yontem, kategoriler, dmg))
    return ag.kenar_kararliligi(g, pencere=pencere, adim=20, yontem=yontem, en_fazla_pencere=30)


def ag_cizimi(kenar, dug, degisen, baslik, kat_rengi):
    fig = go.Figure()
    p = dug.set_index("kod")
    for _, e in kenar.iterrows():
        anahtar = frozenset((e["a"], e["b"]))
        vurgu = anahtar in degisen
        fig.add_trace(go.Scatter(
            x=[p.loc[e["a"], "x"], p.loc[e["b"], "x"]], y=[p.loc[e["a"], "y"], p.loc[e["b"], "y"]], mode="lines",
            line=dict(width=1 + 6 * max(float(e["rho"]), 0.0) ** 2, color="#e4572e" if vurgu else "rgba(130,130,130,0.7)"),
            hoverinfo="text", text="%s - %s: rho=%.2f%s" % (e["a"], e["b"], e["rho"], " (değişen kenar)" if vurgu else ""),
            showlegend=False))
    for kt in dict.fromkeys(dug["kategori"].fillna("?")):
        d = dug[dug["kategori"].fillna("?") == kt]
        fig.add_trace(go.Scatter(x=d["x"], y=d["y"], mode="markers+text", text=d["kod"], textposition="top center",
                                 textfont=dict(size=9), marker=dict(size=9 + 2 * d["derece"], color=kat_rengi.get(kt, "#999"),
                                                                    line=dict(width=1, color="white")),
                                 name=ortak.KAT_AD.get(kt, kt), hovertext=d["kod"] + " (derece " + d["derece"].astype(str) + ")", hoverinfo="text"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(title=dict(text=baslik, font=dict(size=13)), height=560, margin=dict(l=5, r=5, t=40, b=5),
                      legend=dict(orientation="h", y=-0.02))
    return fig


def dendrogram_fig(sonuc, k):
    d = dendrogram(sonuc["Z"], labels=sonuc["kodlar"], no_plot=True)
    fig = go.Figure()
    for ic, dc in zip(d["icoord"], d["dcoord"]):
        fig.add_trace(go.Scatter(x=ic, y=dc, mode="lines", line=dict(color="#555", width=1), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(tickvals=[5 + 10 * i for i in range(len(d["ivl"]))], ticktext=d["ivl"], tickangle=90, tickfont=dict(size=8))
    fig.update_yaxes(title="uzaklık sqrt(2(1-rho))")
    fig.update_layout(title=dict(text="Dendrogram (average linkage)", font=dict(size=13)), height=480,
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig


ortak.sayfa_basi("3 Ağ ve Kümeler",
                 "Ağaçta kenar yok demek 'bağlı değil' demek değildir; yalnızca en güçlü ve ağaç yapısına uyan bağlar çizilir.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
g = ortak.getiri(a)
if g.shape[1] < 3:
    st.warning("Ağ için en az 3 seri gerekir; kategori filtresini genişletin.")
    st.stop()
kt = kat.set_index("kod")["kategori"].to_dict()

c1, c2 = st.columns(2)
with c1:
    t1 = st.date_input("Zaman noktası 1 (sol)", g.index[-1].date(), min_value=g.index[300].date(), max_value=g.index[-1].date())
with c2:
    t2 = st.date_input("Zaman noktası 2 (sağ)", g.index[-251].date(), min_value=g.index[300].date(), max_value=g.index[-1].date())

res = {}
for ad, t in (("t1", t1), ("t2", t2)):
    corr, n = korelasyon.korelasyon_matrisi(g, a.pencere, pd.Timestamp(t), a.yontem)
    kenar, dug, elenen = ag.mst_kenarlari(corr, kategori=kt)
    res[ad] = dict(corr=corr, n=n, kenar=kenar, dug=dug, elenen=elenen, t=t)

deg = ag.mst_degisim(res["t1"]["kenar"], res["t2"]["kenar"])
d1 = {frozenset((r.a, r.b)) for r in deg.itertuples() if r.durum == "sadece_1"}
d2 = {frozenset((r.a, r.b)) for r in deg.itertuples() if r.durum == "sadece_2"}

st.subheader("Minimum spanning tree (MST)")
cl, cr = st.columns(2)
for kol, ad, dd in ((cl, "t1", d1), (cr, "t2", d2)):
    r = res[ad]
    with kol:
        ortak.goster(ag_cizimi(r["kenar"], r["dug"], dd, "%s - %dg pencere, %s" % (r["t"], a.pencere, a.yontem.capitalize()), ortak.KAT_RENK))
        nd = len(r["dug"])
        st.caption("Düğüm: %d | kenar: %d (beklenen n-1 = %d) %s. Turuncu kenar = diğer zaman noktasında olmayan kenar. "
                   "Kenar kalınlığı = korelasyon. %s" % (
                       nd, len(r["kenar"]), nd - 1, "- tutarlı" if len(r["kenar"]) == nd - 1 else "- UYARI: tutarsız",
                       ("Yetersiz gözlem nedeniyle ağaç dışı kalan seriler: " + ", ".join(r["elenen"])) if r["elenen"] else ""))
st.write("Kenar değişimi: %d ortak, %d yalnız sol, %d yalnız sağ." % (
    (deg["durum"] == "ortak").sum(), (deg["durum"] == "sadece_1").sum(), (deg["durum"] == "sadece_2").sum()))

# ---- kenar listesi + kararlılık
st.subheader("Kenar listesi ve kararlılık")
kar = kararlilik(a.dmg, a.baz, a.kategoriler, a.pencere, a.yontem)
r1 = res["t1"]
kl = r1["kenar"].copy()
nn = r1["n"]
kl["n (ortak gözlem)"] = [int(nn.loc[x, y]) for x, y in zip(kl["a"], kl["b"])]
anahtar = {frozenset((x, y)): o for x, y, o in zip(kar["a"], kar["b"], kar["oran"])}
kl["kararlılık %"] = [100 * anahtar.get(frozenset((x, y)), 0.0) for x, y in zip(kl["a"], kl["b"])]
kl["durum"] = ["yalnız bu noktada" if frozenset((x, y)) in d1 else "iki noktada da" for x, y in zip(kl["a"], kl["b"])]
kl = kl.sort_values("rho", ascending=False)
ortak.tablo(kl.rename(columns={"a": "A", "b": "B", "uzaklik": "uzaklık"}), hide_index=True,
            column_config={"rho": st.column_config.NumberColumn("rho", format="%.2f"),
                           "uzaklık": st.column_config.NumberColumn(format="%.2f"),
                           "kararlılık %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%")})
st.caption("Kararlılık: %d çakışan/kayan %dg pencerede (20 günlük adım, en son 30 pencere) kenarın MST'de görülme yüzdesi." % (
    int(kar["pencere_sayisi"].max()) if len(kar) else 0, a.pencere))

# ---- dendrogram
st.subheader("Dendrogram")
corr1 = r1["corr"]
dend = ag.hiyerarsik_kumeleme(corr1)
if dend["Z"] is not None:
    k = st.slider("Küme sayısı", 2, 10, 6)
    cc, ck = st.columns([3, 2])
    with cc:
        ortak.goster(dendrogram_fig(dend, k))
    with ck:
        lab = ag.kume_etiketleri(dend, k)
        tbl = pd.DataFrame({"küme": lab}).rename_axis("kod").reset_index()
        tbl["kategori"] = tbl["kod"].map(kt)
        ozet = tbl.groupby("küme")["kod"].apply(lambda s: ", ".join(s)).reset_index().rename(columns={"kod": "seriler"})
        ortak.tablo(ozet, hide_index=True)
    if dend["elenenler"]:
        st.caption("Yetersiz gözlem nedeniyle kümelemeye alınmayan: " + ", ".join(dend["elenenler"]))

st.info("Metodoloji: mesafe d = sqrt(2(1-rho)); MST yalnız n-1 kenar gösterir ve çoğu ilişkiyi gizler. Düğüm rengi = varlık sınıfı. "
        "Yerleşim sabit tohumlu bir kuvvet algoritmasıdır; eksenlerin anlamı yoktur, yalnız bağlantılar önemlidir.")
ortak.sayfa_sonu("Her varlık bir nokta; çizgiler en güçlü bağları gösteren ağaçtır. Aynı renkteki ve birbirine yakın düğümler "
                 "birlikte hareket eden gruplardır. Turuncu çizgiler iki zaman noktası arasında değişen bağlardır. "
                 "Dendrogramda alçakta birleşen varlıklar daha benzerdir. Grup isimlendirmesi (risk-on, güvenli liman vb.) "
                 "okuyucunun yorumudur; pano etiket üretmez.")
