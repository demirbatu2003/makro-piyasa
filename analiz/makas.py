"""İkili Makas (Spread / Göreli Değer) ve Ortalamaya Dönüş (Mean-Reversion) analizi.
Saf pandas/numpy fonksiyonları, I/O ve Streamlit yok.

Bölüm 1 (`makas_tarama`):
- Son `uzun_pencere` (varsayılan 250 iş günü) içinde mutlak korelasyonu |r| >= min_corr olan tüm varlık
  çiftlerini (A, B) tarar.
- Her çift için günlük makası (ex-ante OLS beta-ayarlı, ex-ante 60g volatilite-standardize veya doğrudan
  getiri farkı) ve son `kisa_pencere` (5, 10, 20, 60 iş günü) kümülatif makas değişiminin kendi geçmiş
  rolling `uzun_pencere` ex-ante ortalaması ve standart sapmasına göre Z-skorunu (`makas_z`) hesaplar.
- Geçmişte |z| >= z_esik olduğunda takip eden `ufuk` iş gününde makasın ters yönde kapanma (ortalamaya
  dönme) oranını (%) ve örneklem sayısını (`n_olay`) raporlar.

Bölüm 2 (`ikili_makas_serisi`, `makas_geri_donus_testi`):
- Seçili (A, B) çifti için son 250 iş günü normalize performans serilerini, zaman içindeki `makas_z`
  serisini ve +k*sigma / -k*sigma aşım olaylarından sonraki 5, 10, 20 iş günlük ortalamaya dönüş testini üretir.

Kural: Hiçbir yerde ileriye bakış sızıntısı (look-ahead bias) yoktur. Tüm volatilite, beta ve makas
z-skoru ortalama/std parametreleri yalnız o güne kadarki geçmişle (.shift(1), ex-ante) hesaplanır.
"""
import numpy as np
import pandas as pd

from . import korelasyon
from .beklenti import FAIZ_VARSAYILAN, _bagimsiz_konumlar, _birim_bilgisi, _ileri_kumulatif_sonraki

KISA_PENCERELER = (5, 10, 20, 60)
GERI_DONUS_UFUKLAR = (5, 10, 20)
MAKAS_TURLERI = {
    "beta": "β-Ayarlı Makas (Ex-Ante OLS)",
    "vol_std": "Volatilite-Standardize Makas (60g σ)",
    "dogrudan": "Doğrudan Getiri Farkı (R_A − R_B)",
}


def _etkin_makas_turu(a, b, makas_turu="beta", katalog=None):
    """Farklı birimli (fiyat vs faiz_yuzde) çiftlerde 'dogrudan' seçilmişse 'vol_std'ye düşer."""
    t = str(makas_turu).lower().strip()
    if t == "dogrudan":
        _, ba = _birim_bilgisi(a, katalog)
        _, bb = _birim_bilgisi(b, katalog)
        if ba != bb:
            return "vol_std"
    if t not in ("beta", "vol_std", "dogrudan"):
        raise ValueError(f"Bilinmeyen makas_turu: {makas_turu}")
    return t


def _makas_olcek(a, b, etkin_tur, katalog=None):
    """Makas değişimini kullanıcıya gösterilecek birime çeviren (çarpan, birim_etiketi)."""
    if etkin_tur == "vol_std":
        return 1.0, "σ"
    ca, ba = _birim_bilgisi(a, katalog)
    cb, bb = _birim_bilgisi(b, katalog)
    if ba == bb:
        return ca, ba
    return ca, ba


def makas_durumu(z, esik_asiri=2.0, esik_aciliyor=1.5):
    """Tek bir makas z-skoru için sözel durum etiketi."""
    if z is None or not np.isfinite(z):
        return "Veri yok"
    zv = float(z)
    if zv >= esik_asiri:
        return "A aşırı önde / B geride"
    if zv <= -esik_asiri:
        return "A geride kaldı / B önde"
    if abs(zv) >= esik_aciliyor:
        return "Makas açılıyor"
    return "Normal"


