"""Analiz kütüphanesi testleri (sentetik veri)."""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from analiz import ag, getiriler, korelasyon, leadlag, olay, rejim, saglik_yardimci
from analiz.istatistik import bh_fdr


# ---------------- getiriler ----------------
def test_log_getiri_ve_bp_ayrimi(katalog):
    idx = pd.bdate_range("2024-01-01", periods=5)
    panel = pd.DataFrame({"SPX": [100, 110, 121, 121, 133.1], "DGS10": [4.00, 4.10, 4.05, 4.05, 4.25]}, index=idx)
    g = getiriler.getiri_hesapla(panel, katalog)
    assert np.isclose(g["SPX"].iloc[0], np.log(1.1))      # fiyat -> log-getiri
    assert np.isclose(g["DGS10"].iloc[0], 10.0)            # faiz -> bp (0.10 * 100)
    assert np.isclose(g["DGS10"].iloc[1], -5.0)


def test_tatil_boslugu_ileri_doldurma_yok(katalog):
    idx = pd.bdate_range("2024-01-01", periods=6)
    s = pd.Series([100.0, 101, np.nan, 103, 104, 105], index=idx)
    g = getiriler.getiri_hesapla(pd.DataFrame({"SPX": s}), katalog)
    assert np.isnan(g["SPX"].reindex(idx).loc[idx[2]])                              # tatil günü getirisi yok
    assert np.isclose(g["SPX"].loc[idx[3]], np.log(103 / 101))         # sonraki gün çok günlü getiri


def test_usd_cevirisi(katalog):
    idx = pd.bdate_range("2024-01-01", periods=4)
    panel = pd.DataFrame({
        "BIST": [8000.0, 8200, 8400, 8600], "USDTRY": [30.0, 30.0, 32.0, 32.0],
        "DAX": [16000.0, 16100, 16200, 16300], "EURUSD": [1.10, 1.10, 1.20, 1.20],
        "SPX": [4000.0, 4010, 4020, 4030]}, index=idx)
    u = getiriler.usd_cevir(panel, katalog)
    assert np.allclose(u["BIST"], panel["BIST"] / panel["USDTRY"])     # yerel/kur
    assert np.allclose(u["DAX"], panel["DAX"] * panel["EURUSD"])       # ters kotasyon: x kur
    assert np.allclose(u["SPX"], panel["SPX"])                         # kursuz seri aynen
    # USD log-getirisi = yerel getiri - kur getirisi
    g_loc = np.log(panel["BIST"]).diff()
    g_fx = np.log(panel["USDTRY"]).diff()
    g_usd = np.log(u["BIST"]).diff()
    assert np.allclose(g_usd.dropna(), (g_loc - g_fx).dropna())


def test_usd_nan_kur_gunu(katalog):
    idx = pd.bdate_range("2024-01-01", periods=3)
    panel = pd.DataFrame({"BIST": [1.0, 2, 3], "USDTRY": [10.0, np.nan, 10]}, index=idx)
    u = getiriler.usd_cevir(panel, katalog, ["BIST"])
    assert np.isnan(u["BIST"].iloc[1])


def test_haftalik_ortusmeyen(katalog):
    idx = pd.bdate_range("2024-01-01", periods=20)
    panel = pd.DataFrame({"SPX": np.exp(np.arange(20) * 0.01)}, index=idx)
    w = getiriler.haftalik_getiriler(panel, katalog)
    assert np.allclose(w["SPX"], 0.05)  # 5 iş günü x 0.01


# ---------------- korelasyon ----------------
def test_korelasyon_beklenen_degerler(getiri):
    for yontem, beklenen_ab in (("pearson", 0.8), ("spearman", 0.79)):
        c, n = korelasyon.korelasyon_matrisi(getiri[["A", "B", "C"]], yontem=yontem)
        assert abs(c.loc["A", "B"] - beklenen_ab) < 0.05
        assert abs(c.loc["A", "C"]) < 0.08
        assert n.loc["A", "B"] == len(getiri)


