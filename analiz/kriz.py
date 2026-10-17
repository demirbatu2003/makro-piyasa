"""Kriz ani iliskisi: referans varlik sert dustugunde diger varliklar ne yapiyor? (Ekran 4)
Quantile regression yerine anlasilir iki olcu: exceedance (kuyruk) korelasyonu ve ortak dusus orani."""
import numpy as np
import pandas as pd
from scipy.stats import rankdata


def _kor(x, y, yontem):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan
    if yontem == "spearman":
        x, y = rankdata(x), rankdata(y)
    return float(np.corrcoef(x, y)[0, 1])


def kuyruk_iliskisi(getiri, referans, kuyruk=0.10, yontem="pearson", min_kuyruk=30):
    """Referansin getirisinin alt `kuyruk` payindaki (varsayilan %10) gunler icin, her diger seri ile:
      kor_kuyruk: kuyruk gunlerindeki korelasyon (exceedance correlation)
      kor_normal: kalan (normal) gunlerdeki korelasyon
      ortak_dusus: referans kuyruktayken digerinin de KENDI alt `kuyruk` payinda olma orani
      beklenen: bagimsizlikta beklenen oran (= kuyruk)
      n_kuyruk, n_normal, n, yeterli (n_kuyruk >= min_kuyruk)
    Esikler (her seri icin ayri) ortak dolu satirlar uzerindeki ampirik yuzdeliklerdir (tum ornek; ex-ante degil).
    Dikkat: kuyruga kosullu korelasyon, kirpma nedeniyle bagimsiz veride bile mekanik olarak dusuk cikar;
    kor_kuyruk bu yuzden kor_normal ve ortak_dusus ile birlikte okunmalidir."""
    sat = {}
    for kod in getiri.columns:
        if kod == referans:
            continue
        d = getiri[[referans, kod]].dropna()
        x, y = d[referans].to_numpy(float), d[kod].to_numpy(float)
        n = len(d)
        satir = dict(kor_kuyruk=np.nan, kor_normal=np.nan, ortak_dusus=np.nan, beklenen=kuyruk,
                     n_kuyruk=0, n_normal=0, n=n, yeterli=False)
        if n >= 20:
            qx, qy = np.quantile(x, kuyruk), np.quantile(y, kuyruk)
            t = x <= qx
            satir["n_kuyruk"], satir["n_normal"] = int(t.sum()), int((~t).sum())
            if t.sum() >= 3:
                satir["kor_kuyruk"] = _kor(x[t], y[t], yontem)
                satir["ortak_dusus"] = float((y[t] <= qy).mean())
            satir["kor_normal"] = _kor(x[~t], y[~t], yontem)
            satir["yeterli"] = bool(t.sum() >= min_kuyruk)
        sat[kod] = satir
    cols = ["kor_kuyruk", "kor_normal", "ortak_dusus", "beklenen", "n_kuyruk", "n_normal", "n", "yeterli"]
    return pd.DataFrame(sat).T[cols].astype({"n_kuyruk": int, "n_normal": int, "n": int, "yeterli": bool})
