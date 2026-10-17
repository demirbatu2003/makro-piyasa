"""beklenti.py ve makas.py modülleri için birim testleri (sentetik veri, ex-ante doğrulaması)."""
import numpy as np
import pandas as pd
import pytest

from analiz import beklenti, makas


def _sentetik_getiri(seed=42, n=900):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    t = 0.01 * rng.standard_normal(n)
    # T yukarı şok yaptığında (+2 sigma), sonraki 5 günde H1 güçlü pozitif getiri üretsin
    h1 = 0.008 * rng.standard_normal(n)
    h2 = 0.008 * rng.standard_normal(n)
    sok_gunleri = np.arange(100, n - 30, 25)
    for p in sok_gunleri:
        t[p] = 0.035  # ~3.5 sigma yukarı şok
        h1[p + 1: p + 6] += 0.012  # takip eden 5 günde toplam ~+6% ek getiri
        h2[p + 1: p + 6] -= 0.010  # takip eden 5 günde düşüş
    # Son 5 iş günü içinde canlı bir yukarı şok ekle
    t[-3] = 0.032

    us10y = 2.0 * rng.standard_normal(n)  # bp cinsinden faiz değişimi
    return pd.DataFrame({"T": t, "H1": h1, "H2": h2, "US10Y": us10y}, index=idx)


# =====================================================================
# A İŞİ TESTLERİ: analiz/beklenti.py
# =====================================================================
def test_son_soklar_ve_beklentiler_ekilmis_etki():
    g = _sentetik_getiri()
    soklar, bek = beklenti.son_soklar_ve_beklentiler(g, pencere_gun=10, k=1.8, ufuk=5)
    assert len(soklar) >= 1
    # En son eklenen canlı şok T varlığında yukarı yönlü olmalı
    t_sok = soklar[soklar["kod"] == "T"].iloc[0]
    assert t_sok["yon"] == "yukari" and t_sok["z"] >= 1.8

    # T yukarı şoku için beklenti tablosunu kontrol et
    bek_t = beklenti.sok_beklentisi(g, tetik="T", yon="yukari", k=1.8, ufuk=5)
    b = bek_t.set_index("hedef")
    assert "T" not in b.index
    assert b.loc["H1", "n"] >= 20
    assert b.loc["H1", "medyan"] > 3.0
    assert b.loc["H1", "yukari_orani"] > 80.0
    assert b.loc["H1", "olasilik_farki"] > 20.0
    assert b.loc["H2", "medyan"] < -2.0
    assert b.loc["H2", "olasilik_farki"] < -15.0
    assert b.loc["US10Y", "birim"] == "bp"

    # Bağımsız olaylar arası mesafe > 5 iş günü olmalı ve son ufuk (t + 5 >= len(g)) hariç tutulmalı
    olay_tar = bek_t.attrs["olay_tarihleri"]
    konum = g.index.get_indexer(olay_tar)
    assert (np.diff(konum) > 5).all()
    assert (konum + 5 < len(g)).all()  # t[-3]'teki tamamlanmamış canlı şok geçmiş örnekleme sızmaz


def test_beklenti_ileriye_bakis_sizintisi_yok():
    g = _sentetik_getiri()
    kesim = 600
    g_kesik = g.iloc[:kesim].copy()
    g_bozuk = g.copy()
    # kesim sonrası geleceği tamamen boz
    g_bozuk.iloc[kesim:] = g_bozuk.iloc[kesim:] * -50.0 + 0.5

    _, _, z1 = beklenti._ex_ante_z(g_kesik["T"])
    _, _, z2 = beklenti._ex_ante_z(g_bozuk["T"])
    pd.testing.assert_series_equal(z1, z2.iloc[:kesim])

    m1, v1 = beklenti._varlik_kosul_maskesi(g_kesik, "T", pencere=5, durum="sert_yukari")
    m2, v2 = beklenti._varlik_kosul_maskesi(g_bozuk, "T", pencere=5, durum="sert_yukari")
    pd.testing.assert_series_equal(m1, m2.iloc[:kesim])
    pd.testing.assert_series_equal(v1, v2.iloc[:kesim])


