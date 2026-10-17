"""Veri sağlığı özeti: seri başına boşluk / bayatlık."""
import numpy as np
import pandas as pd


def seri_sagligi(panel, katalog=None, bugun=None, bayat_esik_is_gunu=3, bayat_esik_aylik_gun=45):
    """Seri başına: ilk, son, gozlem, bayatlik_is_gunu, beklenen_is_gunu, eksik_is_gunu,
    en_uzun_bosluk_gun, durum ('taze' | 'bayat' | 'bos').
    Aylık seriler (katalog frekans='aylik') eksik/beklenen hesabına girmez; bayatlık takvim günüdür.
    Not: tatiller 'eksik' görünür; ekran bunu doğal tatil olarak yorumlamalı (kesin ayrım yok)."""
    bugun = pd.Timestamp(bugun) if bugun is not None else panel.index.max()
    frek = {}
    if katalog is not None and "frekans" in katalog.columns:
        frek = katalog.set_index("kod")["frekans"].to_dict()
    satir = []
    for kod in panel.columns:
        s = panel[kod].dropna()
        aylik = frek.get(kod) == "aylik"
        if s.empty:
            satir.append(dict(kod=kod, ilk=pd.NaT, son=pd.NaT, gozlem=0, bayatlik_is_gunu=np.nan,
                              beklenen_is_gunu=np.nan, eksik_is_gunu=np.nan, en_uzun_bosluk_gun=np.nan,
                              durum="bos"))
            continue
        son = s.index[-1]
        bay = int(np.busday_count(son.date(), bugun.date())) if bugun > son else 0
        bosluk = s.index.to_series().diff().dt.days.max()
        if aylik:
            beklenen = eksik = np.nan
            durum = "bayat" if (bugun - son).days > bayat_esik_aylik_gun else "taze"
            bay = (bugun - son).days
        else:
            beklenen = int(np.busday_count(s.index[0].date(), son.date())) + 1
            eksik = max(beklenen - len(s), 0)
            durum = "bayat" if bay > bayat_esik_is_gunu else "taze"
        satir.append(dict(kod=kod, ilk=s.index[0], son=son, gozlem=len(s), bayatlik_is_gunu=bay,
                          beklenen_is_gunu=beklenen, eksik_is_gunu=eksik,
                          en_uzun_bosluk_gun=bosluk if pd.notna(bosluk) else 0, durum=durum))
    return pd.DataFrame(satir)
