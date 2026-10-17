"""Test ortak verisi: bilinen yapıya sahip sentetik seriler."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# makro-pano klasörünü path'e ekle ('analiz' paketi buradan import edilir)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

N = 1500


@pytest.fixture(scope="session")
def idx():
    return pd.bdate_range("2018-01-01", periods=N)


@pytest.fixture(scope="session")
def getiri(idx):
    """Sentetik getiri paneli:
    A,B rho=0.8 | C bağımsız | D(t) = 0.7*A(t-1) + gürültü (A, D'yi 1 gün önden gider)
    T tetikleyici (sigma 0.01) | R(t) = 0.8*T(t-1) + gürültü (T olayından sonraki gün tepki)."""
    rng = np.random.default_rng(42)
    a = rng.standard_normal(N)
    b = 0.8 * a + 0.6 * rng.standard_normal(N)
    c = rng.standard_normal(N)
    d = 0.7 * np.r_[0, a[:-1]] + 0.7 * rng.standard_normal(N)
    t = 0.01 * rng.standard_normal(N)
    r = 0.8 * np.r_[0, t[:-1]] + 0.005 * rng.standard_normal(N)
    return pd.DataFrame({"A": a, "B": b, "C": c, "D": d, "T": t, "R": r}, index=idx) * 0.01 / 0.01


@pytest.fixture(scope="session")
def katalog():
    return pd.DataFrame([
        dict(kod="SPX", ad="S&P", kategori="borsa", birim="fiyat", frekans="gunluk",
             kapanis_notu="ABD 21:00 UTC", usd_kur_kodu=None, usd_kur_ters=False),
        dict(kod="BIST", ad="BIST100", kategori="borsa", birim="fiyat", frekans="gunluk",
             kapanis_notu="TR 15:00 UTC", usd_kur_kodu="USDTRY", usd_kur_ters=False),
        dict(kod="USDTRY", ad="USDTRY", kategori="fx", birim="fiyat", frekans="gunluk",
             kapanis_notu="FX 24/5", usd_kur_kodu=None, usd_kur_ters=False),
        dict(kod="DAX", ad="DAX", kategori="borsa", birim="fiyat", frekans="gunluk",
             kapanis_notu="EU 16:30 UTC", usd_kur_kodu="EURUSD", usd_kur_ters=True),
        dict(kod="EURUSD", ad="EURUSD", kategori="fx", birim="fiyat", frekans="gunluk",
             kapanis_notu="FX 24/5", usd_kur_kodu=None, usd_kur_ters=False),
        dict(kod="DGS10", ad="US 10y", kategori="faiz", birim="faiz_yuzde", frekans="gunluk",
             kapanis_notu="ABD", usd_kur_kodu=None, usd_kur_ters=False),
    ])
