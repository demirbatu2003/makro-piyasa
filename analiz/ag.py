"""Ağ ve kümeler: Spearman uzaklığı, minimum spanning tree, hiyerarşik kümeleme."""
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import squareform

from .korelasyon import korelasyon_matrisi


def uzaklik_matrisi(corr):
    """d = sqrt(2 (1 - rho)); köşegen 0, simetrik."""
    d = np.sqrt(2.0 * (1.0 - corr.clip(-1, 1)))
    a = d.to_numpy(float).copy()
    a = (a + a.T) / 2
    np.fill_diagonal(a, 0.0)
    return pd.DataFrame(a, index=corr.index, columns=corr.columns)


def tam_matris_sec(corr):
    """NaN içeren seriler (yetersiz ortak gözlem) iteratif olarak elenir. Döner: (corr, elenenler)."""
    c = corr.copy()
    elenen = []
    while c.isna().to_numpy().sum() - 0 > 0:
        eksik = c.isna().sum()
        en = eksik.idxmax()
        if eksik[en] == 0:
            break
        elenen.append(en)
        c = c.drop(index=en, columns=en)
    return c, elenen


def mst_kenarlari(corr, kategori=None):
    """Spearman (veya verilen) korelasyon matrisinden MST.
    Döner: (kenarlar, dugumler, elenenler).
    kenarlar: a, b, rho, uzaklik  (n-1 satır). dugumler: kod, kategori, derece, x, y (Plotly yerleşimi).
    kategori: {kod: kategori} sözlüğü veya Series (opsiyonel)."""
    c, elenen = tam_matris_sec(corr)
    kodlar = list(c.columns)
    n = len(kodlar)
    if n < 2:
        return (pd.DataFrame(columns=["a", "b", "rho", "uzaklik"]),
                pd.DataFrame({"kod": kodlar, "kategori": None, "derece": 0, "x": 0.0, "y": 0.0}), elenen)
    d = uzaklik_matrisi(c).to_numpy()
    d = np.where(d == 0, 1e-12, d)  # scipy sıfırı 'kenar yok' sayar
    np.fill_diagonal(d, 0.0)
    mst = minimum_spanning_tree(d).tocoo()
    kenar = pd.DataFrame({"a": [kodlar[i] for i in mst.row], "b": [kodlar[j] for j in mst.col],
                          "uzaklik": mst.data})
    kenar["rho"] = [c.iloc[i, j] for i, j in zip(mst.row, mst.col)]
    kenar = kenar[["a", "b", "rho", "uzaklik"]].reset_index(drop=True)
    derece = pd.concat([kenar["a"], kenar["b"]]).value_counts()
    xy = _yerlesim(kodlar, mst.row, mst.col, mst.data)
    kat = pd.Series(kategori) if kategori is not None else pd.Series(dtype=object)
    dug = pd.DataFrame({"kod": kodlar,
                        "kategori": [kat.get(k, None) for k in kodlar],
                        "derece": [int(derece.get(k, 0)) for k in kodlar],
                        "x": xy[:, 0], "y": xy[:, 1]})
    return kenar, dug, elenen


def _yerlesim(kodlar, satir, sutun, uzak, iterasyon=300, tohum=0):
    """Basit Fruchterman-Reingold (sabit tohum, tekrarlanabilir). Kenar ağırlığı ~ 1/uzaklik."""
    n = len(kodlar)
    rng = np.random.default_rng(tohum)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = np.c_[np.cos(ang), np.sin(ang)] + 0.01 * rng.standard_normal((n, 2))
    k = 1.0 / np.sqrt(n)
    t = 0.1
    w = 1.0 / np.maximum(np.asarray(uzak, float), 0.05)
    w = w / w.max()
    for _ in range(iterasyon):
        delta = pos[:, None, :] - pos[None, :, :]
        mesafe = np.linalg.norm(delta, axis=2) + 1e-9
        kuvvet = (k * k / mesafe**2)[:, :, None] * delta
        disp = kuvvet.sum(axis=1)
        for i, j, ww in zip(satir, sutun, w):
            dv = pos[i] - pos[j]
            m = np.linalg.norm(dv) + 1e-9
            f = (m / k) * dv * ww
            disp[i] -= f
            disp[j] += f
        l = np.linalg.norm(disp, axis=1)[:, None] + 1e-9
        pos += disp / l * np.minimum(l, t)
        t = max(t * 0.98, 1e-3)
    return pos