def test_pairwise_complete_scipy_ile_ayni(getiri):
    g = getiri[["A", "B", "C"]].copy()
    g.loc[g.index[100:400], "B"] = np.nan
    g.loc[g.index[300:500], "C"] = np.nan
    c, n = korelasyon.korelasyon_matrisi(g, yontem="spearman")
    ok = g["B"].notna() & g["C"].notna()
    assert n.loc["B", "C"] == ok.sum()
    assert np.isclose(c.loc["B", "C"], spearmanr(g["B"][ok], g["C"][ok])[0])
    ok = g["A"].notna() & g["B"].notna()
    cp, _ = korelasyon.korelasyon_matrisi(g, yontem="pearson")
    assert np.isclose(cp.loc["A", "B"], np.corrcoef(g["A"][ok], g["B"][ok])[0, 1])


def test_minimum_gozlem_kurali(getiri):
    g = getiri[["A", "B"]].copy()
    son60 = g.index[-60:]
    g.loc[son60[:25], "B"] = np.nan          # 60g pencerede ortak gözlem = 35 < 40
    c, n = korelasyon.korelasyon_matrisi(g, pencere=60)
    assert n.loc["A", "B"] == 35 and np.isnan(c.loc["A", "B"])
    g2 = getiri[["A", "B"]].copy()
    g2.loc[son60[:15], "B"] = np.nan         # 45 >= 40
    c2, n2 = korelasyon.korelasyon_matrisi(g2, pencere=60)
    assert n2.loc["A", "B"] == 45 and np.isfinite(c2.loc["A", "B"])
    assert korelasyon.min_gozlem_varsayilan(250) == 150
    c3, _ = korelasyon.korelasyon_matrisi(g.iloc[:-1], pencere=250)  # 250g: 150 kuralı
    assert np.isfinite(c3.loc["A", "B"])


def test_iki_nokta_ve_fark(getiri):
    g = getiri[["A", "B", "C"]].copy()
    # Son 60 günde B'yi A'dan bağımsız yap -> fark negatif olmalı
    rng = np.random.default_rng(1)
    g.loc[g.index[-60:], "B"] = rng.standard_normal(60) * 0.01
    r = korelasyon.iki_nokta_karsilastirma(g, pencere=60, geri=250)
    assert r["fark"].loc["A", "B"] < -0.4
    assert r["onceki"].loc["A", "B"] > 0.5
    assert r["fark_p"].loc["A", "B"] < 0.01


def test_ikili_rolling(getiri):
    out = korelasyon.ikili_rolling(getiri, "A", "B", pencere=250, yontem="pearson")
    assert abs(out["korelasyon"].dropna().mean() - 0.8) < 0.05
    assert (out["alt"].dropna() < out["korelasyon"].dropna()).all()
    assert out["korelasyon"].iloc[:149].isna().all()           # pencere dolmadan değer yok
    out_s = korelasyon.ikili_rolling(getiri.iloc[:400], "A", "B", pencere=60, yontem="spearman")
    assert abs(out_s["korelasyon"].dropna().mean() - 0.79) < 0.06


def test_fdr_ve_anlamlilik(getiri):
    # BH bilinen örnek
    p = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])
    q, an = bh_fdr(p, 0.05)
    assert an.tolist() == [True, True, False, False, False, False, False, False, False, False]
    assert np.all(np.diff(q) >= -1e-12)
    c, n = korelasyon.korelasyon_matrisi(getiri[["A", "B", "C", "D"]], yontem="pearson")
    tab = korelasyon.anlamlilik_tablosu(c, n)
    assert len(tab) == 6
    ab = tab[(tab.a == "A") & (tab.b == "B")].iloc[0]
    ac = tab[(tab.a == "A") & (tab.b == "C")].iloc[0]
    assert ab.fdr_anlamli and ab.p < 1e-10
    assert ac.p > 0.01


