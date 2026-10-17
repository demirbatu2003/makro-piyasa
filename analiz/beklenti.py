"""Koşullu beklenti ve canlı şok motoru. Saf pandas/numpy fonksiyonları, I/O ve Streamlit yok.

Bölüm 1: Son iş günlerindeki canlı şokları (|z| >= k, ex-ante 60g sigma) tarar ve seçilen şokun
geçmişteki benzer örneklerinden sonraki H iş gününde diğer varlıkların dağılımını / olasılık farkını hesaplar.

Bölüm 2: Çoklu koşullu olasılık motoru ("Eğer X ve Y olursa ne yükselir/düşer?"). Seçilen varlık
hareketi ve/veya VIX rejimi koşullarının geçmişte birlikte sağlandığı bağımsız dönemleri (±5 iş günü
örtüşme ayıklamalı) bulur ve takip eden ufukta (5, 20, 60 iş günü) koşullu vs koşulsuz dağılımı karşılaştırır.

Kural: Hiçbir yerde ileriye bakış sızıntısı (look-ahead bias) yoktur. Tüm volatilite ve z-skor hesapları
yalnız o güne kadarki geçmişle (ex-ante, .shift(1)) yapılır; ileri getiriler yalnız t+1..t+ufuk aralığı
tamamlanmış geçmiş olaylar üzerinden hesaplanır.
"""
import numpy as np
import pandas as pd

from . import rejim

FAIZ_VARSAYILAN = frozenset({"US2Y", "US10Y", "FED", "ECB", "DGS10", "DGS2"})
SOK_UFUKLAR = (1, 5, 20)
KOSUL_UFUKLAR = (5, 20, 60)

DURUM_AD = {
    "yukari": "Yükselişte (>0)",
    "sert_yukari": "Sert Yükselişte (>+1σ)",
    "cok_sert_yukari": "Çok Sert Yükselişte (>+2σ)",
    "asagi": "Düşüşte (<0)",
    "sert_asagi": "Sert Düşüşte (<-1σ)",
    "cok_sert_asagi": "Çok Sert Düşüşte (<-2σ)",
}


def _birim_bilgisi(kod, katalog=None):
    """Seri için (ölçek çarpanı, birim etiketi) döner. Fiyat log-getirisi -> (*100, '%'); faiz -> (*1, 'bp')."""
    if katalog is not None and "kod" in katalog.columns and "birim" in katalog.columns:
        k = katalog.set_index("kod")
        if kod in k.index:
            faiz = k.loc[kod, "birim"] == "faiz_yuzde"
            return (1.0, "bp") if faiz else (100.0, "%")
    if kod in FAIZ_VARSAYILAN:
        return (1.0, "bp")
    return (100.0, "%")


def _bagimsiz_konumlar(aday_konumlar, ayikla_gun=5):
    """Sıralı tam sayı konum dizisinde ardışık `ayikla_gun` gözlem içindeki örtüşen olayları ayıklar."""
    secilen = []
    son = -10**9
    for p in aday_konumlar:
        p = int(p)
        if p - son > ayikla_gun:
            secilen.append(p)
            son = p
    return np.array(secilen, dtype=int)


def _ileri_kumulatif_sonraki(getiri, konumlar, ufuk):
    """Her olay konumu p için takip eden p+1 .. p+ufuk (dahil) satırlarının kümülatif getiri toplamı.
    Olay günü p'nin kendisi dahil edilmez (yalnız şok sonrası gelecek hareket ölçülür).
    p + ufuk >= len(getiri) olan (henüz tamamlanmamış) dönemler veya pencerede hiç gözlemi olmayanlar NaN döner."""
    konumlar = np.asarray(konumlar, dtype=int)
    n_satir, n_sutun = getiri.shape
    if len(konumlar) == 0 or ufuk < 1:
        return np.empty((0, n_sutun), dtype=float)
    arr = getiri.to_numpy(dtype=float)
    dolu = np.isfinite(arr)
    cs = np.vstack([np.zeros((1, n_sutun)), np.cumsum(np.where(dolu, arr, 0.0), axis=0)])
    cn = np.vstack([np.zeros((1, n_sutun)), np.cumsum(dolu, axis=0)])
    bas = konumlar + 1
    son = konumlar + int(ufuk)
    gecerli = (konumlar >= 0) & (son < n_satir)
    basc = np.where(gecerli, bas, 0)
    sonc = np.where(gecerli, son, 0)
    top = cs[sonc + 1] - cs[basc]
    adet = cn[sonc + 1] - cn[basc]
    return np.where(gecerli[:, None] & (adet > 0), top, np.nan)