def kenar_listesi_ciz(kenar, dugumler):
    """Plotly Scatter için kenar koordinatları: (x_liste, y_liste) None ile ayrılmış segmentler."""
    p = dugumler.set_index("kod")
    xs, ys = [], []
    for a, b in zip(kenar["a"], kenar["b"]):
        xs += [p.loc[a, "x"], p.loc[b, "x"], None]
        ys += [p.loc[a, "y"], p.loc[b, "y"], None]
    return xs, ys


def mst_degisim(kenar1, kenar2):
    """İki zaman noktasındaki MST kenarlarını karşılaştırır: durum = ortak | sadece_1 | sadece_2."""
    k1 = {frozenset((a, b)) for a, b in zip(kenar1["a"], kenar1["b"])}
    k2 = {frozenset((a, b)) for a, b in zip(kenar2["a"], kenar2["b"])}
    satir = []
    for e in k1 | k2:
        a, b = sorted(e)
        durum = "ortak" if e in k1 and e in k2 else ("sadece_1" if e in k1 else "sadece_2")
        satir.append({"a": a, "b": b, "durum": durum})
    return pd.DataFrame(satir, columns=["a", "b", "durum"]).sort_values(["durum", "a", "b"]).reset_index(drop=True)


def kenar_kararliligi(getiri, pencere=250, adim=20, yontem="spearman", min_gozlem=None, en_fazla_pencere=None):
    """Kayan pencerelerde her MST kenarının görülme oranı (0-1). Döner: a, b, oran, pencere_sayisi."""
    sayac, toplam = {}, 0
    uc = list(range(len(getiri), pencere - 1, -adim))
    if en_fazla_pencere:
        uc = uc[:en_fazla_pencere]
    for e in uc:
        c, _ = korelasyon_matrisi(getiri.iloc[:e], pencere, None, yontem, min_gozlem)
        kenar, _, _ = mst_kenarlari(c)
        if kenar.empty:
            continue
        toplam += 1
        for a, b in zip(kenar["a"], kenar["b"]):
            key = tuple(sorted((a, b)))
            sayac[key] = sayac.get(key, 0) + 1
    satir = [{"a": a, "b": b, "oran": v / toplam, "pencere_sayisi": toplam} for (a, b), v in sayac.items()]
    return pd.DataFrame(satir, columns=["a", "b", "oran", "pencere_sayisi"]).sort_values(
        "oran", ascending=False).reset_index(drop=True)


def hiyerarsik_kumeleme(corr, yontem="average"):
    """Hiyerarşik kümeleme (uzaklık = sqrt(2(1-rho))). NaN'li seriler elenir.
    Döner dict: kodlar (elenenler çıkmış), Z (scipy linkage), sira (dendrogram yaprak sırası, kodlar),
    elenenler."""
    c, elenen = tam_matris_sec(corr)
    kodlar = list(c.columns)
    if len(kodlar) < 2:
        return {"kodlar": kodlar, "Z": None, "sira": kodlar, "elenenler": elenen}
    d = squareform(uzaklik_matrisi(c).to_numpy(), checks=False)
    Z = linkage(d, method=yontem)
    sira = [kodlar[i] for i in leaves_list(Z)]
    return {"kodlar": kodlar, "Z": Z, "sira": sira, "elenenler": elenen}


def kume_etiketleri(sonuc, k):
    """hiyerarsik_kumeleme çıktısından k kümeye kes: Series (kod -> küme no)."""
    lab = fcluster(sonuc["Z"], k, criterion="maxclust")
    return pd.Series(lab, index=sonuc["kodlar"], name="kume")


def matrisi_sirala(m, sira):
    """Matrisi (satır ve sütun) verilen kod sırasına göre dizer; sirada olmayanlar atılır."""
    sira = [s for s in sira if s in m.index]
    return m.loc[sira, sira]
