"""Makro Pano arayuzu: ortak yardimcilar (veri, onbellek, kenar cubugu, grafik ve sayfa iskeleti).
Analiz mantigi analiz paketindedir; burada yalnizca arayuz kodu vardir."""
import sqlite3
import sys
from zoneinfo import ZoneInfo
from collections import namedtuple
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analiz import ag, getiriler, korelasyon
from toplayici import db, oku
from toplayici import yapilandirma as Y

try:
    from pano import varlik_bilgi
except ImportError:
    import varlik_bilgi

NEDENSELLIK = ("Korelasyon nedensellik değildir. Ortak bir üçüncü etken (USD, risk iştahı) iki seriyi birlikte "
               "oynatabilir; ilişki sabit değildir, kriz ve rejim değişimlerinde bozulabilir.")
KAT_AD = {"kripto": "Kripto", "fx": "FX", "emtia": "Emtia", "borsa": "Borsa", "faiz": "Faiz", "vix": "VIX",
          "politika": "Politika faizi"}
KAT_RENK = {"kripto": "#f7931a", "fx": "#2a9d8f", "emtia": "#c9a227", "borsa": "#3b6fd4", "faiz": "#8e44ad",
            "vix": "#d62728", "politika": "#7f7f7f"}

Ayar = namedtuple("Ayar", "baz pencere yontem kategoriler dmg")


# ---------------------------------------------------------------- veri ve onbellek
def db_damga():
    """Veri tabanindaki son degisikligi gosteren ucuz anahtar (satir sayisi, son cekim zamani, toplam) - yalniz gunluk tablo.
    Saatlik nabiz yazimi onbellegi gecersiz kilmaz (agir yeniden hesaplama olmasin).
    Katalog okunurken dosyaya yazildigi icin dosya mtime'i kullanilmaz."""
    c = db.baglan_oku()
    try:
        a = c.execute("SELECT COUNT(*), MAX(cekim_zamani), ROUND(SUM(kapanis),4) FROM gunluk").fetchone()
    finally:
        c.close()
    return "|".join(str(x) for x in a)


@st.cache_data(show_spinner="Veri okunuyor...", max_entries=2)
def yukle(dmg):
    kat = oku.katalog()
    panel = oku.gunluk_panel(None)
    return kat, panel


def evren_kodlari(kat):
    """Korelasyon / ag / rejim / lead-lag evreni: v1, gunluk, kategori != politika."""
    m = kat["v1"] & (kat["frekans"] == "gunluk") & (kat["kategori"] != "politika")
    return list(kat.loc[m, "kod"])


@st.cache_data(show_spinner="Getiriler hesaplanıyor...")
def getiri_tum(dmg, baz):
    kat, panel = yukle(dmg)
    ev = evren_kodlari(kat)
    seviye = getiriler.usd_cevir(panel, kat, kodlar=ev) if baz == "USD" else panel[ev]
    return getiriler.getiri_hesapla(seviye, kat)


@st.cache_data(show_spinner=False)
def seviye_tum(dmg, baz):
    kat, panel = yukle(dmg)
    ev = evren_kodlari(kat)
    return getiriler.usd_cevir(panel, kat, kodlar=ev) if baz == "USD" else panel[ev]


@st.cache_data(show_spinner=False)
def haftalik_tum(dmg, baz):
    kat, _ = yukle(dmg)
    return getiriler.haftalik_getiriler(seviye_tum(dmg, baz), kat)


@st.cache_data(show_spinner=False)
def saglik_tablosu(dmg):
    return oku.saglik()


@st.cache_data(show_spinner=False)
def suphe_sayilari(dmg):
    c = db.baglan_oku()
    try:
        d = pd.read_sql("SELECT kod, SUM(suphe) AS suphe FROM gunluk GROUP BY kod", c)
    finally:
        c.close()
    return d.set_index("kod")["suphe"]


@st.cache_data(show_spinner=False)
def politika_olaylari(dmg):
    c = db.baglan_oku()
    try:
        d = pd.read_sql("SELECT kod, tarih, onceki, yeni, degisim FROM politika_olaylari ORDER BY tarih", c)
    finally:
        c.close()
    d["tarih"] = pd.to_datetime(d["tarih"])
    return d


@st.cache_data(show_spinner=False)
def son_hatalar(dmg, n=15):
    c = db.baglan_oku()
    try:
        return pd.read_sql("SELECT zaman_utc, kaynak, kod, hata FROM cekim_gunlugu WHERE sonuc='hata' "
                           "ORDER BY id DESC LIMIT %d" % n, c)
    finally:
        c.close()


