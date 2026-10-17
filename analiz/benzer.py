"""Benzer Günler (analog / koşullu taban oranı). Saf fonksiyonlar; I/O ve Streamlit yok.

TAHMİN DEĞİL: "t gününe benzeyen geçmiş günlerde sonraki H iş gününde sonuçların dağılımı" ile
"koşulsuz" (aynı geçmiş aralıktaki tüm günler) dağılımı karşılaştırılır.

Tasarım kararları (önceden kayda geçirildi):
- Zaman ekseni: panelin ilk-son tarihi arasındaki hafta içi günler (iş günü ızgarası); "iş günü" = bu ızgarada satır.
- Özellikler yalnız t'de bilinen veriyle hesaplanır. Her serinin son gözlemi özellik hesabı için EN FAZLA 5 TAKVİM GÜNÜ
  ileri taşınır (tatil/haftalık boşluk); daha eskiyse NaN. SONUÇLARDA ileri doldurma YOKTUR: t veya t+H'de gözlem yoksa
  o gün o hedef için sonuç yoktur (NaN, n'e girmez).
- Standardizasyon: her gün için GENİŞLEYEN z-skor (ortalama/std yalnız o güne kadarki geçmişten; en az 500 gözlem ısınma).
  Böylece z[t] t sonrası veriden etkilenmez. Farklı günlerin z-skorları farklı (genişleyen) ölçeklerle hesaplandığından
  yaklaşık karşılaştırılabilir; bu bilinçli bir sadelik tercihidir.
- Benzerlik: seçili özellikler üzerinde Öklid uzaklığı. Adaylar "bugün"den en az H+5 iş günü önce olmalıdır.
  Açgözlü bağımsız seçim: en yakını al, ±20 iş günü içindekileri ele, K'ya kadar tekrarla.
- Koşulsuz taban oranı: aynı aday kümesindeki (analog arama havuzu) tüm günler.
- BTC özellik olarak KULLANILMAZ (geçmişi 2017-08'de başlar); hedef olarak kullanılır, n yalnız BTC verisi olan analoglardır.
"""
import numpy as np
import pandas as pd
from scipy import stats as _st

from . import getiriler

TASIMA_GUN = 5          # özellik için son gözlemin azami taşınma süresi (takvim günü)
ISINMA = 500            # z-skor için asgari iş günü
ARALIK = 20             # analoglar arası dışlama yarıçapı (iş günü)
VARSAYILAN_K = 25
UFUKLAR = (5, 20, 60)

OZELLIK_AD = {
    "vix": "VIX seviyesi",
    "dxy_60g": "DXY 60g değişim (log, %)",
    "brent_60g": "Brent 60g değişim (log, %)",
    "us10y_60g": "US10Y 60g değişim (bp)",
    "egri": "Eğri: US10Y − US2Y (puan)",
    "spx_vol20": "SPX 20g gerçekleşmiş oynaklık (yıllık, %)",
    "spx_60g": "SPX 60g değişim (log, %)",
    "usdtry_20g": "USDTRY 20g değişim (log, %)",
}
OZELLIKLER = tuple(OZELLIK_AD)
GEREKLI_SERILER = ("VIX", "DXY", "BRENT", "US10Y", "US2Y", "SPX", "USDTRY")

# hedef kodu -> (seri, tür, usd_çevir)
HEDEFLER = {
    "BIST100_TL": ("BIST100", "log", False),
    "BIST100_USD": ("BIST100", "log", True),
    "GRAMALTIN": ("GRAMALTIN", "log", False),
    "XAUUSD": ("XAUUSD", "log", False),
    "BTC": ("BTC", "log", False),
    "SPX": ("SPX", "log", False),
    "NASDAQ": ("NASDAQ", "log", False),
    "USDTRY": ("USDTRY", "log", False),
    "BRENT": ("BRENT", "log", False),
    "US10Y": ("US10Y", "bp", False),
}


def izgara(panel):
    return pd.bdate_range(panel.index.min().normalize(), panel.index.max().normalize())


def _tasi(s, grid, max_gun=TASIMA_GUN):
    """Seviyeyi ızgaraya taşır; son gözlem max_gun takvim gününden eskiyse NaN (yalnız özellikler için)."""
    s = s.dropna()
    if s.empty:
        return pd.Series(np.nan, index=grid)
    tarih = pd.Series(s.index, index=s.index)
    v = s.reindex(grid, method="ffill")
    son = tarih.reindex(grid, method="ffill")
    yas = (pd.Series(grid, index=grid) - son).dt.days
    return v.where(yas <= max_gun)