def test_kosullu_olasilik_tablosu_coklu_kosul_ve_vix():
    rng = np.random.default_rng(7)
    n = 1000
    idx = pd.bdate_range("2019-01-01", periods=n)
    x = 0.01 * rng.standard_normal(n)
    y = 0.01 * rng.standard_normal(n)
    hedef = 0.008 * rng.standard_normal(n)
    vix = pd.Series(18.0, index=idx)

    # Belirli dönemlerde: X son 5g sert düşüşte (<-1σ) VE VIX gergin (>25) iken hedef sonraki 5 günde yükselsin
    tetik_konumlar = np.arange(120, n - 40, 40)
    for p in tetik_konumlar:
        x[p - 4: p + 1] = -0.015
        vix.iloc[p] = 30.0
        hedef[p + 1: p + 6] += 0.015

    g = pd.DataFrame({"X": x, "Y": y, "HEDEF": hedef}, index=idx)
    tab = beklenti.kosullu_olasilik_tablosu(
        g,
        kosullar=[{"kod": "X", "pencere": 5, "durum": "sert_asagi", "k": 1.0}],
        vix_seviye=vix,
        vix_rejim="gergin",
        ufuk=5,
    )
    t_hedef = tab.set_index("hedef").loc["HEDEF"]
    assert t_hedef["n_kosullu"] >= 15
    assert t_hedef["yukari_olasiligi"] > t_hedef["kosulsuz_yukari"] + 20.0
    assert t_hedef["medyan_kosullu"] > t_hedef["medyan_kosulsuz"] + 3.0
    assert np.isclose(t_hedef["olasilik_farki"], t_hedef["yukari_olasiligi"] - t_hedef["kosulsuz_yukari"])
    assert np.isclose(t_hedef["medyan_fark"], t_hedef["medyan_kosullu"] - t_hedef["medyan_kosulsuz"])

    olay_tar = tab.attrs["olay_tarihleri"]
    konum = g.index.get_indexer(olay_tar)
    assert (np.diff(konum) > 5).all()
    assert (konum + 5 < n).all()


# =====================================================================
# B İŞİ TESTLERİ: analiz/makas.py
# =====================================================================
def _sentetik_makas_verisi(seed=11, n=900):
    """A ve B yüksek korelasyonlu iki varlık; aralarındaki makas ortalamaya dönen (mean-reverting)
    bir süreç izler. Son 20 günde ise A aşırı önde gidecek şekilde ayrışır."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    ortak_faktor = 0.012 * rng.standard_normal(n)
    rb = ortak_faktor + 0.002 * rng.standard_normal(n)

    # Ortalamaya dönen makas şokları: p gününde A ani ayrışır, sonraki 10 günde makas kapanır
    ek_makas = 0.0015 * rng.standard_normal(n)
    for p in range(300, n - 40, 35):
        yon = 1.0 if (p // 35) % 2 == 0 else -1.0
        ek_makas[p] += yon * 0.045                 # p gününde sert makas açılması
        ek_makas[p + 1: p + 11] -= yon * 0.0045    # sonraki 10 günde makasın kapanması

    # Son 20 iş gününde A aşırı önde gitsin (güncel z >= +2.0)
    ek_makas[-20:] = 0.006
    ra = rb + ek_makas
    c = 0.01 * rng.standard_normal(n)  # ilişkisiz 3. varlık
    return pd.DataFrame({"A": ra, "B": rb, "C": c}, index=idx)


def test_makas_ileriye_bakis_sizintisi_yok():
    g = _sentetik_makas_verisi()
    kesim = 650
    s1 = makas.ikili_makas_serisi(g.iloc[:kesim], "A", "B", kisa_pencere=20, uzun_pencere=250, makas_turu="beta")

    g_bozuk = g.copy()
    g_bozuk.iloc[kesim:] = g_bozuk.iloc[kesim:] * -20.0 + 0.2
    s2 = makas.ikili_makas_serisi(g_bozuk, "A", "B", kisa_pencere=20, uzun_pencere=250, makas_turu="beta")

    for col in ("beta", "gunluk_makas", "kisa_makas", "makas_ort", "makas_std", "makas_z"):
        pd.testing.assert_series_equal(s1[col], s2[col].iloc[:kesim])


def test_makas_tarama_ve_geri_donus():
    g = _sentetik_makas_verisi()
    tarama = makas.makas_tarama(g, uzun_pencere=250, kisa_pencere=20, min_corr=0.55, ufuk=10, makas_turu="beta")
    # Yalnızca (A, B) çifti yüksek korelasyonlu olmalı; C elenmeli
    assert len(tarama) == 1
    satir = tarama.iloc[0]
    assert satir["A"] == "A" and satir["B"] == "B"
    assert satir["r_250"] > 0.75
    assert abs(satir["beta"] - 1.0) < 0.25
    assert satir["makas_z"] >= 2.0
    assert satir["durum"] == "A aşırı önde / B geride"
    assert satir["kapanma_orani"] > 70.0

    # Detaylı geri dönüş testi (5, 10, 20 iş günü)
    gd = makas.makas_geri_donus_testi(g, "A", "B", kisa_pencere=20, uzun_pencere=250, k=2.0, ufuklar=(5, 10, 20))
    gd_10 = gd[(gd["yon"] == "tum") & (gd["ufuk"] == 10)].iloc[0]
    assert gd_10["n"] >= 8
    assert gd_10["kapanma_orani"] > 70.0
    assert gd_10["medyan_kapanma"] > 0.5


def test_farkli_birimli_ciftte_dogrudan_makas_vol_std_olur():
    g = _sentetik_makas_verisi()
    g["US10Y"] = g["B"] * 1000.0  # faiz bp serisi
    seri = makas.ikili_makas_serisi(g, "A", "US10Y", makas_turu="dogrudan")
    assert seri.attrs["etkin_tur"] == "vol_std"
    assert seri["makas_z"].dropna().abs().max() < 20.0