def ikili_makas_serisi(getiri, a, b, kisa_pencere=20, uzun_pencere=250, sigma_pencere=60,
                       min_sigma_gun=40, makas_turu="beta", katalog=None):
    """(a, b) çifti için ex-ante günlük makas, kısa pencere kümülatif makas, makas Z-skoru ve
    son `uzun_pencere` iş günü normalize performans serilerini döner.

    Döner: DataFrame(index=getiri.index) sütunlar:
      r_a, r_b, beta, gunluk_makas, kisa_makas, makas_ort, makas_std, makas_z,
      a_kisa_getiri, b_kisa_getiri, norm_a, norm_b, kum_std_a, kum_std_b"""
    kisa_pencere = int(kisa_pencere)
    uzun_pencere = int(uzun_pencere)
    min_kisa = max(1, int(np.ceil(kisa_pencere * 0.65)))
    min_uzun = min(uzun_pencere, max(40, int(np.ceil(uzun_pencere * 0.6))))
    etkin_tur = _etkin_makas_turu(a, b, makas_turu, katalog)

    ra = getiri[a].astype(float)
    rb = getiri[b].astype(float)
    ortak = ra.notna() & rb.notna()
    ra_o = ra.where(ortak)
    rb_o = rb.where(ortak)

    # Ex-ante OLS beta ve korelasyon (yalnız t-1 ve öncesiyle)
    cov_ab = ra_o.rolling(uzun_pencere, min_periods=min_uzun).cov(rb_o).shift(1)
    var_b = rb_o.rolling(uzun_pencere, min_periods=min_uzun).var().shift(1)
    var_a = ra_o.rolling(uzun_pencere, min_periods=min_uzun).var().shift(1)
    beta_ex = (cov_ab / var_b.where(var_b > 0)).ffill(limit=5)
    denom = np.sqrt((var_a * var_b).where((var_a > 0) & (var_b > 0)))
    corr_ex = (cov_ab / denom).ffill(limit=5)

    # Ex-ante 60g volatiliteler (yalnız t-1 ve öncesiyle)
    sig_a = ra.dropna().rolling(sigma_pencere, min_periods=min_sigma_gun).std().shift(1).reindex(getiri.index).ffill(limit=5)
    sig_b = rb.dropna().rolling(sigma_pencere, min_periods=min_sigma_gun).std().shift(1).reindex(getiri.index).ffill(limit=5)
    std_a = ra / sig_a.where(sig_a > 0)
    std_b = rb / sig_b.where(sig_b > 0)

    if etkin_tur == "beta":
        gunluk_makas = (ra - beta_ex * rb).where(ortak)
    elif etkin_tur == "vol_std":
        isaret = pd.Series(np.where(corr_ex < 0, -1.0, 1.0), index=getiri.index)
        gunluk_makas = (std_a - isaret * std_b).where(ortak)
    else:  # dogrudan
        gunluk_makas = (ra - rb).where(ortak)

    kisa_makas = gunluk_makas.rolling(kisa_pencere, min_periods=min_kisa).sum()
    # Ex-ante rolling ortalama ve std: .shift(1) ile t günü z-skoru yalnız t-1'e kadarki dağılımı kullanır
    makas_ort = kisa_makas.rolling(uzun_pencere, min_periods=min_uzun).mean().shift(1)
    makas_std = kisa_makas.rolling(uzun_pencere, min_periods=min_uzun).std().shift(1)
    makas_z = (kisa_makas - makas_ort) / makas_std.where(makas_std > 0)

    ca, ba = _birim_bilgisi(a, katalog)
    cb, bb = _birim_bilgisi(b, katalog)
    a_kisa = ra.rolling(kisa_pencere, min_periods=min_kisa).sum() * ca
    b_kisa = rb.rolling(kisa_pencere, min_periods=min_kisa).sum() * cb

    # Son uzun_pencere iş günü için normalize performans (100 bazlı ve kümülatif standart getiri)
    norm_a = pd.Series(np.nan, index=getiri.index, dtype=float)
    norm_b = pd.Series(np.nan, index=getiri.index, dtype=float)
    kum_std_a = pd.Series(np.nan, index=getiri.index, dtype=float)
    kum_std_b = pd.Series(np.nan, index=getiri.index, dtype=float)

    son_dilim = getiri.index[-uzun_pencere:] if len(getiri) >= uzun_pencere else getiri.index
    if len(son_dilim):
        ra_son = ra.loc[son_dilim].fillna(0.0)
        rb_son = rb.loc[son_dilim].fillna(0.0)
        if ba == "bp":
            # Faiz serisinde 100 + kümülatif puan değişimi (bp / 100)
            na = 100.0 + (ra_son / 100.0).cumsum() - (ra_son.iloc[0] / 100.0)
        else:
            na = 100.0 * np.exp(ra_son.cumsum() - ra_son.iloc[0])
        if bb == "bp":
            nb = 100.0 + (rb_son / 100.0).cumsum() - (rb_son.iloc[0] / 100.0)
        else:
            nb = 100.0 * np.exp(rb_son.cumsum() - rb_son.iloc[0])
        norm_a.loc[son_dilim] = na
        norm_b.loc[son_dilim] = nb

        sa_son = std_a.loc[son_dilim].fillna(0.0)
        sb_son = std_b.loc[son_dilim].fillna(0.0)
        kum_std_a.loc[son_dilim] = sa_son.cumsum() - sa_son.iloc[0]
        kum_std_b.loc[son_dilim] = sb_son.cumsum() - sb_son.iloc[0]

    out = pd.DataFrame({
        "r_a": ra,
        "r_b": rb,
        "beta": beta_ex,
        "gunluk_makas": gunluk_makas,
        "kisa_makas": kisa_makas,
        "makas_ort": makas_ort,
        "makas_std": makas_std,
        "makas_z": makas_z,
        "a_kisa_getiri": a_kisa,
        "b_kisa_getiri": b_kisa,
        "norm_a": norm_a,
        "norm_b": norm_b,
        "kum_std_a": kum_std_a,
        "kum_std_b": kum_std_b,
    }, index=getiri.index)
    out.attrs["etkin_tur"] = etkin_tur
    out.attrs["a"] = a
    out.attrs["b"] = b
    return out