def _ex_ante_z(seri, sigma_pencere=60, min_sigma_gun=40):
    """Serinin kendi dolu gözlemleri üzerinde ex-ante (bugün hariç, .shift(1)) sigma ve z-skoru."""
    s = seri.dropna().astype(float)
    sigma = s.rolling(sigma_pencere, min_periods=min_sigma_gun).std().shift(1)
    z = s / sigma.where(sigma > 0)
    return s.reindex(seri.index), sigma.reindex(seri.index), z.reindex(seri.index)


# ---------------------------------------------------------------- Bölüm 1: Canlı Şok Tarayıcısı ve Beklentileri
def son_soklari_bul(getiri, pencere_gun=10, k=1.8, sigma_pencere=60, min_sigma_gun=40, katalog=None):
    """Son `pencere_gun` iş gününde ex-ante `sigma_pencere` günlük std'ye göre |z| >= k hareket eden varlıkları bulur.

    Döner: DataFrame(tarih, kod, yon, getiri, getiri_olcekli, birim, sigma, z, mutlak_z)
    Tarihe (en yeni üstte) ve |z| büyüklüğüne göre sıralıdır."""
    cols = ["tarih", "kod", "yon", "getiri", "getiri_olcekli", "birim", "sigma", "z", "mutlak_z"]
    if getiri.empty or pencere_gun < 1:
        return pd.DataFrame(columns=cols)
    son_tarihler = set(getiri.index[-int(pencere_gun):])
    satirlar = []
    for kod in getiri.columns:
        s, sigma, z = _ex_ante_z(getiri[kod], sigma_pencere=sigma_pencere, min_sigma_gun=min_sigma_gun)
        mask = z.abs() >= float(k)
        aday_tarihler = [t for t in getiri.index[mask.fillna(False)] if t in son_tarihler]
        carpan, birim = _birim_bilgisi(kod, katalog)
        for t in aday_tarihler:
            zv = float(z.loc[t])
            gv = float(s.loc[t])
            sv = float(sigma.loc[t])
            satirlar.append({
                "tarih": t,
                "kod": kod,
                "yon": "yukari" if zv > 0 else "asagi",
                "getiri": gv,
                "getiri_olcekli": gv * carpan,
                "birim": birim,
                "sigma": sv * carpan,
                "z": zv,
                "mutlak_z": abs(zv),
            })
    if not satirlar:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(satirlar, columns=cols)
    return df.sort_values(["tarih", "mutlak_z"], ascending=[False, False]).reset_index(drop=True)