def ozellik_tablosu(panel):
    """t gününde bilinen veriyle 8 özellik (hafta içi ızgara). Ham (standardize edilmemiş)."""
    g = izgara(panel)
    L = {}
    for k in GEREKLI_SERILER:
        s = panel[k].astype(float)
        if k not in ("US10Y", "US2Y"):
            s = s.where(s > 0)
        L[k] = _tasi(s, g)

    def lg(s, n):
        return np.log(s / s.shift(n)) * 100.0

    spx = panel["SPX"].astype(float)
    spx = spx.where(spx > 0).dropna()
    r = np.log(spx).diff().reindex(g)  # gözlemli günlerin getirisi; tatilde NaN
    vol = r.rolling(20, min_periods=15).std() * np.sqrt(252) * 100.0
    o = pd.DataFrame({
        "vix": L["VIX"],
        "dxy_60g": lg(L["DXY"], 60),
        "brent_60g": lg(L["BRENT"], 60),
        "us10y_60g": (L["US10Y"] - L["US10Y"].shift(60)) * 100.0,
        "egri": L["US10Y"] - L["US2Y"],
        "spx_vol20": vol,
        "spx_60g": lg(L["SPX"], 60),
        "usdtry_20g": lg(L["USDTRY"], 20),
    }, index=g)
    o.index.name = "tarih"
    return o


def zskor(oz, min_gozlem=ISINMA):
    """Genişleyen z-skor: z[t] = (x[t] - ort(x[:t])) / std(x[:t]); ilk min_gozlem gözlemde NaN."""
    m = oz.expanding(min_periods=min_gozlem).mean()
    s = oz.expanding(min_periods=min_gozlem).std()
    return (oz - m) / s.where(s > 0)


def hedef_seviyeleri(panel, katalog):
    """Hedef seviyeleri hafta içi ızgarada (ileri doldurma yok). Sütun = HEDEFLER anahtarları."""
    g = izgara(panel)
    p = panel.reindex(g)
    usd = getiriler.usd_cevir(p, katalog, kodlar=["BIST100"]) if "BIST100" in p.columns else None
    cikti = {}
    for ad, (kod, tur, usdmi) in HEDEFLER.items():
        if kod not in p.columns:
            continue
        cikti[ad] = usd["BIST100"] if usdmi else p[kod].astype(float)
    return pd.DataFrame(cikti, index=g)


def ileri_getiriler(seviye, ufuk):
    """t -> t+ufuk iş günü ileri getiri: log (fiyat) ya da bp (US10Y). t ya da t+ufukta gözlem yoksa NaN."""
    c = {}
    for ad in seviye.columns:
        s = seviye[ad]
        if HEDEFLER[ad][1] == "bp":
            c[ad] = (s.shift(-ufuk) - s) * 100.0
        else:
            s = s.where(s > 0)
            c[ad] = np.log(s.shift(-ufuk) / s)
    return pd.DataFrame(c, index=seviye.index)


def analog_bul(z, t_poz, ufuk, k=VARSAYILAN_K, kolonlar=None, aralik=ARALIK):
    """t_poz konumundaki güne en yakın K bağımsız analog. Dönen: DataFrame(poz, uzaklik) uzaklığa göre sıralı.
    Adaylar: poz <= t_poz - (ufuk+5), seçili tüm özellikleri sonlu. Seçim açgözlü: seçilenin ±aralik'i dışlanır."""
    kolonlar = list(kolonlar or z.columns)
    zf = z[kolonlar].to_numpy(dtype=float)
    hedef = zf[t_poz]
    bos = pd.DataFrame({"poz": np.array([], dtype=int), "uzaklik": np.array([], dtype=float)})
    if not np.all(np.isfinite(hedef)):
        return bos
    son = t_poz - (ufuk + 5)
    if son < 0:
        return bos
    aday = zf[: son + 1]
    poz = np.flatnonzero(np.all(np.isfinite(aday), axis=1))
    if len(poz) == 0:
        return bos
    d = np.sqrt(((aday[poz] - hedef) ** 2).sum(axis=1))
    sira = np.argsort(d, kind="stable")
    dis = np.zeros(son + 1, dtype=bool)
    secilen, uz = [], []
    for i in sira:
        p = poz[i]
        if dis[p]:
            continue
        secilen.append(p)
        uz.append(d[i])
        dis[max(0, p - aralik): p + aralik + 1] = True
        if len(secilen) >= k:
            break
    return pd.DataFrame({"poz": np.array(secilen, dtype=int), "uzaklik": uz})


