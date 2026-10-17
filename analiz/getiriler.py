"""Getiri hesapları: log-getiri (fiyat), bp değişim (faiz), USD çevirisi, haftalık getiri."""
import numpy as np
import pandas as pd


def _birim(katalog, kod):
    """Katalogdan seri birimi; katalogda yoksa 'fiyat' varsay."""
    k = katalog.set_index("kod")
    if kod in k.index:
        return k.loc[kod, "birim"]
    return "fiyat"


def getiri_hesapla(panel, katalog, max_bosluk_gun=5, hafta_sonu_at=True):
    """Seviye panelinden getiri paneli.

    fiyat      -> ln(P_t / P_onceki)
    faiz_yuzde -> (y_t - y_onceki) * 100  (bp)
    'onceki' serinin kendi bir önceki GÖZLEMİDİR (ileri doldurma yok). Tatilden sonraki
    getiri çok günlüdür; iki gözlem arası takvim günü > max_bosluk_gun ise NaN.
    Fiyat <= 0 olan gözlemler NaN sayılır. hafta_sonu_at: cumartesi/pazar satırlarını at
    (seviyelerde, getiriden ÖNCE atılır: kripto Pazartesi getirisi Cuma->Pazartesi olur, toplam hareket korunur).
    """
    if hafta_sonu_at:
        # Önce seviyelerde hafta sonunu at: kripto Pazartesi getirisi = ln(P_Pzt / P_Cum)
        panel = panel[panel.index.dayofweek < 5]
    cikti = {}
    for kod in panel.columns:
        s = panel[kod].astype(float)
        faiz = _birim(katalog, kod) == "faiz_yuzde"
        deger = s if faiz else np.log(s.where(s > 0))
        d = deger.dropna()
        fark = d.diff()
        gun = d.index.to_series().diff().dt.days
        fark = fark.where(gun <= max_bosluk_gun)
        if faiz:
            fark = fark * 100.0
        cikti[kod] = fark.reindex(panel.index)
    g = pd.DataFrame(cikti, index=panel.index)
    return g.dropna(how="all")


def usd_cevir(panel, katalog, kodlar=None):
    """Yerel seviyeleri USD'ye çevirir (seviye düzeyinde).

    Katalogda usd_kur_kodu dolu olan seriler için: kur 'yerel / USD' ise (usd_kur_ters=False,
    örn. TRY=X) usd = yerel / kur; kur 'USD / yerel' ise (usd_kur_ters=True, örn. EURUSD=X)
    usd = yerel * kur. Kur kodu boş/NaN olan seriler (USD zaten, kripto, VIX...) aynen kalır.
    Seri veya kur o gün NaN ise sonuç NaN (doldurma yok). Kur serisi panelde olmalı.
    """
    k = katalog.set_index("kod")
    kodlar = list(panel.columns) if kodlar is None else list(kodlar)
    cikti = {}
    for kod in kodlar:
        s = panel[kod].astype(float)
        kur = k.loc[kod, "usd_kur_kodu"] if kod in k.index else None
        if kur is None or pd.isna(kur) or kur == "":
            cikti[kod] = s
            continue
        if kur not in panel.columns:
            raise KeyError(f"{kod} için kur serisi panelde yok: {kur}")
        ters = bool(k.loc[kod, "usd_kur_ters"])
        kurs = panel[kur].astype(float)
        cikti[kod] = s * kurs if ters else s / kurs
    return pd.DataFrame(cikti, index=panel.index)


def haftalik_seviye(panel, kural="W-FRI"):
    """Haftalık son GÖZLEM (haftanın son dolu değeri; boş haftalar NaN kalır)."""
    return panel.resample(kural).last()


def haftalik_getiriler(panel, katalog, kural="W-FRI"):
    """Örtüşmeyen haftalık getiriler (log / bp). Gelen panel günlük SEVİYE paneli olmalı."""
    hs = haftalik_seviye(panel, kural)
    return getiri_hesapla(hs, katalog, max_bosluk_gun=21, hafta_sonu_at=False)