def sok_beklentisi(getiri, tetik, yon="yukari", k=1.8, ufuk=5, sigma_pencere=60, min_sigma_gun=40,
                   ayikla_gun=5, min_olay=15, siralama="olasilik_farki", katalog=None, tetik_dahil=False):
    """Seçilen `tetik` varlık geçmişte `yon` yönünde |z| >= k (ex-ante) hareket ettiğinde,
    takip eden `ufuk` iş günü sonunda diğer tüm varlıkların koşullu getiri ve yukarı olasılık tablosunu döner.

    Döner: DataFrame(hedef, birim, n, n_kosulsuz, medyan, q25, q75, kosulsuz_medyan, medyan_farki,
                     yukari_orani, kosulsuz_yukari_orani, olasilik_farki, yetersiz)
    `df.attrs['olay_tarihleri']` içinde bağımsız geçmiş olay tarihleri yer alır."""
    cols = ["hedef", "birim", "n", "n_kosulsuz", "medyan", "q25", "q75", "kosulsuz_medyan",
            "medyan_farki", "yukari_orani", "kosulsuz_yukari_orani", "olasilik_farki", "yetersiz"]
    if tetik not in getiri.columns or len(getiri) <= ufuk:
        bos = pd.DataFrame(columns=cols)
        bos.attrs["olay_tarihleri"] = pd.DatetimeIndex([])
        bos.attrs["n_olay"] = 0
        return bos

    _, _, z = _ex_ante_z(getiri[tetik], sigma_pencere=sigma_pencere, min_sigma_gun=min_sigma_gun)
    z_np = z.to_numpy(dtype=float)
    n_satir = len(getiri)
    ufuk = int(ufuk)

    # Koşulsuz havuz: tetikleyicinin ex-ante z-skorunun hesaplanabildiği ve ileri ufku tamamlanmış tüm günler
    gecerli_havuz = np.isfinite(z_np) & (np.arange(n_satir) + ufuk < n_satir)
    aday_konumlar = np.flatnonzero(gecerli_havuz)

    if yon == "yukari":
        sok_mask = gecerli_havuz & (z_np >= float(k))
    else:
        sok_mask = gecerli_havuz & (z_np <= -float(k))
    olay_konumlar = _bagimsiz_konumlar(np.flatnonzero(sok_mask), ayikla_gun=ayikla_gun)

    hedefler = list(getiri.columns) if tetik_dahil else [c for c in getiri.columns if c != tetik]
    hedef_df = getiri[hedefler]
    kum_olay = _ileri_kumulatif_sonraki(hedef_df, olay_konumlar, ufuk)
    kum_havuz = _ileri_kumulatif_sonraki(hedef_df, aday_konumlar, ufuk)

    satirlar = []
    for j, h in enumerate(hedefler):
        carpan, birim = _birim_bilgisi(h, katalog)
        vo = kum_olay[:, j] if len(olay_konumlar) else np.array([], dtype=float)
        vo = vo[np.isfinite(vo)]
        vt = kum_havuz[:, j] if len(aday_konumlar) else np.array([], dtype=float)
        vt = vt[np.isfinite(vt)]
        n_o = len(vo)
        n_t = len(vt)
        if n_o == 0:
            satirlar.append({
                "hedef": h, "birim": birim, "n": 0, "n_kosulsuz": n_t,
                "medyan": np.nan, "q25": np.nan, "q75": np.nan,
                "kosulsuz_medyan": float(np.median(vt) * carpan) if n_t else np.nan,
                "medyan_farki": np.nan,
                "yukari_orani": np.nan,
                "kosulsuz_yukari_orani": float((vt > 0).mean() * 100.0) if n_t else np.nan,
                "olasilik_farki": np.nan,
                "yetersiz": True,
            })
            continue
        q25, med, q75 = np.quantile(vo, [0.25, 0.50, 0.75]) * carpan
        k_med = float(np.median(vt) * carpan) if n_t else np.nan
        yuk = float((vo > 0).mean() * 100.0)
        k_yuk = float((vt > 0).mean() * 100.0) if n_t else np.nan
        satirlar.append({
            "hedef": h,
            "birim": birim,
            "n": int(n_o),
            "n_kosulsuz": int(n_t),
            "medyan": float(med),
            "q25": float(q25),
            "q75": float(q75),
            "kosulsuz_medyan": k_med,
            "medyan_farki": float(med - k_med) if np.isfinite(k_med) else np.nan,
            "yukari_orani": yuk,
            "kosulsuz_yukari_orani": k_yuk,
            "olasilik_farki": float(yuk - k_yuk) if np.isfinite(k_yuk) else np.nan,
            "yetersiz": bool(n_o < min_olay),
        })

    out = pd.DataFrame(satirlar, columns=cols)
    if len(out) and siralama in out.columns:
        out = out.sort_values(siralama, ascending=False, na_position="last").reset_index(drop=True)
    out.attrs["olay_tarihleri"] = getiri.index[olay_konumlar]
    out.attrs["n_olay"] = int(len(olay_konumlar))
    out.attrs["tetik"] = tetik
    out.attrs["yon"] = yon
    out.attrs["k"] = float(k)
    out.attrs["ufuk"] = int(ufuk)
    return out


