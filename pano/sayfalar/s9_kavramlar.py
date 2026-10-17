"""Kavramlar sayfası: içerik pano/kavramlar_icerik.py içindedir; yeni kavram orada eklenir."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import istatistik, rejim  # noqa: E402
from kavramlar_icerik import KAVRAMLAR  # noqa: E402


# ---------------------------------------------------------------- canlı örnekler (hata verirse sayfa yine render olur)
@st.cache_data(show_spinner=False)
def _canli_veri(dmg):
    """Canlı örnekler için hesaplar. Her parça kendi try bloğunda; başarısız olan None kalır."""
    s = {"vix": None, "beta": None, "cift": None}
    try:
        _, panel = ortak.yukle(dmg)
        v = panel["VIX"].dropna()
        s["vix"] = dict(deger=float(v.iloc[-1]), tarih=v.index[-1],
                        rejim=str(rejim.vix_rejimi(v).iloc[-1]), ort=float(v.tail(250).mean()))
    except Exception:
        pass
    try:
        g = ortak.getiri_tum(dmg, "USD")
        bt = rejim.beta_tablosu(g, "SPX", pencere=250)
        b = bt.loc["BTC"]
        gg = g.iloc[-250:][["SPX", "BTC"]].dropna()  # beta_tablosu ile aynı örneklem
        s["beta"] = dict(beta=float(b["beta"]), se=float(b["se"]), n=int(b["n"]),
                         rho=float(gg["BTC"].corr(gg["SPX"])), sx=float(gg["SPX"].std()),
                         sy=float(gg["BTC"].std()), bitis=gg.index[-1])
    except Exception:
        pass
    try:
        g = ortak.getiri_tum(dmg, "USD")
        gg = g[["BTC", "NASDAQ"]].dropna().tail(250)
        n = len(gg)
        rp = float(gg["BTC"].corr(gg["NASDAQ"], method="pearson"))
        rs = float(gg["BTC"].corr(gg["NASDAQ"], method="spearman"))
        alt, ust = istatistik.fisher_bant(rs, n)
        s["cift"] = dict(n=n, rp=rp, rs=rs, alt=float(alt), ust=float(ust), bitis=gg.index[-1])
    except Exception:
        pass
    return s


def _tr(x, d=2):
    return ("%.*f" % (d, x)).replace(".", ",")


def _canli_vix(s):
    v = s["vix"]
    return ("VIX son değer: **%s** (%s). Rejim: **%s** (eşikler 15 ve 25). Son 250 gözlemin ortalaması %s. "
            "Günlük karşılık ≈ %%%s, aylık ≈ %%%s." % (
                _tr(v["deger"]), v["tarih"].date(), v["rejim"], _tr(v["ort"], 1),
                _tr(v["deger"] / np.sqrt(252)), _tr(v["deger"] / np.sqrt(12))))


def _canli_beta(s):
    b = s["beta"]
    return ("BTC'nin SPX'e göre betası (son 250 gün, USD baz, %s'e kadar, n=%d): **%s** (se %s). "
            "Yorum: SPX %%1 oynarsa BTC ortalama %%%s oynamış. "
            "Kontrol: ρ × σ_BTC / σ_SPX = %s × %s / %s = %s (Pearson ρ ile)." % (
                b["bitis"].date(), b["n"], _tr(b["beta"]), _tr(b["se"]), _tr(b["beta"]),
                _tr(b["rho"]), _tr(b["sy"], 4), _tr(b["sx"], 4), _tr(b["rho"] * b["sy"] / b["sx"])))


def _canli_ps(s):
    c = s["cift"]
    return ("BTC - NASDAQ, son %d ortak gün (%s'e kadar, USD baz): Pearson **%s**, Spearman **%s**. "
            "Fark (Spearman - Pearson): %s." % (c["n"], c["bitis"].date(), _tr(c["rp"]), _tr(c["rs"]), _tr(c["rs"] - c["rp"])))


def _canli_fisher(s):
    c = s["cift"]
    return ("BTC - NASDAQ Spearman r = %s, n = %d: yaklaşık %%95 Fisher aralığı **[%s ; %s]**. "
            "Günlük getiriler bağımsız varsayılır; gerçek aralık biraz daha geniş olabilir." % (
                _tr(c["rs"]), c["n"], _tr(c["alt"]), _tr(c["ust"])))


CANLI = {  # anahtar -> (canlı veri alanı, metin fonksiyonu). Yeni örnek için buraya ekleyin.
    "vix": ("vix", _canli_vix),
    "beta": ("beta", _canli_beta),
    "pearson_spearman": ("cift", _canli_ps),
    "korelasyon_ozet": ("cift", _canli_ps),
    "fisher": ("cift", _canli_fisher),
}


def canli_goster(anahtar, canli):
    if not anahtar or anahtar not in CANLI:
        return
    alan, fn = CANLI[anahtar]
    st.markdown("#### Panodan canlı örnek")
    if canli.get(alan) is None:
        st.info("Canlı örnek şu an hesaplanamadı (veri okunamadı ya da yetersiz). Sayfanın geri kalanı etkilenmez.")
        return
    try:
        st.success(fn(canli))
    except Exception:
        st.info("Canlı örnek şu an hesaplanamadı. Sayfanın geri kalanı etkilenmez.")


def kavram_goster(k, canli):
    st.header(k["baslik"])
    st.markdown("#### Ne olduğu")
    st.markdown(k["ne"])
    st.markdown("#### Neden önemli, piyasada nasıl kullanılır")
    st.markdown(k["neden"])
    st.markdown("#### Nasıl okunur")
    st.markdown(k["okuma"])
    st.markdown("#### Matematik")
    for f in k.get("formuller", []):
        st.latex(f)
    if k.get("semboller"):
        st.markdown("**Semboller:**")
        st.markdown("\n".join("- `%s`: %s" % (s, a) for s, a in k["semboller"]))
    if k.get("not_"):
        st.caption(k["not_"])
    if k.get("ornek"):
        st.markdown("**Adım adım örnek**")
        st.markdown(k["ornek"])
    canli_goster(k.get("canli"), canli)
    st.markdown("#### Bu panoda nerede kullanılıyor")
    st.markdown("\n".join("- " + p for p in k.get("panoda", [])))
    if k.get("iliski"):
        st.markdown("#### Diğer kavramlarla ilişkisi")
        st.markdown("\n".join("- " + p for p in k["iliski"]))


st.title("Kavramlar")
st.caption("Panoda geçen temel kavramların sade açıklaması, formülleri ve panodan canlı örnekleri. "
           "Bu sayfa bilgi amaçlıdır; yatırım tavsiyesi değildir.")

try:
    canli = _canli_veri(ortak.db_damga())
except Exception:
    canli = {}

st.markdown("**İçindekiler**")
st.markdown("\n".join("%d. **%s**: %s" % (i + 1, k["baslik"], k["kisa"]) for i, k in enumerate(KAVRAMLAR)))
st.caption("Aşağıdaki sekmelerden bir kavram seçin.")

sekmeler = st.tabs([k["baslik"] for k in KAVRAMLAR])
for sek, k in zip(sekmeler, KAVRAMLAR):
    with sek:
        kavram_goster(k, canli)
