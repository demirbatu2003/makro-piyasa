"""Event study: |getiri| > k*sigma olayları ve diğer serilerin kümülatif tepkileri."""
import numpy as np
import pandas as pd
from scipy import stats

UFUKLAR = (0, 1, 5, 20)


def olaylari_bul(seri, k=2.0, sigma_pencere=60, min_sigma_gun=40, yon="her_ikisi", ayikla_gun=5):
    """Tetikleyici seride olay günleri. sigma = ÖNCEKİ sigma_pencere günün std'si (bugün hariç,
    ex-ante, bakış-ileri sızıntı yok). Çakışan olaylar: bir olaydan sonraki `ayikla_gun`
    gözlem içindeki olaylar atılır (ilk olay kalır; ayni yönden bağımsız). Döner: DataFrame
    (tarih index'li): getiri, sigma, z, yon."""
    s = seri.dropna()
    sigma = s.rolling(sigma_pencere, min_periods=min_sigma_gun).std().shift(1)
    z = s / sigma
    mask = z.abs() > k
    if yon == "yukari":
        mask &= z > 0
    elif yon == "asagi":
        mask &= z < 0
    adaylar = s.index[mask.fillna(False)]
    konum = {t: i for i, t in enumerate(s.index)}
    secilen, son = [], -10**9
    for t in adaylar:
        i = konum[t]
        if i - son > ayikla_gun:
            secilen.append(t)
            son = i
    ol = pd.DataFrame({"getiri": s.loc[secilen], "sigma": sigma.loc[secilen], "z": z.loc[secilen]})
    ol["yon"] = np.where(ol["z"] > 0, "yukari", "asagi")
    return ol


def _ileri_kumulatif(getiri, tarihler, ufuk):
    """Her olay günü t için t..t+ufuk satır toplamı. Eksik gün getirisi 0 sayılır (tatil sonrası
    getiri çok günlü olduğundan toplam doğru kalır); pencerede hiç veri yoksa veya
    seri t+ufuk'a kadar uzanmıyorsa NaN."""
    idx = getiri.index
    konum = idx.get_indexer(tarihler)
    arr = getiri.to_numpy(float)
    dolu = np.isfinite(arr)
    cs = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(np.where(dolu, arr, 0.0), axis=0)])
    cn = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(dolu, axis=0)])
    son = konum + ufuk
    gecerli = (son < len(idx)) & (konum >= 0)
    sonc = np.where(gecerli, son, 0)
    top = cs[sonc + 1] - cs[konum]
    adet = cn[sonc + 1] - cn[konum]
    top = np.where(gecerli[:, None] & (adet > 0), top, np.nan)
    return pd.DataFrame(top, index=tarihler, columns=getiri.columns)


def olay_tepkileri(getiri, tetik, k=2.0, ufuklar=UFUKLAR, sigma_pencere=60, yon="her_ikisi",
                   ayikla_gun=5, min_olay=20, hedefler=None):
    """Event study. tetik sütunundaki olaylar için diğer serilerin t+0..t+h kümülatif tepkisi.
    yon='her_ikisi' ise yukarı ve aşağı AYRI satırlarda verilir.
    Döner: olaylar (DataFrame), ozet (uzun tablo: yon, hedef, ufuk, n, ortalama, medyan, q25, q75,
    ci_alt, ci_ust [ortalama için t-güven aralığı], poz_orani, ayni_yon_orani, yetersiz).
    n < min_olay -> yetersiz=True (ekranda 'yetersiz veri')."""
    olaylar = olaylari_bul(getiri[tetik], k, sigma_pencere, yon=yon, ayikla_gun=ayikla_gun)
    hedefler = [c for c in (hedefler or getiri.columns) if c != tetik]
    satir = []
    for yn in ("yukari", "asagi"):
        ol = olaylar[olaylar["yon"] == yn]
        if len(ol) == 0:
            continue
        for h in ufuklar:
            kum = _ileri_kumulatif(getiri[hedefler], ol.index, h)
            for c in hedefler:
                v = kum[c].dropna()
                n = len(v)
                if n == 0:
                    continue
                ort = v.mean()
                if n > 1:
                    se = v.std(ddof=1) / np.sqrt(n)
                    tk = stats.t.ppf(0.975, n - 1)
                    lo, hi = ort - tk * se, ort + tk * se
                else:
                    lo = hi = np.nan
                isaret = 1.0 if yn == "yukari" else -1.0
                satir.append(dict(yon=yn, hedef=c, ufuk=h, n=n, ortalama=ort, medyan=v.median(),
                                  q25=v.quantile(0.25), q75=v.quantile(0.75), ci_alt=lo, ci_ust=hi,
                                  poz_orani=(v > 0).mean(), ayni_yon_orani=(v * isaret > 0).mean(),
                                  yetersiz=n < min_olay))
    cols = ["yon", "hedef", "ufuk", "n", "ortalama", "medyan", "q25", "q75", "ci_alt", "ci_ust",
            "poz_orani", "ayni_yon_orani", "yetersiz"]
    return olaylar, pd.DataFrame(satir, columns=cols)