def test_ortalama_ikili(getiri):
    c, _ = korelasyon.korelasyon_matrisi(getiri[["A", "B", "C"]], yontem="pearson")
    assert 0.2 < korelasyon.ortalama_ikili_korelasyon(c) < 0.4   # (0.8+0+0)/3 civarı


# ---------------- ag ----------------
def test_mst_n_eksi_1_kenar(getiri):
    cols = ["A", "B", "C", "D", "T", "R"]
    c, _ = korelasyon.korelasyon_matrisi(getiri[cols], yontem="spearman")
    kenar, dug, elenen = ag.mst_kenarlari(c, {"A": "borsa"})
    assert len(kenar) == len(cols) - 1 and not elenen
    assert {"A", "B"} == set(kenar.iloc[np.argmin(kenar["uzaklik"])][["a", "b"]])  # en yakın çift
    assert set(dug["kod"]) == set(cols) and dug[["x", "y"]].notna().all().all()
    xs, ys = ag.kenar_listesi_ciz(kenar, dug)
    assert len(xs) == 3 * len(kenar)


def test_mst_nan_seri_elenir(getiri):
    g = getiri[["A", "B", "C", "D"]].copy()
    g["C"] = np.nan
    c, _ = korelasyon.korelasyon_matrisi(g, yontem="spearman")
    kenar, dug, elenen = ag.mst_kenarlari(c)
    assert elenen == ["C"] and len(kenar) == 2


def test_kumeleme_ve_kararlilik(getiri):
    c, _ = korelasyon.korelasyon_matrisi(getiri[["A", "B", "C", "D"]], yontem="spearman")
    h = ag.hiyerarsik_kumeleme(c)
    assert sorted(h["sira"]) == ["A", "B", "C", "D"]
    pos = {k: i for i, k in enumerate(h["sira"])}
    assert abs(pos["A"] - pos["B"]) == 1 or abs(pos["A"] - pos["D"]) == 1
    lab = ag.kume_etiketleri(h, 2)
    assert lab.nunique() == 2
    kk = ag.kenar_kararliligi(getiri[["A", "B", "C", "D"]], pencere=250, adim=250)
    assert kk.loc[(kk.a == "A") & (kk.b == "B"), "oran"].iloc[0] == 1.0
    d = ag.mst_degisim(pd.DataFrame({"a": ["A"], "b": ["B"]}), pd.DataFrame({"a": ["B", "C"], "b": ["A", "D"]}))
    assert set(d["durum"]) == {"ortak", "sadece_2"}


# ---------------- rejim ----------------
def test_vix_rejimi_ve_kosullu_korelasyon():
    rng = np.random.default_rng(3)
    n = 900
    idx = pd.bdate_range("2020-01-01", periods=n)
    vix = pd.Series(np.r_[np.full(300, 12.0), np.full(300, 20.0), np.full(300, 30.0)], index=idx)
    rj = rejim.vix_rejimi(vix)
    assert (rj.iloc[:300] == "sakin").all() and (rj.iloc[300:600] == "normal").all()
    assert (rj.iloc[600:] == "gergin").all()
    assert (rejim.vix_rejimi(pd.Series([15.0, 25.0, np.nan])).astype(object).iloc[:2] == "normal").all()
    x = rng.standard_normal(n)
    y = np.where(np.arange(n) >= 600, 0.9 * x + np.sqrt(1 - 0.81) * rng.standard_normal(n), rng.standard_normal(n))
    g = pd.DataFrame({"X": x, "Y": y}, index=idx)
    sonuc, ozet = rejim.rejim_korelasyonlari(g, rj, yontem="pearson")
    assert sonuc["gergin"][0].loc["X", "Y"] > 0.85
    assert abs(sonuc["sakin"][0].loc["X", "Y"]) < 0.2
    assert ozet.set_index("rejim").loc["gergin", "gun_sayisi"] == 300
    # yetersiz rejim -> NaN
    _, ozet2 = rejim.rejim_korelasyonlari(g.iloc[:330], rj.iloc[:330])
    assert not ozet2.set_index("rejim").loc["normal", "yeterli"]


