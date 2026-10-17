import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import saglik_yardimci  # noqa: E402
from toplayici import yapilandirma as Y  # noqa: E402

ortak.sayfa_basi("0 Genel Bakış ve Veri Sağlığı")
ortak.kenar_cubugu()  # genel kontroller bu ekranda kullanılmaz ama tutarlılık için görünür

dmg = ortak.db_damga()
kat, panel = ortak.yukle(dmg)
sag = ortak.saglik_tablosu(dmg).set_index("kod")

# ---- kontroller
c1, c2 = st.columns([1, 3])
with c1:
    esik = st.number_input("Staleness threshold (iş günü)", 1, 30, 3, help="Günlük serilerde bu kadar iş gününden eski son tarih uyarı üretir.")
with c2:
    st.write("")
    if st.button("Verileri güncelle", help="Makro-pano kökünden `python -m toplayici gunluk` çalıştırır."):
        with st.spinner("Güncelleniyor (birkaç dakika sürebilir)..."):
            try:
                env = dict(__import__("os").environ, PYTHONIOENCODING="utf-8")
                r = subprocess.run([sys.executable, "-m", "toplayici", "gunluk"], cwd=str(ortak.KOK),
                                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=1500, env=env)
                (st.success if r.returncode == 0 else st.error)("Çıkış kodu: %d" % r.returncode)
                st.code(((r.stdout or "") + ("\n--- stderr ---\n" + r.stderr if r.stderr else ""))[-6000:] or "(çıktı yok)")
                st.cache_data.clear()
                st.info("Önbellek temizlendi; sayfa yeni veriyle yeniden hesaplanır.")
            except subprocess.TimeoutExpired:
                st.error("Güncelleme zaman aşımına uğradı (25 dk).")
            except Exception as e:
                st.error("Güncelleme başlatılamadı: %s" % e)

# ---- seri tablosu
bugun = pd.Timestamp.now().normalize()
sh = saglik_yardimci.seri_sagligi(panel[[c for c in panel.columns]], kat, bugun=bugun,
                                  bayat_esik_is_gunu=int(esik)).set_index("kod")
suphe = ortak.suphe_sayilari(dmg)
ktl = kat.set_index("kod")


def degisimler(s, birim, frek):
    s = s.dropna()
    if len(s) < 2:
        return (np.nan,) * 3
    son = s.index[-1]

    def ref(gun):
        r = s[s.index <= son - pd.Timedelta(days=gun)]
        return r.iloc[-1] if len(r) else np.nan

    def fark(r):
        if not np.isfinite(r):
            return np.nan
        return (s.iloc[-1] - r) * 100.0 if birim == "faiz_yuzde" else (s.iloc[-1] / r - 1.0) * 100.0

    d1 = fark(s.iloc[-2]) if frek == "gunluk" else np.nan
    d7 = fark(ref(7)) if frek == "gunluk" else np.nan
    return d1, d7, fark(ref(30))


satir = []
for kod in panel.columns:
    k = ktl.loc[kod]
    s = panel[kod].dropna()
    d1, d7, d30 = degisimler(panel[kod], k["birim"], k["frekans"])
    h = sag.loc[kod] if kod in sag.index else None
    eski = (sh.loc[kod, "bayatlik_is_gunu"] > esik) if (k["frekans"] == "gunluk" and kod in sh.index) else False
    satir.append({
        "kod": kod, "ad": k["ad"], "kategori": ortak.KAT_AD.get(k["kategori"], k["kategori"]),
        "son değer": s.iloc[-1] if len(s) else np.nan,
        "1g": d1, "1h": d7, "1a": d30, "birim": "bp" if k["birim"] == "faiz_yuzde" else "%",
        "son tarih": s.index[-1].date() if len(s) else None,
        "staleness (iş günü)": sh.loc[kod, "bayatlik_is_gunu"] if kod in sh.index else np.nan,
        "durum": h["durum"] if h is not None else "?",
        "eşik aşıldı": "EVET" if eski else "",
        "şüpheli satır": int(suphe.get(kod, 0)),
        "gözlem": len(s),
        "eksik iş günü": sh.loc[kod, "eksik_is_gunu"] if kod in sh.index else np.nan,
        "son başarılı çekim": ortak.zaman_tr(h["son_basarili_cekim"]) if h is not None and isinstance(h["son_basarili_cekim"], str) else None,
        "son hata": str(h["son_hata"])[:120] if h is not None and isinstance(h["son_hata"], str) else "",
    })
tab = pd.DataFrame(satir)

# ---- uyarılar
eski = tab[tab["eşik aşıldı"] == "EVET"]
if len(eski):
    st.warning("Veri yaşı eşiği (%d iş günü) aşan %d günlük seri var: %s. 'Verileri güncelle' düğmesini deneyin." % (
        esik, len(eski), ", ".join(eski["kod"])))
else:
    st.success("Tüm günlük seriler %d iş günü eşiği içinde." % esik)
