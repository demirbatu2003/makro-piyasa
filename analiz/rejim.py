"""VIX rejimi, rejime koşullu korelasyon ve beta tablosu."""
import numpy as np
import pandas as pd

from .korelasyon import korelasyon_matrisi

REJIMLER = ("sakin", "normal", "gergin")


def vix_rejimi(vix_seviye, esikler=(15.0, 25.0)):
    """Mutlak eşikli VIX rejimi: < alt sakin, alt-üst normal, > üst gergin (TASARIM varsayılanı).
    Girdi VIX SEVİYESİ (getiri değil). Eşikler sabit olduğundan bakış-ileri sızıntı yok.
    Döner: kategorik Series (NaN'ler korunur)."""
    alt, ust = esikler
    v = vix_seviye.astype(float)
    r = pd.Series(np.where(v < alt, "sakin", np.where(v > ust, "gergin", "normal")),
                  index=v.index, dtype=object)
    r[v.isna()] = np.nan
    return pd.Series(pd.Categorical(r, categories=list(REJIMLER)), index=v.index, name="rejim")


def rejim_korelasyonlari(getiri, rejim, yontem="spearman", min_gozlem=40, min_rejim_gun=60):
    """Rejime koşullu korelasyon matrisleri. Rejim günü sayısı min_rejim_gun'den azsa o rejimin
    matrisi tamamen NaN ve yeterli=False. Döner: (sonuc, ozet)
    sonuc: {rejim: (corr, n)}; ozet: DataFrame(rejim, gun_sayisi, yeterli)."""
    rj = rejim.reindex(getiri.index)
    sonuc, satir = {}, []
    for r in REJIMLER:
        g = getiri[rj == r]
        yeterli = len(g) >= min_rejim_gun
        if yeterli:
            c, n = korelasyon_matrisi(g, None, None, yontem, min_gozlem)
        else:
            c, n = korelasyon_matrisi(g, None, None, yontem, 10**9)
        sonuc[r] = (c, n)
        satir.append({"rejim": r, "gun_sayisi": len(g), "yeterli": yeterli})
    return sonuc, pd.DataFrame(satir)


def beta_tablosu(getiri, referans, pencere=None, bitis=None, min_gozlem=30):
    """Her seri için y = a + beta * x + e (x = referans getirisi), ortak gözlemlerle OLS.
    Döner: DataFrame(index=seri) sütunlar: beta, se, t, r, n. Birim: y birimi / x birimi
    (fiyat getirisi için log-getiri oranı, faiz için bp / log-getiri). 'X %1 hareket ederse
    y ortalama beta kadar % hareket eder' okuması fiyat serileri için geçerlidir.
    n < min_gozlem ise NaN."""
    g = getiri if bitis is None else getiri.loc[:pd.Timestamp(bitis)]
    g = g.iloc[-pencere:] if pencere else g
    x_all = g[referans]
    satir = {}
    for kod in g.columns:
        if kod == referans:
            continue
        ok = x_all.notna() & g[kod].notna()
        n = int(ok.sum())
        if n < min_gozlem:
            satir[kod] = dict(beta=np.nan, se=np.nan, t=np.nan, r=np.nan, n=n)
            continue
        x, y = x_all[ok].to_numpy(), g[kod][ok].to_numpy()
        xc = x - x.mean()
        sxx = (xc**2).sum()
        beta = (xc * (y - y.mean())).sum() / sxx
        res = (y - y.mean()) - beta * xc
        se = np.sqrt((res**2).sum() / (n - 2) / sxx)
        r = np.corrcoef(x, y)[0, 1]
        satir[kod] = dict(beta=beta, se=se, t=beta / se if se > 0 else np.nan, r=r, n=n)
    return pd.DataFrame(satir).T[["beta", "se", "t", "r", "n"]].astype({"n": int})