def test_beta_tablosu():
    rng = np.random.default_rng(5)
    idx = pd.bdate_range("2020-01-01", periods=1000)
    x = rng.standard_normal(1000) * 0.01
    g = pd.DataFrame({"SPX": x, "Y2": 2.0 * x + 0.002 * rng.standard_normal(1000),
                      "Z": rng.standard_normal(1000) * 0.01}, index=idx)
    b = rejim.beta_tablosu(g, "SPX")
    assert abs(b.loc["Y2", "beta"] - 2.0) < 0.05 and b.loc["Y2", "n"] == 1000
    assert abs(b.loc["Z", "beta"]) < 0.15 and "SPX" not in b.index
    b60 = rejim.beta_tablosu(g, "SPX", pencere=60)
    assert b60.loc["Y2", "n"] == 60


# ---------------- olay ----------------
def test_event_study_ekilmis_tepki(getiri):
    olaylar, ozet = olay.olay_tepkileri(getiri[["T", "R", "C"]], "T", k=2.0, ufuklar=(0, 1, 5, 20))
    assert (olaylar["z"].abs() > 2).all()
    # ex-ante sigma: ilk 40 gözlemde olay olamaz
    assert olaylar.index.min() >= getiri.index[40]
    # çakışan olayları ayıklama: ardışık olaylar > 5 satır arayla
    pos = getiri.index.get_indexer(olaylar.index)
    assert (np.diff(pos) > 5).all()
    up = ozet[(ozet.yon == "yukari") & (ozet.hedef == "R")].set_index("ufuk")
    dn = ozet[(ozet.yon == "asagi") & (ozet.hedef == "R")].set_index("ufuk")
    assert abs(up.loc[0, "ortalama"]) < 0.005                         # t+0'da tepki yok
    assert up.loc[1, "ortalama"] > 0.012 and up.loc[1, "ci_alt"] > 0   # t+1'de ekilmiş tepki
    assert dn.loc[1, "ortalama"] < -0.012 and dn.loc[1, "ci_ust"] < 0
    assert up.loc[1, "ayni_yon_orani"] > 0.9
    # ilişkisiz seri: CI sıfırı içermeli
    c = ozet[(ozet.yon == "yukari") & (ozet.hedef == "C") & (ozet.ufuk == 1)].iloc[0]
    assert c.ci_alt < 0 < c.ci_ust
    assert up.loc[1, "n"] == (olaylar.yon == "yukari").sum()


def test_event_yon_ve_yetersiz(getiri):
    ol, oz = olay.olay_tepkileri(getiri[["T", "R"]], "T", yon="yukari", min_olay=10**6)
    assert set(oz["yon"]) == {"yukari"} and oz["yetersiz"].all()
    # sigma gelecekten etkilenmez: son gün devasa şok, önceki olaylar değişmez
    t = getiri["T"].copy()
    ol0 = olay.olaylari_bul(t)
    t2 = t.copy()
    t2.iloc[-1] = 1.0
    ol1 = olay.olaylari_bul(t2)
    assert ol1.index[:-1].equals(ol0.index) or ol1.index[-1] == t.index[-1]
    assert ol0.index.isin(ol1.index).all()