if (tab["durum"] == "hata").any():
    st.error("Hatalı seriler (son çekim başarısız ya da veri yok): " + ", ".join(tab.loc[tab["durum"] == "hata", "kod"]))

m1, m2, m3, m4 = st.columns(4)
m1.metric("v1 serisi", len(tab))
m2.metric("gecikmiş", int((tab["durum"] == "gecikmis").sum()))
m3.metric("hata", int((tab["durum"] == "hata").sum()))
m4.metric("şüpheli satır (toplam)", int(tab["şüpheli satır"].sum()))


def renk(v):
    return {"ok": "background-color:#2e7d3233", "gecikmis": "background-color:#f9a82566",
            "hata": "background-color:#d32f2f66"}.get(v, "")


sty = (tab.style.map(renk, subset=["durum"])
       .format({"son değer": "{:,.4g}", "1g": "{:+.2f}", "1h": "{:+.2f}", "1a": "{:+.2f}",
                "staleness (iş günü)": "{:.0f}", "eksik iş günü": "{:.0f}"}, na_rep="-"))
st.subheader("Seri bazında durum")
st.caption("1g / 1h / 1a: son gözlem ile bir önceki gözlem / 7 gün / 30 gün önceki gözlem arasındaki değişim "
           "(fiyatlarda %, faizlerde bp). Aylık ve politika serilerinde 1g/1h anlamsızdır, boş bırakılır. "
           "'Eksik iş günü' tatilleri de içerir (kesin ayrım yok); kripto 7/24 olduğundan hafta sonu zaten atlanır.")
# Satir secimi: Styler ile on_select="rerun" calisir (renk/format korunur); secilen satirin kodu tab'dan okunur.
ev = st.dataframe(sty, hide_index=True, height=560, width="stretch", key="s0_seri_tablosu",
                  on_select="rerun", selection_mode="single-row")
try:
    sec = list(ev.selection.rows)
except (AttributeError, TypeError):
    sec = []
if sec and 0 <= sec[0] < len(tab):
    ortak.bilgi_butonu(tab["kod"].iloc[sec[0]], "s0_bilgi")
else:
    st.caption("Bir satıra tıklayın: varlığın bilgi kartı butonu burada çıkar.")

# ---- kaynak durumu
st.subheader("Kaynak durumu")
kay = ktl["kaynak"]
rows = []
for kaynak in ["yahoo", "binance", "fred", "bis", "turetilmis"]:
    kodlar = [k for k in tab["kod"] if kay.get(k) == kaynak]
    if not kodlar:
        continue
    t = tab[tab["kod"].isin(kodlar)]
    rows.append({"kaynak": kaynak, "seri": len(t), "ok": int((t["durum"] == "ok").sum()),
                 "gecikmiş": int((t["durum"] == "gecikmis").sum()), "hata": int((t["durum"] == "hata").sum()),
                 "son başarılı çekim": t["son başarılı çekim"].dropna().max() if t["son başarılı çekim"].notna().any() else None})
rows.append({"kaynak": "evds", "seri": 0, "ok": 0, "gecikmiş": 0, "hata": 0,
             "son başarılı çekim": "anahtar tanımlı" if Y.EVDS_KEY else "kurulmadı (v2)"})
ortak.tablo(pd.DataFrame(rows), hide_index=True)

hat = ortak.son_hatalar(dmg).copy()
hat["zaman_utc"] = hat["zaman_utc"].map(ortak.zaman_tr)
with st.expander("Son çekim hataları (günlükten, en yeni 15)"):
    if len(hat):
        ortak.tablo(hat, hide_index=True)
    else:
        st.write("Kayıtlı hata yok.")

st.subheader("Veri yok olan kalemler")
st.markdown("- Brezilya / Hindistan / Çin 10y tahvil faizi: ücretsiz güvenilir kaynak yok (veri yok).\n"
            "- Türkiye 2y / 10y tahvil ve TL mevduat faizi: EVDS gerektirir; EVDS kurulmadı, v2'de doğrulanacak.\n"
            "- USDTRY resmi (TCMB) kuru: EVDS sonrası.")

st.subheader("Metodoloji notları")
st.markdown("- **Shanghai** ve **JSE** serilerinin veri kalitesi şüphelidir (boşluk / gecikme); proxy ya da zayıf kaynak.\n"
            "- **Hindistan repo** (BIS) gecikmelidir; son gözlem eskidir.\n"
            "- Gram altın ve altcoin sepeti türetilmiş serilerdir. Yahoo FX tarihi ve vadeli roll sıçramaları şüpheli satır olarak işaretlenir, silinmez.")

ortak.sayfa_sonu("Önce üstteki şeride ve 'eşik aşıldı' sütununa bakın: stale (güncel olmayan) ya da hatalı bir seri, o seriyi içeren tüm "
                 "korelasyonları yanıltabilir. Şüpheli satır sayısı tek günde ±%50'den büyük hareketleri sayar; silinmez, "
                 "ama sonuçları etkileyebilir.")
