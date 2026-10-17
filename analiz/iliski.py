"""Ikili iliski araclari (Ekran 1 ve 2): secili aralik ozeti, kismi korelasyon, rolling beta.
Saf fonksiyonlar; ileri doldurma yok, her hesapta yalniz ilgili sutunlarin ortak dolu satirlari kullanilir."""
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from .istatistik import fisher_bant


def _kes(getiri, bas=None, bit=None):
    g = getiri
    if bas is not None:
        g = g.loc[pd.Timestamp(bas):]
    if bit is not None:
        g = g.loc[:pd.Timestamp(bit)]
    return g


def _ols_beta(x, y):
    """y = a + beta*x + e. Doner: beta, se, n (n<3 veya x sabitse NaN)."""
    n = len(x)
    if n < 3:
        return np.nan, np.nan, n
    xc = x - x.mean()
    sxx = float((xc ** 2).sum())
    if sxx <= 0:
        return np.nan, np.nan, n
    yc = y - y.mean()
    beta = float((xc * yc).sum() / sxx)
    res = yc - beta * xc
    se = float(np.sqrt((res ** 2).sum() / (n - 2) / sxx))
    return beta, se, n


def aralik_ozeti(getiri, a, b, bas=None, bit=None):
    """Secilen aralik (bas..bit, dahil) icin TEK korelasyon ozeti. Ortak dolu satirlar kullanilir.
    Doner dict: n, spearman, pearson, sp_alt, sp_ust, pe_alt, pe_ust (Fisher %95; bagimsiz gozlem varsayar),
    beta, beta_se (b ~ a; 'a %1 oynarsa b ortalama beta kadar oynar'), beta_alt, beta_ust (+-1,96 se).
    n < 4 ise tum degerler NaN."""
    g = _kes(getiri[[a, b]], bas, bit).dropna()
    n = len(g)
    nan = float("nan")
    out = dict(n=n, spearman=nan, pearson=nan, sp_alt=nan, sp_ust=nan, pe_alt=nan, pe_ust=nan,
               beta=nan, beta_se=nan, beta_alt=nan, beta_ust=nan)
    if n < 4:
        return out
    x, y = g[a].to_numpy(float), g[b].to_numpy(float)
    if x.std() > 0 and y.std() > 0:
        out["pearson"] = float(np.corrcoef(x, y)[0, 1])
        out["spearman"] = float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])
        for ad, on in (("sp", "spearman"), ("pe", "pearson")):
            lo, hi = fisher_bant(out[on], n)
            out[ad + "_alt"], out[ad + "_ust"] = float(lo), float(hi)
    beta, se, _ = _ols_beta(x, y)
    out.update(beta=beta, beta_se=se, beta_alt=beta - 1.96 * se, beta_ust=beta + 1.96 * se)
    return out


def _kalan(x, Z):
    """x'in Z (sabit terimli) uzerine OLS artigi."""
    A = np.column_stack([np.ones(len(Z)), Z])
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ coef


def kismi_korelasyon(getiri, a, b, kontroller, yontem="spearman", min_gozlem=30):
    """a ve b'nin getirilerini kontrol degiskenlerinin getirilerine OLS ile regres edip ARTIKLARI korele eder.
    Pairwise-complete: a, b ve tum kontrollerin ortak dolu satirlari. Spearman: once her sutunun rank'i alinir
    (ortak satirlar uzerinde). Doner dict: r, n, alt, ust (Fisher; etkin n = n-k), ham (kontrolsuz, ayni satirlarda).
    n < min_gozlem veya n < k+4 ise NaN."""
    kontroller = [k for k in kontroller if k not in (a, b)]
    g = getiri[[a, b] + kontroller].dropna()
    n, k = len(g), len(kontroller)
    nan = float("nan")
    out = dict(r=nan, n=n, alt=nan, ust=nan, ham=nan)
    if n < max(min_gozlem, k + 4):
        return out
    v = g.to_numpy(float)
    if yontem == "spearman":
        v = np.column_stack([rankdata(v[:, i]) for i in range(v.shape[1])])
    if v[:, 0].std() == 0 or v[:, 1].std() == 0:
        return out
    out["ham"] = float(np.corrcoef(v[:, 0], v[:, 1])[0, 1])
    if k == 0:
        out["r"] = out["ham"]
    else:
        ra, rb = _kalan(v[:, 0], v[:, 2:]), _kalan(v[:, 1], v[:, 2:])
        if ra.std() < 1e-12 or rb.std() < 1e-12:
            return out
        out["r"] = float(np.corrcoef(ra, rb)[0, 1])
    lo, hi = fisher_bant(out["r"], n - k)
    out["alt"], out["ust"] = float(lo), float(hi)
    return out


def kismi_korelasyon_matrisi(getiri, kontrol, yontem="spearman", min_gozlem=60):
    """Tek bir kontrol serisi cikarilmis kismi korelasyon matrisi (kontrol sutunu matristen cikar).
    Her cift icin cift + kontrolun ortak dolu satirlari kullanilir. Doner (corr, n); n < min_gozlem hucreleri NaN."""
    kodlar = [c for c in getiri.columns if c != kontrol]
    m = len(kodlar)
    r = np.full((m, m), np.nan)
    nn = np.zeros((m, m), dtype=int)
    for i in range(m):
        ok = getiri[kodlar[i]].notna() & getiri[kontrol].notna()
        nn[i, i] = int(ok.sum())
        r[i, i] = 1.0 if nn[i, i] >= min_gozlem else np.nan
        for j in range(i + 1, m):
            d = kismi_korelasyon(getiri, kodlar[i], kodlar[j], [kontrol], yontem, min_gozlem)
            r[i, j] = r[j, i] = d["r"]
            nn[i, j] = nn[j, i] = d["n"]
    return (pd.DataFrame(r, index=kodlar, columns=kodlar),
            pd.DataFrame(nn, index=kodlar, columns=kodlar))


def rolling_beta(getiri, x, y, pencere=60, min_gozlem=None):
    """Rolling OLS beta (y = a + beta*x). Pencere = son `pencere` SATIR; yalniz ortak dolu satirlar sayilir.
    Doner DataFrame: beta, se, alt, ust (beta +-1,96 se), n. n < min_gozlem (varsayilan ~%67 pencere) NaN.
    Not: pencereler ortusur, noktalar bagimsiz degildir."""
    if min_gozlem is None:
        min_gozlem = int(np.ceil(0.67 * pencere))
    ok = getiri[x].notna() & getiri[y].notna()
    xv, yv = getiri[x].where(ok), getiri[y].where(ok)
    n = ok.astype(float).rolling(pencere, min_periods=1).sum()
    xc, yc = xv - xv.mean(), yv - yv.mean()   # sayisal kararlilik icin tum ornek ortalamasi cikarilir

    def topla(s):
        return s.fillna(0).rolling(pencere, min_periods=1).sum()

    sx, sy, sxx, sxy, syy = topla(xc), topla(yc), topla(xc ** 2), topla(xc * yc), topla(yc ** 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        cxx = sxx - sx ** 2 / n
        cxy = sxy - sx * sy / n
        cyy = syy - sy ** 2 / n
        beta = cxy / cxx
        sse = (cyy - beta * cxy).clip(lower=0)
        se = np.sqrt(sse / (n - 2) / cxx)
    gec = (n >= min_gozlem) & (cxx > 1e-18)
    beta, se = beta.where(gec), se.where(gec)
    return pd.DataFrame({"beta": beta, "se": se, "alt": beta - 1.96 * se, "ust": beta + 1.96 * se, "n": n.astype(int)})
