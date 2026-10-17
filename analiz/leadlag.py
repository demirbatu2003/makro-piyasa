"""Lead-lag: gecikmeli çapraz korelasyon (sınırlı kapsam; Granger yok)."""
import numpy as np
import pandas as pd

from .istatistik import fisher_bant, korelasyon_p

ASENKRON_UYARI = "Kapanış saatleri farklı olabilir; gecikmeli ilişki saat farkından kaynaklanabilir, öngörü değildir."


def kapanis_uyarisi(katalog, x, y):
    """Katalogdaki kapanis_notu'ndan iki seri için uyarı metni (katalog yoksa/ not yoksa genel uyarı)."""
    if katalog is None or "kapanis_notu" not in katalog.columns:
        return ASENKRON_UYARI
    k = katalog.set_index("kod")["kapanis_notu"]
    nx = k.get(x, None)
    ny = k.get(y, None)
    if pd.isna(nx) or pd.isna(ny) or nx is None or ny is None:
        return ASENKRON_UYARI
    if nx == ny:
        return f"Kapanış notu aynı ({nx})."
    return f"{x}: {nx} | {y}: {ny}. {ASENKRON_UYARI}"


def capraz_korelasyon(getiri, x, y, gecikmeler=(-1, 0, 1), yontem="spearman", katalog=None, min_gozlem=30):
    """corr(X(t-k), Y(t)); k>0 => X, Y'yi k adım ÖNDEN gider (X lead). k<0 => Y, X'i önden gider.
    Gecikme satır cinsindendir: günlük getiri verilirse gün, haftalık getiri
    (getiriler.haftalik_getiriler) verilirse hafta. İkili tam gözlem, ileri doldurma yok.
    Döner: gecikme, r, n, p, alt, ust, anlamli (p<0.05, çoklu test düzeltmesiz), uyari."""
    uyari = kapanis_uyarisi(katalog, x, y)
    satir = []
    for k in gecikmeler:
        xs = getiri[x].shift(k)
        ok = xs.notna() & getiri[y].notna()
        n = int(ok.sum())
        r = np.nan
        if n >= min_gozlem:
            r = pd.concat([xs[ok], getiri[y][ok]], axis=1).corr(method=yontem).iloc[0, 1]
        alt, ust = fisher_bant(r, n)
        p = float(korelasyon_p(r, n))
        satir.append(dict(gecikme=k, r=r, n=n, p=p, alt=float(alt), ust=float(ust),
                          anlamli=bool(p < 0.05) if np.isfinite(p) else False,
                          uyari=uyari if k != 0 else uyari + " (k=0: eşzamanlı)"))
    return pd.DataFrame(satir)
