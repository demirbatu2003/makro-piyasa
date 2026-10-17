"""Benzer Günler testleri (sentetik veri)."""
import numpy as np
import pandas as pd
import pytest

from analiz import benzer

N = 2600


def _panel(seed=1, n=N, rejim_etkisi=True):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2012-01-02", periods=n)
    # kalıcı rejim: VIX log-düzeyi AR(1)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = 0.98 * x[i - 1] + 0.15 * rng.standard_normal()
    vix = 18 * np.exp(0.3 * x)
    esik = np.log(vix / 18) / 0.3 > 0.5
    r = 0.0003 * rng.standard_normal(n) * 0 + 0.008 * rng.standard_normal(n)
    if rejim_etkisi:
        # VIX durumu yüksekken (dünün durumu) günlük getiri +0.4%
        r = r + 0.004 * np.r_[False, esik[:-1]]
    spx = 1000 * np.exp(np.cumsum(r))

    def yuru(s, sig=0.01):
        return s * np.exp(np.cumsum(sig * rng.standard_normal(n)))

    p = pd.DataFrame({
        "VIX": vix, "DXY": yuru(np.full(n, 100.)), "BRENT": yuru(np.full(n, 60.)), "US10Y": 2 + np.cumsum(0.01 * rng.standard_normal(n)),
        "US2Y": 1 + np.cumsum(0.01 * rng.standard_normal(n)), "SPX": spx, "USDTRY": yuru(np.full(n, 5.)),
        "BIST100": yuru(np.full(n, 1e5)), "GRAMALTIN": yuru(np.full(n, 200.)), "XAUUSD": yuru(np.full(n, 1500.)),
        "NASDAQ": yuru(np.full(n, 5000.)), "BTC": yuru(np.full(n, 8000.)),
    }, index=idx)
    p["BTC"] = p["BTC"].where(p.index >= idx[1500])  # BTC geç başlıyor
    return p, esik


def _kat():
    return pd.DataFrame([dict(kod="BIST100", usd_kur_kodu="USDTRY", usd_kur_ters=False, birim="fiyat")])


def _hazir(p):
    oz = benzer.ozellik_tablosu(p)
    z = benzer.zskor(oz)
    sev = benzer.hedef_seviyeleri(p, _kat())
    return oz, z, sev


def test_ileriye_bakma_yok():
    p, _ = _panel()
    oz, z, _ = _hazir(p)
    t = 2000
    tarih = oz.index[t]
    p2 = p.copy()
    gel = p2.index > tarih
    p2.loc[gel, :] = p2.loc[gel, :] * 7.0 + 3.0  # gelecek verisini boz
    oz2 = benzer.ozellik_tablosu(p2)
    z2 = benzer.zskor(oz2)
    pd.testing.assert_frame_equal(oz.iloc[: t + 1], oz2.iloc[: t + 1])
    pd.testing.assert_frame_equal(z.iloc[: t + 1], z2.iloc[: t + 1])


def test_aralik_ve_aday_kesimi():
    p, _ = _panel()
    _, z, _ = _hazir(p)
    t, H, K = 2500, 20, 25
    an = benzer.analog_bul(z, t, H, K)
    poz = np.sort(an["poz"].to_numpy())
    assert len(poz) == K
    assert (np.diff(poz) > benzer.ARALIK).all()          # ±20 gün içinde başka analog yok
    assert poz.max() <= t - (H + 5)                        # aday kesimi
    assert (np.diff(an["uzaklik"].to_numpy()) >= -1e-12).all()


def test_ozellik_tasima_siniri():
    p, _ = _panel()
    p.loc[p.index[1200:1215], "VIX"] = np.nan  # 15 iş günü (21 takvim günü) boşluk
    oz = benzer.ozellik_tablosu(p)
    assert oz["vix"].iloc[1201] == pytest.approx(p["VIX"].iloc[1199])  # 5 takvim günü içinde taşındı
    assert np.isnan(oz["vix"].iloc[1210])                               # eski -> NaN


def test_ekilmis_rejim_etkisi_bulunur():
    p, esik = _panel(seed=3)
    oz, z, sev = _hazir(p)
    ileri = benzer.ileri_getiriler(sev, 20)
    # VIX yüksek rejimde olan ve tamamen öngörülebilir bir t seç
    adaylar = [t for t in range(2000, 2550) if esik[t] and esik[t - 30:t + 1].all() and np.isfinite(z["vix"].iloc[t])]
    assert adaylar
    t = adaylar[0]
    an, tab = benzer.analiz(z, ileri, t, 20, 25, kolonlar=["vix"])
    satir = tab.set_index("hedef").loc["SPX"]
    assert satir["medyan_a"] > satir["medyan_t"]
    assert satir["fark"] > 0.01
    assert satir["yukari_a"] > satir["yukari_t"]


def test_btc_n_yalniz_veri_olan_tarihler():
    p, _ = _panel()
    oz, z, sev = _hazir(p)
    ileri = benzer.ileri_getiriler(sev, 20)
    t = 2500
    an, tab = benzer.analiz(z, ileri, t, 20, 25)
    satir = tab.set_index("hedef").loc["BTC"]
    btc_var = np.isfinite(ileri["BTC"].to_numpy()[an["poz"].to_numpy()])
    assert satir["n_a"] == btc_var.sum()
    assert satir["n_a"] < len(an)  # bazı analoglar BTC verisinden önce
    assert (an["poz"].to_numpy()[btc_var] >= 1500).all()
    ad = benzer.aday_pozisyonlari(z, t, 20)
    assert satir["n_t"] == np.isfinite(ileri["BTC"].to_numpy()[ad]).sum()


def test_walk_forward_ve_yorum():
    p, _ = _panel(seed=5)
    oz, z, sev = _hazir(p)
    ileri = benzer.ileri_getiriler(sev, 20)
    wf = benzer.walk_forward(z, ileri, baslangic="2018-01-01", kolonlar=["vix"])
    assert len(wf) > 100
    # walk-forward satırlarında analog yalnız geçmiş: gerçekleşen getiri t+20'dedir, analog medyan bundan bağımsız hesaplanır
    ozet = benzer.walk_forward_ozet(wf)
    assert "SPX" in set(ozet["hedef"])
    assert isinstance(benzer.walk_forward_yorum(ozet), str)
    spx = ozet.set_index("hedef").loc["SPX"]
    assert spx["spearman"] > 0  # ekilmiş etki walk-forward'da da görünür