def test_event_tatil_nan_sifir_sayilir():
    idx = pd.bdate_range("2021-01-01", periods=200)
    rng = np.random.default_rng(0)
    t = pd.Series(0.01 * np.where(np.arange(200) % 2 == 0, 1.0, -1.0), index=idx)
    t.iloc[100] = 0.2
    hedef = pd.Series(0.0, index=idx)
    hedef.iloc[101] = 0.01
    hedef.iloc[102] = np.nan   # tatil
    hedef.iloc[103] = 0.02
    _, oz = olay.olay_tepkileri(pd.DataFrame({"T": t, "H": hedef}), "T", ufuklar=(5,), min_olay=1)
    r = oz[(oz.yon == "yukari") & (oz.hedef == "H")].iloc[0]
    assert np.isclose(r.ortalama, 0.03) and r.n == 1


# ---------------- leadlag ----------------
def test_leadlag_ekilmis_lag(getiri, katalog):
    tab = leadlag.capraz_korelasyon(getiri, "A", "D", gecikmeler=(-1, 0, 1), yontem="pearson")
    t = tab.set_index("gecikme")
    assert abs(t.loc[1, "r"] - 0.707) < 0.05 and t.loc[1, "anlamli"]   # A(t-1) -> D(t): 0.7/sqrt(0.98)=0.707*0.707
    assert abs(t.loc[0, "r"]) < 0.1 and abs(t.loc[-1, "r"]) < 0.1
    assert t["r"].idxmax() == 1 and t.loc[1, "r"] > 0
    # ters çift: D'nin A'yı önden gittiği bir ilişki yok, k=-1 güçlü olmalı (A, D'yi önden gider)
    ters = leadlag.capraz_korelasyon(getiri, "D", "A", gecikmeler=(-1, 0, 1), yontem="pearson").set_index("gecikme")
    assert ters["r"].idxmax() == -1
    # negatif işaret: işareti ters çevrilmiş lead negatif r vermeli
    neg = getiri.assign(D=-getiri["D"])
    assert leadlag.capraz_korelasyon(neg, "A", "D", yontem="pearson").set_index("gecikme").loc[1, "r"] < -0.4


def test_leadlag_uyari_kapanis_notu(getiri, katalog):
    g = getiri.rename(columns={"A": "SPX", "B": "BIST"})
    tab = leadlag.capraz_korelasyon(g, "SPX", "BIST", katalog=katalog)
    assert tab["uyari"].str.contains("ABD 21:00 UTC").all() and tab["uyari"].str.contains("TR 15:00 UTC").all()
    assert {"gecikme", "r", "n", "p", "alt", "ust", "uyari"} <= set(tab.columns)


# ---------------- saglik ----------------
def test_saglik(katalog):
    idx = pd.bdate_range("2024-01-01", periods=30)
    s1 = pd.Series(1.0, index=idx)
    s2 = s1.copy()
    s2.iloc[10:13] = np.nan
    s3 = s1.copy()
    s3.iloc[-10:] = np.nan
    h = saglik_yardimci.seri_sagligi(pd.DataFrame({"SPX": s1, "BIST": s2, "DAX": s3}), katalog).set_index("kod")
    assert h.loc["SPX", "durum"] == "taze" and h.loc["SPX", "eksik_is_gunu"] == 0
    assert h.loc["BIST", "eksik_is_gunu"] == 3 and h.loc["BIST", "en_uzun_bosluk_gun"] == 6
    assert h.loc["DAX", "durum"] == "bayat"


def test_hafta_sonu_seviyede_atilir_toplam_korunur(katalog):
    idx = pd.date_range("2024-01-01", periods=28, freq="D")  # 7 gün takvim, Pzt başlangıç
    rng = np.random.default_rng(9)
    p = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.02, 28))), index=idx)
    g = getiriler.getiri_hesapla(pd.DataFrame({"SPX": p}), katalog)["SPX"]
    assert (g.index.dayofweek < 5).all()
    pzt = idx[7]
    assert np.isclose(g.loc[pzt], np.log(p[pzt] / p[idx[4]]))   # ln(Pzt/Cum)
    haftaici = p[p.index.dayofweek < 5]
    assert np.isclose(g.sum(), np.log(haftaici.iloc[-1] / haftaici.iloc[0]))