# ---------------------------------------------------------------- kenar cubugu
def kenar_cubugu():
    """Genel kontroller (her sayfada). Dondurdugu Ayar sayfalara aktarilir."""
    dmg = db_damga()
    kat, _ = yukle(dmg)
    ev = kat[kat["kod"].isin(evren_kodlari(kat))]
    kategoriler = list(dict.fromkeys(ev["kategori"]))
    with st.sidebar:
        st.markdown("### Genel kontroller")
        baz = st.radio("Baz", ["USD", "Yerel"], key="ayar_baz", horizontal=True,
                       help="USD: yerel endeksler analiz.getiriler.usd_cevir ile USD'ye çevrilir. "
                            "Yerel: seri kendi para biriminde (gram altın TL bazında kalır).")
        pencere = st.radio("Pencere", [60, 250], index=1, key="ayar_pencere", horizontal=True,
                           format_func=lambda x: "%dg" % x)
        yontem_ad = st.radio("Korelasyon yöntemi", ["Spearman", "Pearson"], key="ayar_yontem", horizontal=True)
        secili = st.multiselect("Kategori filtresi", kategoriler, default=kategoriler, key="ayar_kat",
                                format_func=lambda k: KAT_AD.get(k, k))
        if not secili:
            secili = kategoriler
            st.caption("Hiç kategori seçilmediği için tümü kullanılıyor.")
        if st.button("Panoyu kapat", key="pano_kapat", help="Sunucuyu durdurur; yeniden açmak için masaüstündeki 'Makro Pano' kısayolu."):
            import subprocess
            subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), str(KOK / "pano_durdur.py"),
                              str(st.get_option("server.port"))], creationflags=0x08000000)
            st.stop()
        st.caption("Evren: v1, günlük, politika faizi dışı seriler. Politika faizleri ve aylık seriler yalnız "
                   "'Yavaş / Bağlam' ekranındadır.")
    return Ayar(baz, int(pencere), yontem_ad.lower(), tuple(secili), dmg)


def getiri(a):
    kat, _ = yukle(a.dmg)
    g = getiri_tum(a.dmg, a.baz)
    kt = kat.set_index("kod")["kategori"]
    return g[[c for c in g.columns if kt.get(c) in a.kategoriler]]


def kod_etiket(kat):
    ad = kat.set_index("kod")["ad"].to_dict()
    return lambda k: "%s - %s" % (k, ad.get(k, k))


# ---------------------------------------------------------------- zaman gosterimi
TR = ZoneInfo("Europe/Istanbul")