def son_soklar_ve_beklentiler(getiri, pencere_gun=10, k=1.8, ufuk=5, tetik=None, yon=None,
                              sigma_pencere=60, min_sigma_gun=40, ayikla_gun=5, min_olay=15,
                              siralama="olasilik_farki", katalog=None, tetik_dahil=False):
    """Bölüm 1 ana fonksiyonu:
    1) Son `pencere_gun` iş günündeki canlı şokları (`soklar`) bulur.
    2) Seçilen `(tetik, yon)` (verilmezse en son gerçekleşen canlı şok) için geçmişteki aynı yönlü
       |z| >= k olaylarının `ufuk` iş günü sonrasındaki beklenti tablosunu (`beklentiler`) hesaplar.
    Döner: (soklar, beklentiler)."""
    soklar = son_soklari_bul(getiri, pencere_gun=pencere_gun, k=k,
                             sigma_pencere=sigma_pencere, min_sigma_gun=min_sigma_gun, katalog=katalog)
    if tetik is None:
        if len(soklar) == 0:
            bos = sok_beklentisi(getiri.iloc[0:0], "", ufuk=ufuk, katalog=katalog)
            return soklar, bos
        tetik = str(soklar.iloc[0]["kod"])
        yon = str(soklar.iloc[0]["yon"])
    elif yon is None:
        alt = soklar[soklar["kod"] == tetik]
        if len(alt):
            yon = str(alt.iloc[0]["yon"])
        else:
            son_deger = getiri[tetik].dropna()
            yon = "yukari" if (len(son_deger) == 0 or son_deger.iloc[-1] >= 0) else "asagi"

    beklentiler = sok_beklentisi(
        getiri, tetik=tetik, yon=yon, k=k, ufuk=ufuk,
        sigma_pencere=sigma_pencere, min_sigma_gun=min_sigma_gun,
        ayikla_gun=ayikla_gun, min_olay=min_olay, siralama=siralama,
        katalog=katalog, tetik_dahil=tetik_dahil,
    )
    return soklar, beklentiler


# ---------------------------------------------------------------- Bölüm 2: Çoklu Koşullu Olasılık Motoru
def _varlik_kosul_maskesi(getiri, kod, pencere=5, durum="yukari", k=1.0, sigma_pencere=60, min_sigma_gun=40):
    """Tek bir varlık koşulu için (koşul_sağlandı_maskesi, gözlem_geçerli_maskesi) döner.
    Tüm hesaplar yalnız t ve öncesiyle (ex-ante) yapılır."""
    s = getiri[kod].astype(float)
    pencere = max(1, int(pencere))
    if pencere == 1:
        r_m = s
    else:
        min_p = max(1, int(np.ceil(pencere * 0.6)))
        r_m = s.rolling(pencere, min_periods=min_p).sum()

    rm_dolu = r_m.dropna()
    sigma_m = rm_dolu.rolling(sigma_pencere, min_periods=min_sigma_gun).std().shift(1).reindex(getiri.index)
    z_m = r_m / sigma_m.where(sigma_m > 0)

    d = str(durum).lower().strip()
    if d in ("yukari", ">0", "pozitif"):
        gecerli = r_m.notna()
        mask = r_m > 0
    elif d in ("asagi", "<0", "negatif"):
        gecerli = r_m.notna()
        mask = r_m < 0
    elif d in ("sert_yukari", ">+1sigma", ">+ksigma"):
        gecerli = z_m.notna()
        mask = z_m >= float(k)
    elif d in ("cok_sert_yukari", ">+2sigma"):
        gecerli = z_m.notna()
        mask = z_m >= 2.0
    elif d in ("sert_asagi", "<-1sigma", "<-ksigma"):
        gecerli = z_m.notna()
        mask = z_m <= -float(k)
    elif d in ("cok_sert_asagi", "<-2sigma"):
        gecerli = z_m.notna()
        mask = z_m <= -2.0
    else:
        raise ValueError(f"Bilinmeyen koşul durumu: {durum}")
    return mask.fillna(False), gecerli.fillna(False)