def aday_pozisyonlari(z, t_poz, ufuk, kolonlar=None):
    kolonlar = list(kolonlar or z.columns)
    son = t_poz - (ufuk + 5)
    if son < 0:
        return np.array([], dtype=int)
    zf = z[kolonlar].to_numpy(dtype=float)[: son + 1]
    return np.flatnonzero(np.all(np.isfinite(zf), axis=1))


def dagilim_ozeti(v):
    v = pd.Series(v).dropna().astype(float)
    n = len(v)
    if n == 0:
        return dict(n=0, medyan=np.nan, q25=np.nan, q75=np.nan, p10=np.nan, p90=np.nan, yukari=np.nan)
    q = v.quantile([.1, .25, .5, .75, .9])
    return dict(n=n, medyan=q[.5], q25=q[.25], q75=q[.75], p10=q[.1], p90=q[.9], yukari=float((v > 0).mean()))


def karsilastir(ileri_h, analog_poz, aday_poz):
    """Hedef başına analog (_a) ve koşulsuz (_t) özet; fark = analog medyanı - koşulsuz medyan."""
    satir = []
    ap = np.asarray(analog_poz, dtype=int)
    tp = np.asarray(aday_poz, dtype=int)
    for h in ileri_h.columns:
        arr = ileri_h[h].to_numpy()
        a = dagilim_ozeti(arr[ap])
        t = dagilim_ozeti(arr[tp])
        d = {"hedef": h}
        d.update({k + "_a": v for k, v in a.items()})
        d.update({k + "_t": v for k, v in t.items()})
        d["fark"] = a["medyan"] - t["medyan"]
        satir.append(d)
    return pd.DataFrame(satir)


def analiz(z, ileri_h, t_poz, ufuk, k=VARSAYILAN_K, kolonlar=None):
    """Tek çağrıda: analog listesi + karşılaştırma tablosu."""
    an = analog_bul(z, t_poz, ufuk, k, kolonlar)
    ad = aday_pozisyonlari(z, t_poz, ufuk, kolonlar)
    return an, karsilastir(ileri_h, an["poz"].to_numpy(dtype=int), ad)


# ---------------------------------------------------------------- walk-forward dürüstlük kontrolü
def walk_forward(z, ileri_h, ufuk=20, k=VARSAYILAN_K, baslangic="2016-01-01", kolonlar=None, min_analog=8):
    """Ayda bir tarih (ay başı ilk iş günü) için analogları yalnız o tarihe kadarki veriyle bul; analog medyanı,
    koşulsuz medyan ve sonradan gerçekleşen ileri getiriyi döndür. Satır = (tarih, hedef)."""
    idx = z.index
    ilk = idx.searchsorted(pd.Timestamp(baslangic))
    alt = idx[ilk:]
    aylar = pd.Series(alt, index=alt).groupby([alt.year, alt.month]).first()
    A = {h: ileri_h[h].to_numpy() for h in ileri_h.columns}
    satir = []
    for tarih in aylar:
        t = idx.get_loc(tarih)
        if t + ufuk >= len(idx):
            continue
        an = analog_bul(z, t, ufuk, k, kolonlar)
        if len(an) == 0:
            continue
        ad = aday_pozisyonlari(z, t, ufuk, kolonlar)
        ap = an["poz"].to_numpy(dtype=int)
        for h, arr in A.items():
            gercek = arr[t]
            if not np.isfinite(gercek):
                continue
            va = arr[ap]
            va = va[np.isfinite(va)]
            vt = arr[ad]
            vt = vt[np.isfinite(vt)]
            if len(va) < min_analog or len(vt) < 50:
                continue
            satir.append((tarih, h, float(np.median(va)), float(np.median(vt)), float(gercek), len(va)))
    return pd.DataFrame(satir, columns=["tarih", "hedef", "analog_medyan", "taban_medyan", "gerceklesen", "n_analog"])


def walk_forward_ozet(wf):
    """Hedef başına: n gözlem, yön isabeti (analog / koşulsuz medyan yönü / hep yukarı), Spearman, MAE karşılaştırması."""
    satir = []
    for h, d in wf.groupby("hedef", sort=False):
        d = d[d["gerceklesen"] != 0]
        n = len(d)
        if n < 12:
            satir.append(dict(hedef=h, n=n, yetersiz=True, avantaj=False))
            continue
        sg = np.sign(d["gerceklesen"])
        ya = float((np.sign(d["analog_medyan"]) == sg).mean())
        yt = float((np.sign(d["taban_medyan"]) == sg).mean())
        if d["analog_medyan"].nunique() > 1:
            rho, p = _st.spearmanr(d["analog_medyan"], d["gerceklesen"])
        else:
            rho, p = np.nan, np.nan
        mae_a = float((d["gerceklesen"] - d["analog_medyan"]).abs().mean())
        mae_t = float((d["gerceklesen"] - d["taban_medyan"]).abs().mean())
        av = bool(np.isfinite(rho) and rho > 0 and p < 0.05 and mae_a < mae_t and ya > yt)
        satir.append(dict(hedef=h, n=n, yetersiz=False, yon_analog=ya, yon_taban=yt, hep_yukari=float((sg > 0).mean()),
                          spearman=float(rho), spearman_p=float(p), mae_analog=mae_a, mae_taban=mae_t, avantaj=av))
    return pd.DataFrame(satir)