def zaman_tr(v):
    """'2026-10-17T10:10:32Z' -> '2026-10-17 10:10:32Z (TR 13:10:32)'. Yalniz gosterim; saklanan veri degismez."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return v
    try:
        t = pd.Timestamp(v)
    except (ValueError, TypeError):
        return v
    if pd.isna(t):
        return v
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return "%sZ (TR %s)" % (t.strftime("%Y-%m-%d %H:%M:%S"), t.astimezone(TR).strftime("%H:%M:%S"))


# ---------------------------------------------------------------- iskelet
def sayfa_basi(baslik, uyari_metni=None):
    st.title(baslik)
    saglik_seridi()
    if uyari_metni:
        st.warning(uyari_metni)


def saglik_seridi():
    try:
        s = saglik_tablosu(db_damga())
    except Exception as e:  # bozuk veritabani panoyu cokertmesin
        st.error("Veri sağlığı okunamadı: %s" % e)
        return
    gec = int((s["durum"] == "gecikmis").sum())
    hata = int((s["durum"] == "hata").sum())
    son = s["son_basarili_cekim"].dropna()
    son_txt = zaman_tr(son.max()) if len(son) else "bilinmiyor"
    txt = "Veri sağlığı - son başarılı çekim: %s | gecikmiş seri: %d | hatalı seri: %d | toplam v1 serisi: %d" % (
        son_txt, gec, hata, len(s))
    if hata:
        st.error(txt + " - ayrıntı için 'Genel Bakış ve Veri Sağlığı' ekranı.")
    elif gec:
        st.warning(txt)
    else:
        st.success(txt)


def sayfa_sonu(nasil_okunur):
    st.divider()
    with st.expander("Bu sayfayı nasıl okumalı"):
        st.markdown(nasil_okunur)
    st.caption(NEDENSELLIK)


# ---------------------------------------------------------------- grafikler
def sirala(corr):
    """Hiyerarsik kume sirasi; elenenler (yetersiz veri) sona eklenir, gizlenmez."""
    try:
        r = ag.hiyerarsik_kumeleme(corr)
        sira = list(r["sira"]) + list(r["elenenler"])
    except Exception:
        sira = list(corr.columns)
    sira += [c for c in corr.columns if c not in sira]
    return sira


def harita_yuksekligi(n):
    """Seri basina ~26 px + kenar bosluklari; 33 seri icin ~1000 px."""
    return int(max(520, 26 * n + 150))


def harita_bicim(fig, n, buyuk=False):
    """Eksen etiketleri buyuk, kalin ve koyu; hucre ici sayilar okunakli; uzun etiketler kesilmesin diye automargin.
    Kalinlik: tick metni <b> ile sarilir (Plotly eksen fontunda weight guvenilir degil)."""
    f = 16 if buyuk else 13
    zt = 13 if buyuk else (10 if n > 20 else 12)
    kodlar = None
    for tr in fig.data:
        if tr.x is not None and len(tr.x):
            kodlar = list(tr.x)
            break
    tf = dict(size=f, color="#111111", family="Arial, sans-serif")
    fig.update_xaxes(tickfont=tf, tickangle=90, automargin=True, showgrid=False, fixedrange=True)
    fig.update_yaxes(tickfont=tf, automargin=True, showgrid=False, fixedrange=True)
    fig.update_layout(dragmode=False, hovermode="closest")
    if kodlar:
        tt = ["<b>%s</b>" % k for k in kodlar]
        fig.update_xaxes(tickmode="array", tickvals=kodlar, ticktext=tt)
        fig.update_yaxes(tickmode="array", tickvals=kodlar, ticktext=tt)
    fig.data[-1].update(texttemplate="%{z:.2f}", textfont=dict(size=zt, color="#111111"))
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), font=dict(size=f))
    return fig


def isi_haritasi(corr, ntxt, sira, baslik, zmin=-1.0, zmax=1.0, yukseklik=None, fark=False):
    """corr: DataFrame; ntxt: ayni boyutta metin (hover'da gozlem sayisi). NaN hucreler gri kalir (gizlenmez)."""
    c = corr.reindex(index=sira, columns=sira)
    nt = ntxt.reindex(index=sira, columns=sira)
    gri = np.where(c.isna().to_numpy(), 1.0, np.nan)
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=gri, x=sira, y=sira, colorscale=[[0, "#bdbdbd"], [1, "#bdbdbd"]], showscale=False,
                             customdata=nt.to_numpy(),
                             hovertemplate="%{y} / %{x}<br>yetersiz veri, n=%{customdata}<extra></extra>"))
    fig.add_trace(go.Heatmap(z=c.to_numpy(dtype=float), x=sira, y=sira, zmin=zmin, zmax=zmax, zmid=0,
                             colorscale="RdBu", customdata=nt.to_numpy(),
                             colorbar=dict(thickness=14, len=0.6),
                             hovertemplate="%{y} / %{x}<br>" + ("fark" if fark else "r") +
                                           "=%{z:.2f}<br>n=%{customdata}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title=dict(text=baslik, font=dict(size=16)),
                      height=yukseklik or harita_yuksekligi(len(sira)))
    return harita_bicim(fig, len(sira))


VURGU_RENK = "#d62728"
HARITA_CONFIG = {"displayModeBar": False, "scrollZoom": False, "staticPlot": False}


def vurgula(fig, kod):
    """Secili varligin satirini ve sutununu cerceveler, o eksen etiketlerini renklendirir (figur kopyalanir)."""
    f = go.Figure(fig)
    kodlar = list(f.data[0].x)
    if kod not in kodlar:
        return f
    i = kodlar.index(kod)
    n = len(kodlar)
    ln = dict(color=VURGU_RENK, width=3)
    f.add_shape(type="rect", xref="x", yref="y", x0=-0.5, x1=n - 0.5, y0=i - 0.5, y1=i + 0.5, line=ln, layer="above")
    f.add_shape(type="rect", xref="x", yref="y", x0=i - 0.5, x1=i + 0.5, y0=-0.5, y1=n - 0.5,
                line=dict(color=VURGU_RENK, width=2, dash="dot"), layer="above")
    tt = ["<b><span style='color:%s'>%s</span></b>" % (VURGU_RENK, k) if k == kod else "<b>%s</b>" % k for k in kodlar]
    f.update_xaxes(ticktext=tt)
    f.update_yaxes(ticktext=tt)
    return f


def _secili_kod(key, kodlar):
    """Onceki rerun'dan gelen tiklama secimi -> satir varligi. Secim yoksa (ayni hucreye tekrar tiklama dahil) None."""
    try:
        pts = st.session_state["harita_" + key].selection.points
    except (KeyError, AttributeError, TypeError):
        return None
    for p in pts or []:
        y = p.get("y") if isinstance(p, dict) else None
        if y in kodlar:
            return y
    return None


def _secili_hucre(key, kodlar):
    """Secili hucrenin (satir, sutun) varliklari; yoksa (None, None)."""
    try:
        pts = st.session_state["harita_" + key].selection.points
    except (KeyError, AttributeError, TypeError):
        return None, None
    for p in pts or []:
        if isinstance(p, dict) and p.get("y") in kodlar:
            return p.get("y"), (p.get("x") if p.get("x") in kodlar else None)
    return None, None


def bilgi_dialog_ac(kod):
    """Dialog'u (baslik = varligin tam adi, genis) acar; icerik tek bir markdown blogu."""
    ad = varlik_bilgi.BILGI.get(kod, {}).get("ad", str(kod))

    def _ic():
        st.markdown(varlik_bilgi.bilgi_karti(kod))
    st.dialog(ad, width="large")(_ic)()


def bilgi_butonu(kod, key):
    """'i {kod} nedir?' butonu; basinca bilgi karti dialog'u acilir."""
    if st.button("ℹ️ %s nedir?" % kod, key=key):
        bilgi_dialog_ac(kod)


def harita_goster(fig, key):
    """Haritayi tam genislikte, sabit yukseklikte, zoom/pan/arac cubugu olmadan cizer.
    Tam ekran: Streamlit'in kendi eleman tam ekran dugmesi (dialog yok; sayfa sicramaz).
    Vurgulama: hucreye tiklayinca o hucrenin satir varligi kirmizi cerceveyle vurgulanir (sutunu noktali cerceve);
    ayni hucreye tekrar tiklamak ya da bos alana tiklamak vurguyu kaldirir. Plotly isi haritasi secimi desteklemedigi icin
    her hucrenin ustunde gorunmez bir scatter noktasi katmani vardir; secim yalniz bu katmandan gelir."""
    kodlar = list(fig.data[0].x) if fig.data and fig.data[0].x is not None else []
    # Streamlit, figur (vurgu) degisince widget'i sifirladigi icin secim bir sonraki rerun'da bos gelir; vurguyu kendimiz tutariz.
    yeni = _secili_hucre(key, kodlar)
    onc = st.session_state.get("hl_" + key)
    if yeni[0]:
        onc = None if yeni == onc else yeni  # ayni hucreye tekrar tiklama vurguyu kaldirir
        st.session_state["hl_" + key] = onc
    v = onc[0] if onc else None
    f = vurgula(fig, v) if v else go.Figure(fig)
    xs = [x for _ in kodlar for x in kodlar]
    ys = [y for y in kodlar for _ in kodlar]
    gizli = dict(size=14, color="rgba(0,0,0,0)")
    # Hover'i da bu katman verir (isi haritasinin hover'i kapatilir): tiklamanin secime donusmesi icin sart.
    hm = fig.data[-1]
    z = np.asarray(hm.z, dtype=float).ravel()
    nn = np.asarray(hm.customdata).ravel()
    etiket = "fark" if "fark" in (hm.hovertemplate or "") else "r"
    txt = ["%s / %s<br>yetersiz veri, n=%s" % (y, x, n) if np.isnan(v) else "%s / %s<br>%s=%.2f<br>n=%s" % (y, x, etiket, v, n)
           for (y, x, v, n) in zip(ys, xs, z, nn)]
    for tr in f.data:
        tr.hoverinfo = "skip"
        tr.hovertemplate = None
    f.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=gizli, selected=dict(marker=gizli),
                           unselected=dict(marker=gizli), hovertext=txt, hoverinfo="text", showlegend=False, name=""))
    f.update_layout(clickmode="event+select", dragmode=False)
    st.plotly_chart(f, width="stretch", key="harita_" + key, config=HARITA_CONFIG,
                    on_select="rerun", selection_mode="points")
    # Bilgi butonlari: yer her zaman ayni (sabit sayida satir), vurgu yoksa pasif; sayfa sicramaz.
    r, c = onc if onc else (None, None)
    if r:
        b1, b2, _ = st.columns([1, 1, 3])
        with b1:
            bilgi_butonu(r, "bilgi_" + key + "_satir")
        with b2:
            if c and c != r:
                bilgi_butonu(c, "bilgi_" + key + "_sutun")


def goster(fig):
    st.plotly_chart(fig, width="stretch")


def tablo(df, **kw):
    st.dataframe(df, width="stretch", **kw)


def ortak_n(g):
    return korelasyon.ortak_gozlem(g)