def kosul_gunlerini_bul(getiri, kosullar=None, vix_seviye=None, vix_rejim=None,
                        vix_esikler=(15.0, 25.0), ufuk=20, ayikla_gun=5,
                        sigma_pencere=60, min_sigma_gun=40):
    """Verilen varlık koşulları ve/veya VIX rejimi koşulunun birlikte sağlandığı
    bağımsız geçmiş olay konumlarını, koşulsuz havuz konumlarını ve tam tarih maskesini döner."""
    n_satir = len(getiri)
    tam_gecerli = pd.Series(True, index=getiri.index)
    tam_maske = pd.Series(True, index=getiri.index)

    for ks in (kosullar or []):
        if not ks or not ks.get("kod"):
            continue
        m, g = _varlik_kosul_maskesi(
            getiri,
            kod=ks["kod"],
            pencere=ks.get("pencere", 5),
            durum=ks.get("durum", "yukari"),
            k=ks.get("k", 1.0),
            sigma_pencere=sigma_pencere,
            min_sigma_gun=min_sigma_gun,
        )
        tam_maske &= m
        tam_gecerli &= g

    if vix_rejim is not None and str(vix_rejim).strip() not in ("", "tumu", "hepsi", "yok"):
        if vix_seviye is None:
            raise ValueError("vix_rejim koşulu için vix_seviye serisi gereklidir.")
        rj = rejim.vix_rejimi(vix_seviye.reindex(getiri.index), esikler=vix_esikler)
        tam_gecerli &= rj.notna()
        tam_maske &= (rj == str(vix_rejim).strip())

    ufuk_uygun = np.arange(n_satir) + int(ufuk) < n_satir
    aday_konumlar = np.flatnonzero(tam_gecerli.to_numpy(dtype=bool) & ufuk_uygun)
    olay_aday = np.flatnonzero((tam_maske & tam_gecerli).to_numpy(dtype=bool) & ufuk_uygun)
    olay_konumlar = _bagimsiz_konumlar(olay_aday, ayikla_gun=ayikla_gun)
    bugun_aktif = bool((tam_maske & tam_gecerli).iloc[-1]) if n_satir > 0 else False
    return olay_konumlar, aday_konumlar, bugun_aktif


