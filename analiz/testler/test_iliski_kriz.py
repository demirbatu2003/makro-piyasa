"""Kismi korelasyon, aralik ozeti, rolling beta ve kriz ani iliskisi testleri (sentetik veri)."""
import numpy as np
import pandas as pd

from analiz import iliski, kriz

N = 2000


def _idx():
    return pd.bdate_range("2015-01-01", periods=N)


def test_kismi_ortak_faktor_sifira_yakin():
    rng = np.random.default_rng(1)
    f = rng.standard_normal(N)
    g = pd.DataFrame({"A": f + 0.5 * rng.standard_normal(N), "B": f + 0.5 * rng.standard_normal(N), "F": f}, index=_idx())
    for yontem in ("pearson", "spearman"):
        d = iliski.kismi_korelasyon(g, "A", "B", ["F"], yontem=yontem)
        assert d["ham"] > 0.7 and abs(d["r"]) < 0.1 and d["n"] == N, (yontem, d)
        assert d["alt"] < d["r"] < d["ust"]


def test_kismi_kontrolsuz_ham_ve_nan_toleransi():
    rng = np.random.default_rng(2)
    g = pd.DataFrame(rng.standard_normal((N, 3)), columns=list("ABF"), index=_idx())
    g.iloc[:100, 2] = np.nan
    d = iliski.kismi_korelasyon(g, "A", "B", ["F"])
    assert d["n"] == N - 100
    d0 = iliski.kismi_korelasyon(g, "A", "B", [])
    assert d0["r"] == d0["ham"]
    assert np.isnan(iliski.kismi_korelasyon(g.iloc[:20], "A", "B", ["F"])["r"])  # n kucuk


def test_kismi_matris_ortak_faktor():
    rng = np.random.default_rng(3)
    f = rng.standard_normal(N)
    g = pd.DataFrame({"A": f + rng.standard_normal(N), "B": f + rng.standard_normal(N),
                      "C": rng.standard_normal(N), "F": f}, index=_idx())
    c, n = iliski.kismi_korelasyon_matrisi(g, "F")
    assert list(c.columns) == ["A", "B", "C"]
    assert abs(c.loc["A", "B"]) < 0.1 and c.loc["A", "B"] == c.loc["B", "A"] and c.loc["A", "A"] == 1.0
    assert n.loc["A", "B"] == N


def test_aralik_ozeti():
    rng = np.random.default_rng(4)
    x = rng.standard_normal(N)
    g = pd.DataFrame({"X": x, "Y": 1.5 * x + rng.standard_normal(N)}, index=_idx())
    d = iliski.aralik_ozeti(g, "X", "Y")
    assert d["n"] == N and abs(d["beta"] - 1.5) < 0.1 and d["beta_alt"] < 1.5 < d["beta_ust"]
    assert d["sp_alt"] < d["spearman"] < d["sp_ust"] and d["pe_alt"] < d["pearson"] < d["pe_ust"]
    dk = iliski.aralik_ozeti(g, "X", "Y", bas=g.index[-100], bit=g.index[-1])
    assert dk["n"] == 100
    assert np.isnan(iliski.aralik_ozeti(g, "X", "Y", bas=g.index[-2])["pearson"])


def test_rolling_beta_bilinen_beta():
    rng = np.random.default_rng(5)
    x = rng.standard_normal(N)
    y = 0.8 * x + 0.5 * rng.standard_normal(N)
    g = pd.DataFrame({"X": x, "Y": y}, index=_idx())
    rb = iliski.rolling_beta(g, "X", "Y", pencere=120)
    ok = rb.dropna()
    assert abs(ok["beta"].mean() - 0.8) < 0.03
    kapsam = ((ok["alt"] <= 0.8) & (0.8 <= ok["ust"])).mean()
    assert kapsam > 0.85, kapsam
    # tam pencere OLS ile tutarli
    son = g.iloc[-120:]
    b, se, _ = iliski._ols_beta(son["X"].to_numpy(), son["Y"].to_numpy())
    assert abs(rb["beta"].iloc[-1] - b) < 1e-8 and abs(rb["se"].iloc[-1] - se) < 1e-8
    assert rb["beta"].iloc[:50].isna().all()


def test_rolling_beta_rejim_degisimi_ve_nan():
    rng = np.random.default_rng(6)
    x = rng.standard_normal(N)
    beta = np.where(np.arange(N) < N // 2, 0.5, 1.5)
    g = pd.DataFrame({"X": x, "Y": beta * x + 0.3 * rng.standard_normal(N)}, index=_idx())
    g.iloc[300:310, 1] = np.nan
    rb = iliski.rolling_beta(g, "X", "Y", pencere=60)
    assert abs(rb["beta"].iloc[N // 2 - 5] - 0.5) < 0.2 and abs(rb["beta"].iloc[-1] - 1.5) < 0.2
    assert rb["n"].iloc[320] <= 60


def test_kuyruk_ekilmis_bagimlilik():
    rng = np.random.default_rng(7)
    x = rng.standard_normal(N)
    y = rng.standard_normal(N)
    t = x <= np.quantile(x, 0.10)
    y[t] = 0.9 * x[t] + 0.3 * rng.standard_normal(t.sum())   # yalniz kuyrukta bagimlilik
    g = pd.DataFrame({"R": x, "Y": y, "Z": rng.standard_normal(N)}, index=_idx())
    k = kriz.kuyruk_iliskisi(g, "R", kuyruk=0.10)
    assert k.loc["Y", "kor_kuyruk"] > 0.6 and abs(k.loc["Y", "kor_normal"]) < 0.1
    assert k.loc["Y", "ortak_dusus"] > 0.4          # beklenen 0,10
    assert abs(k.loc["Z", "ortak_dusus"] - 0.10) < 0.07   # bagimsiz: ~%10
    assert k.loc["Y", "n_kuyruk"] == t.sum() and k.loc["Y", "n_kuyruk"] + k.loc["Y", "n_normal"] == N
    assert bool(k.loc["Y", "yeterli"]) and "R" not in k.index


def test_kuyruk_kucuk_n_yetersiz():
    rng = np.random.default_rng(8)
    g = pd.DataFrame(rng.standard_normal((120, 2)), columns=["R", "Y"], index=pd.bdate_range("2020-01-01", periods=120))
    k = kriz.kuyruk_iliskisi(g, "R", kuyruk=0.10, min_kuyruk=30)
    assert not k.loc["Y", "yeterli"] and k.loc["Y", "n_kuyruk"] == 12