def makas_geri_donus_testi(getiri, a, b, kisa_pencere=20, uzun_pencere=250, sigma_pencere=60,
                           k=2.0, ufuklar=GERI_DONUS_UFUKLAR, ayikla_gun=5, min_olay=10,
                           makas_turu="beta", katalog=None, _seri_df=None):
    """Seçili (a, b) çiftinin makas Z-skoru geçmişte +k*sigma üstüne çıktığında ('A_onde'),
    -k*sigma altına indiğinde ('B_onde') ve her ikisinde ('tum', |z| >= k) takip eden `ufuklar`
    (varsayılan 5, 10, 20 iş günü) içinde makasın ters yönde kapanma (ortalamaya dönme) istatistiklerini hesaplar.

    Kapanma (mean-reversion) ölçümü:
    Olay günü t'den sonraki t+1 .. t+ufuk iş günlerindeki gelecek kümülatif makas değişimi
    Delta_S = sum_{j=1..ufuk} gunluk_makas[t+j] üzerinden ölçülür (pencere kayması yanılsaması yoktur).
    Kapanma miktarı = -sign(z_t) * Delta_S (> 0 ise makas ters yönde kapanmıştır).

    Döner: DataFrame(yon, yon_etiket, ufuk, n, kapanma_orani, medyan_kapanma, q25_kapanma, q75_kapanma,
                     medyan_z_degisim, birim, yetersiz)."""
    seri = _seri_df if _seri_df is not None else ikili_makas_serisi(
        getiri, a, b, kisa_pencere=kisa_pencere, uzun_pencere=uzun_pencere,
        sigma_pencere=sigma_pencere, makas_turu=makas_turu, katalog=katalog,
    )
    etkin_tur = seri.attrs.get("etkin_tur", _etkin_makas_turu(a, b, makas_turu, katalog))
    carpan, birim = _makas_olcek(a, b, etkin_tur, katalog)

    z_np = seri["makas_z"].to_numpy(dtype=float)
    gm_df = seri[["gunluk_makas"]]
    n_satir = len(seri)

    yon_tanimlari = [
        ("tum", f"Tüm Aşırılıklar (|z| ≥ {k:g}σ)", np.isfinite(z_np) & (np.abs(z_np) >= float(k))),
        ("A_onde", f"A Aşırı Önde (z ≥ +{k:g}σ)", np.isfinite(z_np) & (z_np >= float(k))),
        ("B_onde", f"B Aşırı Önde (z ≤ −{k:g}σ)", np.isfinite(z_np) & (z_np <= -float(k))),
    ]

    cols = ["yon", "yon_etiket", "ufuk", "n", "kapanma_orani", "medyan_kapanma",
            "q25_kapanma", "q75_kapanma", "medyan_z_degisim", "birim", "yetersiz"]
    satirlar = []
    olay_sozluk = {}

    for yon_kod, yon_ad, mask in yon_tanimlari:
        # Yeni bir aşırılık döneminin başlangıcı (eşik aşımı) + ardışık ayikla_gun dışlaması
        onceki = np.r_[False, mask[:-1]]
        baslangiclar = np.flatnonzero(mask & ~onceki)
        bagimsiz = _bagimsiz_konumlar(baslangiclar, ayikla_gun=ayikla_gun)
        olay_sozluk[yon_kod] = seri.index[bagimsiz]
        for h in ufuklar:
            h = int(h)
            uygun = bagimsiz[bagimsiz + h < n_satir]
            if len(uygun) == 0:
                satirlar.append({
                    "yon": yon_kod, "yon_etiket": yon_ad, "ufuk": h, "n": 0,
                    "kapanma_orani": np.nan, "medyan_kapanma": np.nan,
                    "q25_kapanma": np.nan, "q75_kapanma": np.nan,
                    "medyan_z_degisim": np.nan, "birim": birim, "yetersiz": True,
                })
                continue
            ileri_makas = _ileri_kumulatif_sonraki(gm_df, uygun, h)[:, 0]
            z_olay = z_np[uygun]
            z_sonra = z_np[uygun + h]
            isaret = np.sign(z_olay)

            # Kapanma miktarı: z > 0 iken gelecek makas düştüyse (+), z < 0 iken gelecek makas yükseldiyse (+)
            kapanma = -isaret * ileri_makas * carpan
            gecerli = np.isfinite(kapanma)
            kv = kapanma[gecerli]
            n_g = len(kv)
            if n_g == 0:
                satirlar.append({
                    "yon": yon_kod, "yon_etiket": yon_ad, "ufuk": h, "n": 0,
                    "kapanma_orani": np.nan, "medyan_kapanma": np.nan,
                    "q25_kapanma": np.nan, "q75_kapanma": np.nan,
                    "medyan_z_degisim": np.nan, "birim": birim, "yetersiz": True,
                })
                continue
            q25, med, q75 = np.quantile(kv, [0.25, 0.50, 0.75])
            oran = float((kv > 0).mean() * 100.0)

            z_kapanma = -isaret * (z_sonra - z_olay)
            zk_gecerli = z_kapanma[np.isfinite(z_kapanma)]
            med_zk = float(np.median(zk_gecerli)) if len(zk_gecerli) else np.nan

            satirlar.append({
                "yon": yon_kod,
                "yon_etiket": yon_ad,
                "ufuk": h,
                "n": int(n_g),
                "kapanma_orani": oran,
                "medyan_kapanma": float(med),
                "q25_kapanma": float(q25),
                "q75_kapanma": float(q75),
                "medyan_z_degisim": med_zk,
                "birim": birim,
                "yetersiz": bool(n_g < min_olay),
            })

    out = pd.DataFrame(satirlar, columns=cols)
    out.attrs["olay_tarihleri"] = olay_sozluk
    return out