def kosullu_olasilik_tablosu(getiri, kosullar=None, ufuk=20, vix_seviye=None, vix_rejim=None,
                             vix_esikler=(15.0, 25.0), ayikla_gun=5, sigma_pencere=60,
                             min_sigma_gun=40, min_olay=15, siralama="olasilik_farki",
                             katalog=None, kod1=None, durum1="yukari", pencere1=5, k1=1.0,
                             kod2=None, durum2="yukari", pencere2=5, k2=1.0):
    """Bölüm 2 ana fonksiyonu: Çoklu koşullu olasılık motoru ("Eğer X ve Y olursa ne yükselir/düşer?").

    Koşullar `kosullar=[{"kod": ..., "pencere": ..., "durum": ..., "k": ...}, ...]` listesiyle
    veya doğrudan `kod1, durum1, pencere1, kod2, durum2, pencere2` parametreleriyle verilebilir.
    Opsiyonel olarak `vix_seviye` ve `vix_rejim` ('sakin'/'normal'/'gergin') eklenebilir.

    Döner: DataFrame(hedef, birim, n_kosullu, n_kosulsuz, yukari_olasiligi, kosulsuz_yukari,
                     olasilik_farki, medyan_kosullu, q25_kosullu, q75_kosullu, medyan_kosulsuz,
                     medyan_fark, yetersiz).
    `df.attrs['olay_tarihleri']` bağımsız dönem başlangıç tarihlerini,
    `df.attrs['bugun_aktif']` ise koşulun son iş gününde aktif olup olmadığını tutar."""
    cols = ["hedef", "birim", "n_kosullu", "n_kosulsuz", "yukari_olasiligi", "kosulsuz_yukari",
            "olasilik_farki", "medyan_kosullu", "q25_kosullu", "q75_kosullu", "medyan_kosulsuz",
            "medyan_fark", "yetersiz"]
    if kosullar is None:
        kosullar = []
        if kod1:
            kosullar.append({"kod": kod1, "durum": durum1, "pencere": pencere1, "k": k1})
        if kod2:
            kosullar.append({"kod": kod2, "durum": durum2, "pencere": pencere2, "k": k2})

    if getiri.empty or len(getiri) <= int(ufuk):
        bos = pd.DataFrame(columns=cols)
        bos.attrs["olay_tarihleri"] = pd.DatetimeIndex([])
        bos.attrs["n_olay"] = 0
        bos.attrs["bugun_aktif"] = False
        return bos

    olay_konumlar, aday_konumlar, bugun_aktif = kosul_gunlerini_bul(
        getiri, kosullar=kosullar, vix_seviye=vix_seviye, vix_rejim=vix_rejim,
        vix_esikler=vix_esikler, ufuk=ufuk, ayikla_gun=ayikla_gun,
        sigma_pencere=sigma_pencere, min_sigma_gun=min_sigma_gun,
    )

    hedefler = list(getiri.columns)
    kum_olay = _ileri_kumulatif_sonraki(getiri, olay_konumlar, int(ufuk))
    kum_havuz = _ileri_kumulatif_sonraki(getiri, aday_konumlar, int(ufuk))

    satirlar = []
    for j, h in enumerate(hedefler):
        carpan, birim = _birim_bilgisi(h, katalog)
        vo = kum_olay[:, j] if len(olay_konumlar) else np.array([], dtype=float)
        vo = vo[np.isfinite(vo)]
        vt = kum_havuz[:, j] if len(aday_konumlar) else np.array([], dtype=float)
        vt = vt[np.isfinite(vt)]
        n_k = len(vo)
        n_t = len(vt)
        if n_k == 0:
            satirlar.append({
                "hedef": h, "birim": birim, "n_kosullu": 0, "n_kosulsuz": int(n_t),
                "yukari_olasiligi": np.nan,
                "kosulsuz_yukari": float((vt > 0).mean() * 100.0) if n_t else np.nan,
                "olasilik_farki": np.nan,
                "medyan_kosullu": np.nan, "q25_kosullu": np.nan, "q75_kosullu": np.nan,
                "medyan_kosulsuz": float(np.median(vt) * carpan) if n_t else np.nan,
                "medyan_fark": np.nan,
                "yetersiz": True,
            })
            continue
        q25, med_k, q75 = np.quantile(vo, [0.25, 0.50, 0.75]) * carpan
        med_t = float(np.median(vt) * carpan) if n_t else np.nan
        yuk_k = float((vo > 0).mean() * 100.0)
        yuk_t = float((vt > 0).mean() * 100.0) if n_t else np.nan
        satirlar.append({
            "hedef": h,
            "birim": birim,
            "n_kosullu": int(n_k),
            "n_kosulsuz": int(n_t),
            "yukari_olasiligi": yuk_k,
            "kosulsuz_yukari": yuk_t,
            "olasilik_farki": float(yuk_k - yuk_t) if np.isfinite(yuk_t) else np.nan,
            "medyan_kosullu": float(med_k),
            "q25_kosullu": float(q25),
            "q75_kosullu": float(q75),
            "medyan_kosulsuz": med_t,
            "medyan_fark": float(med_k - med_t) if np.isfinite(med_t) else np.nan,
            "yetersiz": bool(n_k < min_olay),
        })

    out = pd.DataFrame(satirlar, columns=cols)
    if len(out) and siralama in out.columns:
        out = out.sort_values(siralama, ascending=False, na_position="last").reset_index(drop=True)
    out.attrs["olay_tarihleri"] = getiri.index[olay_konumlar]
    out.attrs["n_olay"] = int(len(olay_konumlar))
    out.attrs["bugun_aktif"] = bugun_aktif
    return out
