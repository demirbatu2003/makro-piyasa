"""Pairwise-complete korelasyon, pencere kuralları, fark matrisleri, rolling, FDR."""
import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata

from .istatistik import bh_fdr, fisher_bant, korelasyon_p

MIN_GOZLEM = {60: 40, 250: 150}


def min_gozlem_varsayilan(pencere):
    """TASARIM kuralı: 60g->40, 250g->150; diğer pencerelerde ~%67 (yukarı yuvarlı)."""
    return MIN_GOZLEM.get(int(pencere), int(np.ceil(0.67 * pencere)))


def ortak_gozlem(getiri):
    """Hücre başına ortak (iki seride de dolu) gözlem sayısı matrisi."""
    m = getiri.notna().astype(float)
    return (m.T @ m).astype(int)


def _pencere_kes(getiri, pencere, bitis):
    g = getiri if bitis is None else getiri.loc[:pd.Timestamp(bitis)]
    return g.iloc[-pencere:] if pencere else g


def korelasyon_matrisi(getiri, pencere=None, bitis=None, yontem="spearman", min_gozlem=None):
    """Pairwise-complete korelasyon. Son `pencere` satır (bitis tarihine kadar).
    Döner: (corr, n). n < min_gozlem olan hücreler NaN. Köşegen: seri yeterli gözlemliyse 1.
    min_gozlem verilmezse pencereye göre TASARIM kuralı (pencere=None -> 30)."""
    g = _pencere_kes(getiri, pencere, bitis)
    if min_gozlem is None:
        min_gozlem = min_gozlem_varsayilan(pencere) if pencere else 30
    n = ortak_gozlem(g)
    c = g.corr(method=yontem, min_periods=2)
    c = c.where(n >= min_gozlem)
    return c, n


def iki_nokta_karsilastirma(getiri, pencere=60, geri=250, yontem="spearman", min_gozlem=None, bitis=None):
    """'Şimdi' ile `geri` satır önce biten aynı uzunlukta pencere + fark matrisi.
    fark_p: Fisher-z ile iki bağımsız örneklem farkı testi (pencereler örtüşmüyorsa geçerli;
    geri < pencere ise örtüşür ve p iyimserdir). Döner dict."""
    g = getiri if bitis is None else getiri.loc[:pd.Timestamp(bitis)]
    simdi, n1 = korelasyon_matrisi(g, pencere, None, yontem, min_gozlem)
    onceki_g = g.iloc[:-geri] if geri else g
    onceki, n0 = korelasyon_matrisi(onceki_g, pencere, None, yontem, min_gozlem)
    fark = simdi - onceki
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.arctanh(simdi.clip(-0.999999, 0.999999)) - np.arctanh(onceki.clip(-0.999999, 0.999999))
        se = np.sqrt(1.0 / (n1.where(n1 > 3) - 3) + 1.0 / (n0.where(n0 > 3) - 3))
        zs = (z / se).to_numpy(dtype=float)
    p = pd.DataFrame(2 * norm.sf(np.abs(zs)), index=simdi.index, columns=simdi.columns)
    return {"simdi": simdi, "onceki": onceki, "fark": fark, "n_simdi": n1, "n_onceki": n0,
            "fark_p": p, "simdi_bitis": g.index[-1] if len(g) else None,
            "onceki_bitis": onceki_g.index[-1] if len(onceki_g) else None}


def ortalama_ikili_korelasyon(corr):
    """Köşegen dışı hücrelerin ortalaması (NaN'ler hariç) - 'piyasa ne kadar tek faktörlü'."""
    a = corr.to_numpy(dtype=float).copy()
    np.fill_diagonal(a, np.nan)
    return float(np.nanmean(a)) if np.isfinite(a).any() else float("nan")


def _rolling_spearman(x, y, pencere, min_gozlem):
    """Pencere içinde ortak-dolu gözlemlerle Spearman."""
    xv, yv = x.to_numpy(float), y.to_numpy(float)
    out = np.full(len(xv), np.nan)
    for i in range(pencere - 1, len(xv)):
        a, b = xv[i - pencere + 1:i + 1], yv[i - pencere + 1:i + 1]
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() >= min_gozlem:
            ra, rb = rankdata(a[ok]), rankdata(b[ok])
            if ra.std() > 0 and rb.std() > 0:
                out[i] = np.corrcoef(ra, rb)[0, 1]
    return pd.Series(out, index=x.index)


def ikili_rolling(getiri, a, b, pencere=60, yontem="spearman", min_gozlem=None):
    """İki seri için rolling korelasyon. Sütunlar: korelasyon, n, alt, ust (Fisher bandı;
    örtüşen pencereler nedeniyle gerçek belirsizlik daha geniştir)."""
    if min_gozlem is None:
        min_gozlem = min_gozlem_varsayilan(pencere)
    ortak = getiri[a].notna() & getiri[b].notna()
    x, y = getiri[a].where(ortak), getiri[b].where(ortak)
    n = ortak.astype(float).rolling(pencere, min_periods=1).sum()
    if yontem == "spearman":
        r = _rolling_spearman(x, y, pencere, min_gozlem)
    else:
        r = x.rolling(pencere, min_periods=min_gozlem).corr(y)
    r = r.where(n >= min_gozlem)
    alt, ust = fisher_bant(r.to_numpy(), n.to_numpy())
    return pd.DataFrame({"korelasyon": r, "n": n.astype(int), "alt": alt, "ust": ust})


def anlamlilik_tablosu(corr, n, alpha=0.05):
    """Üst üçgen çiftler için uzun tablo: a, b, r, n, p, q (BH-FDR), fdr_anlamli.
    Keşif listesi için (v2); matris ekranlarında anlamlılık boyaması yok."""
    kodlar = list(corr.columns)
    iu = np.triu_indices(len(kodlar), k=1)
    r = corr.to_numpy(float)[iu]
    nn = n.to_numpy(float)[iu]
    p = korelasyon_p(r, nn)
    q, an = bh_fdr(p, alpha)
    return pd.DataFrame({"a": [kodlar[i] for i in iu[0]], "b": [kodlar[j] for j in iu[1]],
                         "r": r, "n": nn.astype(int), "p": p, "q": q, "fdr_anlamli": an})