def walk_forward_yorum(ozet):
    """Önceden kayıtlı kural: bir hedefte 'avantaj' = Spearman>0 ve p<0.05 ve MAE analog<koşulsuz ve yön isabeti analog>koşulsuz.
    Hedeflerin en az üçte biri (en az 3; 10 hedefte 4) avantaj gösteriyorsa 'avantaj görünüyor (küçük örneklem)'; aksi halde 'görünmüyor'."""
    ok = ozet[~ozet["yetersiz"].astype(bool)] if len(ozet) else ozet
    if len(ok) == 0:
        return "Walk-forward için yeterli gözlem yok."
    nav = int(ok["avantaj"].sum())
    esik = max(3, int(np.ceil(len(ok) / 3)))
    if nav >= esik:
        return ("Bir avantaj görünüyor (ama küçük örneklem): %d/%d hedefte analog medyanı, koşulsuz medyandan hem yön hem hata "
                "açısından daha iyi. Aylık örnekler az ve hedefler birbiriyle ilişkili; kesin sonuç sayılmamalı." % (nav, len(ok)))
    return ("Koşulsuz ortalamaya göre anlamlı bir avantaj görünmüyor: %d/%d hedefte analog medyanı koşulsuz medyanı hem yön hem hata "
            "açısından geçiyor (eşik %d). Tek tek hedeflerdeki küçük üstünlükler çoklu test nedeniyle tesadüf olabilir."
            % (nav, len(ok), esik))


# ---------------------------------------------------------------- bugünün durumu
_FRAZ = {
    "vix": ("piyasa sakin sayılır", "orta bir gerginlik düzeyi", "piyasa tedirgin sayılır"),
    "dxy_60g": ("dolar son 3 ayda belirgin zayıfladı", "dolar yatay seyrediyor", "dolar son 3 ayda belirgin güçlendi"),
    "brent_60g": ("petrol son 3 ayda belirgin düştü", "petrol yatay seyrediyor", "petrol son 3 ayda belirgin yükseldi"),
    "us10y_60g": ("ABD 10y faizi son 3 ayda belirgin düştü", "faiz yatay", "ABD 10y faizi son 3 ayda belirgin yükseldi"),
    "egri": ("eğri tarihsel olarak görece düz (düz ya da ters eğri resesyon sinyali olarak izlenir)", "eğim orta", "eğri dik (normal ya da toparlanma dönemi)"),
    "spx_vol20": ("hisse piyasası sakin", "oynaklık orta", "hisse piyasası çalkantılı"),
    "spx_60g": ("S&P 500 son 3 ayda düştü", "S&P 500 yatay", "S&P 500 son 3 ayda belirgin yükseldi"),
    "usdtry_20g": ("kur son ayda geriledi (TL güçlendi)", "kur görece yatay", "TL son ayda dolar karşısında değer kaybetti"),
}


def _sozel(p):
    return ("çok düşük" if p < .10 else "düşük" if p < .30 else "orta" if p <= .70 else "yüksek" if p <= .90 else "çok yüksek")


def bugunun_durumu(oz, t_poz=None):
    """Her özellik için: değer, geçmiş persentil (t dahil, yalnız t'ye kadar), sözel okuma."""
    t_poz = len(oz) - 1 if t_poz is None else t_poz
    satir = []
    for c in oz.columns:
        gecmis = oz[c].iloc[: t_poz + 1].dropna()
        v = oz[c].iloc[t_poz]
        if not np.isfinite(v) or len(gecmis) == 0:
            satir.append(dict(ozellik=c, deger=np.nan, persentil=np.nan, okuma="veri yok"))
            continue
        p = float((gecmis <= v).mean())
        fr = _FRAZ[c][0 if p < .30 else 2 if p > .70 else 1]
        satir.append(dict(ozellik=c, deger=float(v), persentil=p, okuma="tarihsel olarak %s; %s" % (_sozel(p), fr)))
    return pd.DataFrame(satir)
