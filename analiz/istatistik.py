"""Ortak istatistik yardımcıları: Fisher z bandı, p-değeri, Benjamini-Hochberg FDR."""
import numpy as np
from scipy import stats


def fisher_bant(r, n, z_kritik=1.96):
    """Korelasyon için yaklaşık %95 Fisher-z güven aralığı (alt, ust). n<=3 ise NaN.
    Not: örtüşen pencerelerde bağımsız gözlem varsayar, gerçek bant daha geniştir."""
    r = np.asarray(r, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.arctanh(np.clip(r, -0.999999, 0.999999))
        se = 1.0 / np.sqrt(np.where(n > 3, n - 3, np.nan))
        return np.tanh(z - z_kritik * se), np.tanh(z + z_kritik * se)


def korelasyon_p(r, n):
    """İki yönlü p-değeri, t = r*sqrt((n-2)/(1-r^2)) yaklaşımı (Pearson ve Spearman için)."""
    r = np.asarray(r, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        rc = np.clip(r, -1.0, 1.0)
        t = rc * np.sqrt((n - 2) / np.clip(1 - rc**2, 1e-300, None))
        p = 2 * stats.t.sf(np.abs(t), np.where(n > 2, n - 2, np.nan))
    return np.where(np.isfinite(r) & (n > 2), p, np.nan)


def bh_fdr(p, alpha=0.05):
    """Benjamini-Hochberg. p: 1B dizi (NaN'ler yok sayılır). Döner: (q_degeri, anlamli_bool)."""
    p = np.asarray(p, dtype=float)
    q = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    m = int(ok.sum())
    if m == 0:
        return q, np.zeros(p.shape, dtype=bool)
    pv = p[ok]
    sira = np.argsort(pv)
    ranked = pv[sira] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    qq = np.empty(m)
    qq[sira] = np.minimum(ranked, 1.0)
    q[ok] = qq
    return q, np.where(ok, q <= alpha, False)