def makas_tarama(getiri, uzun_pencere=250, kisa_pencere=20, min_corr=0.55, ufuk=10,
                 z_esik=2.0, sigma_pencere=60, yontem="spearman", makas_turu="beta",
                 ayikla_gun=5, min_olay=10, katalog=None):
    """Bölüm 1 ana fonksiyonu: Otomatik Makas Tarayıcısı.

    Son `uzun_pencere` iş gününde |r| >= min_corr olan tüm varlık çiftlerini (A, B) tarar;
    her çift için son `kisa_pencere` günlük kümülatif makas Z-skorunu (`makas_z`),
    OLS betasini, kısa getirileri, durumu ve geçmişte |z| >= z_esik olduğunda takip eden
    `ufuk` iş gününde makasın kapanma (ortalamaya dönme) oranını (%) hesaplar.

    Döner: DataFrame(A, B, r_250, beta, A_kisa_getiri, B_kisa_getiri, makas_z, mutlak_z,
                     durum, kapanma_orani, medyan_kapanma, n_olay, birim_a, birim_b,
                     makas_birim, yetersiz)
    |makas_z| büyüklüğüne göre azalan sırada döner."""
    cols = ["A", "B", "r_250", "beta", "A_kisa_getiri", "B_kisa_getiri", "makas_z", "mutlak_z",
            "durum", "kapanma_orani", "medyan_kapanma", "n_olay", "birim_a", "birim_b",
            "makas_birim", "yetersiz"]
    if getiri.empty or getiri.shape[1] < 2:
        return pd.DataFrame(columns=cols)

    corr, _ = korelasyon.korelasyon_matrisi(getiri, pencere=int(uzun_pencere), yontem=yontem)
    kodlar = list(corr.columns)
    c_np = corr.to_numpy(dtype=float)

    satirlar = []
    for i in range(len(kodlar)):
        for j in range(i + 1, len(kodlar)):
            r_val = c_np[i, j]
            if not np.isfinite(r_val) or abs(r_val) < float(min_corr):
                continue
            a, b = kodlar[i], kodlar[j]
            seri = ikili_makas_serisi(
                getiri, a, b, kisa_pencere=kisa_pencere, uzun_pencere=uzun_pencere,
                sigma_pencere=sigma_pencere, makas_turu=makas_turu, katalog=katalog,
            )
            z_dolu = seri["makas_z"].dropna()
            if len(z_dolu) == 0:
                continue
            son_t = z_dolu.index[-1]
            z_son = float(z_dolu.iloc[-1])
            beta_dolu = seri["beta"].loc[:son_t].dropna()
            beta_son = float(beta_dolu.iloc[-1]) if len(beta_dolu) else np.nan
            a_kisa = float(seri.loc[son_t, "a_kisa_getiri"]) if pd.notna(seri.loc[son_t, "a_kisa_getiri"]) else np.nan
            b_kisa = float(seri.loc[son_t, "b_kisa_getiri"]) if pd.notna(seri.loc[son_t, "b_kisa_getiri"]) else np.nan

            gd = makas_geri_donus_testi(
                getiri, a, b, kisa_pencere=kisa_pencere, uzun_pencere=uzun_pencere,
                sigma_pencere=sigma_pencere, k=z_esik, ufuklar=(int(ufuk),),
                ayikla_gun=ayikla_gun, min_olay=min_olay, makas_turu=makas_turu,
                katalog=katalog, _seri_df=seri,
            )
            gd_tum = gd[(gd["yon"] == "tum") & (gd["ufuk"] == int(ufuk))]
            if len(gd_tum):
                kap_oran = float(gd_tum.iloc[0]["kapanma_orani"]) if pd.notna(gd_tum.iloc[0]["kapanma_orani"]) else np.nan
                med_kap = float(gd_tum.iloc[0]["medyan_kapanma"]) if pd.notna(gd_tum.iloc[0]["medyan_kapanma"]) else np.nan
                n_ol = int(gd_tum.iloc[0]["n"])
                yet = bool(gd_tum.iloc[0]["yetersiz"])
                m_birim = str(gd_tum.iloc[0]["birim"])
            else:
                kap_oran, med_kap, n_ol, yet, m_birim = np.nan, np.nan, 0, True, "%"

            _, ba = _birim_bilgisi(a, katalog)
            _, bb = _birim_bilgisi(b, katalog)
            satirlar.append({
                "A": a,
                "B": b,
                "r_250": float(r_val),
                "beta": beta_son,
                "A_kisa_getiri": a_kisa,
                "B_kisa_getiri": b_kisa,
                "makas_z": z_son,
                "mutlak_z": abs(z_son),
                "durum": makas_durumu(z_son),
                "kapanma_orani": kap_oran,
                "medyan_kapanma": med_kap,
                "n_olay": n_ol,
                "birim_a": ba,
                "birim_b": bb,
                "makas_birim": m_birim,
                "yetersiz": yet,
            })

    if not satirlar:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(satirlar, columns=cols)
    return df.sort_values("mutlak_z", ascending=False, na_position="last").reset_index(drop=True)
