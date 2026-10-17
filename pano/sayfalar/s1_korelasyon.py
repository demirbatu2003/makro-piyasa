import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from analiz import iliski, korelasyon  # noqa: E402


@st.cache_data(show_spinner="Korelasyon matrisleri hesaplanıyor...")
def karsilastir(dmg, baz, kategoriler, pencere, geri, yontem):
    g = ortak.getiri(ortak.Ayar(baz, pencere, yontem, kategoriler, dmg))
    return korelasyon.iki_nokta_karsilastirma(g, pencere=pencere, geri=geri, yontem=yontem)


@st.cache_data(show_spinner="Kısmi korelasyon matrisi hesaplanıyor...")
def kismi_matris(dmg, baz, kategoriler, pencere, yontem, kontrol):
    g = ortak.getiri(ortak.Ayar(baz, pencere, yontem, kategoriler, dmg))
    g = g.iloc[-pencere:]
    return iliski.kismi_korelasyon_matrisi(g, kontrol, yontem=yontem, min_gozlem=korelasyon.min_gozlem_varsayilan(pencere))


ortak.sayfa_basi("1 Korelasyon Haritası",
                 "465 çiftten bir kısmı yalnızca şans eseri güçlü görünür. Kısa pencere (60g) gürültülüdür; 250g ile "
                 "birlikte okuyun. Korelasyon nedensellik değildir.")
a = ortak.kenar_cubugu()
g = ortak.getiri(a)
if len(g) < 400:
    st.error("Yeterli getiri verisi yok.")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    varsayilan = g.index[-251].date()
    tarih = st.date_input("Karşılaştırma tarihi (varsayılan: 250 işlem günü önce)", varsayilan,
                          min_value=g.index[300].date(), max_value=g.index[-2].date())
with c2:
    sadece_anlamli = st.checkbox("Fark matrisinde yalnız istatistiksel olarak ayırt edilebilir değişimleri göster "
                                 "(p<0,05, çoklu test düzeltmesiz)", value=False)
geri = max(int((g.index > pd.Timestamp(tarih)).sum()), 1)
st.caption("Seçili baz: %s | yöntem: %s | evren: %d seri | 'Şimdi' = %s'e biten pencere, 'önce' = %d işlem günü önce biten "
           "aynı uzunlukta pencere. Minimum ortak gözlem: 60g için 40, 250g için 150; altı gri." % (
               a.baz, a.yontem.capitalize(), g.shape[1], g.index[-1].date(), geri))

pencereler = [a.pencere] + [p for p in (60, 250) if p != a.pencere]
sonuclar = {p: karsilastir(a.dmg, a.baz, a.kategoriler, p, geri, a.yontem) for p in pencereler}

tab_ana, tab_kismi = st.tabs(["Korelasyon haritaları", "Kısmi korelasyon matrisi"])
with tab_ana:
    # ---- tek sayı özeti
    st.subheader("Ortalama ikili korelasyon")
    cols = st.columns(len(pencereler))
    for col, p in zip(cols, sorted(pencereler)):
        r = sonuclar[p]
        s, o = korelasyon.ortalama_ikili_korelasyon(r["simdi"]), korelasyon.ortalama_ikili_korelasyon(r["onceki"])
        col.metric("%dg pencere" % p, "%.3f" % s, "%+.3f (önceki: %.3f)" % (s - o, o), delta_color="off")
        nn = r["n_simdi"].to_numpy()
        col.caption("hücre başına ortak gözlem (medyan): %d" % int(np.median(nn[np.triu_indices_from(nn, 1)])))

    for p in pencereler:
        r = sonuclar[p]
        st.subheader("%dg pencere" % p)
        sira = ortak.sirala(r["simdi"])  # hiyerarşik kümeleme sırası ('şimdi' matrisinden)
        fark = r["fark"]
        if sadece_anlamli:
            fark = fark.where(r["fark_p"] < 0.05)
        ns = r["n_simdi"].astype(str)
        no = r["n_onceki"].astype(str)
        t1, t2, t3 = st.tabs(["Şimdi", "Önce", "Fark (şimdi - önce)"])
        with t1:
            ortak.harita_goster(ortak.isi_haritasi(r["simdi"], ns, sira, "Şimdi (%s)" % r["simdi_bitis"].date()), "s1_simdi_%d" % p)
        with t2:
            ortak.harita_goster(ortak.isi_haritasi(r["onceki"], no, sira, "Önce (%s)" % r["onceki_bitis"].date()), "s1_once_%d" % p)
        with t3:
            ortak.harita_goster(ortak.isi_haritasi(fark, ns + " / " + no, sira, "Fark (şimdi - önce)", zmin=-0.8, zmax=0.8,
                                                   fark=True), "s1_fark_%d" % p)
        gri = int(r["simdi"].isna().to_numpy().sum())
        st.caption("Şimdi matrisinde gri (yetersiz gözlem) hücre: %d / %d. Gri hücreler gizlenmez; üzerine gelince ortak gözlem sayısı görünür. "
                   "Fark hücresinde hover 'n şimdi / n önce' gösterir." % (gri, r["simdi"].size))


with tab_kismi:
    st.markdown("Seçilen **kontrol** varlığın etkisi her varlıktan çıkarıldıktan sonra (OLS artıkları) kalan ilişki. "
                "Hücre = iki varlığın, kontrolün hareketlerinden arındırılmış korelasyonu. Son %dg penceresi, %s." % (a.pencere, a.yontem.capitalize()))
    kod_list = list(g.columns)
    kontrol = st.selectbox("Kontrol varlık", kod_list, index=kod_list.index("DXY") if "DXY" in kod_list else 0,
                           format_func=ortak.kod_etiket(ortak.yukle(a.dmg)[0]), key="s1_kismi_kontrol")
    kc, kn = kismi_matris(a.dmg, a.baz, a.kategoriler, a.pencere, a.yontem, kontrol)
    ksira = ortak.sirala(kc)
    ortak.harita_goster(ortak.isi_haritasi(kc, kn.astype(str), ksira, "Kısmi korelasyon (kontrol: %s, son %dg)" % (kontrol, a.pencere)),
                        "s1_kismi_%d" % a.pencere)
    st.caption("Kontrol varlık matriste yer almaz. Gri hücre: kontrolle ortak yeterli gözlem yok. Kontrole bağlı ortak hareket çıkarıldığı için "
               "ham haritadaki mavi bloklar sönüyorsa o ilişki büyük ölçüde kontrolden (ör. dolar) gelir.")

st.info("Metodoloji: log-getiri (faizlerde bp değişim); çiftler tam gözlem (pairwise); ~465 çiftte %5 düzeyinde ~23 şans eseri "
        "bulgu beklenir. Bu bir 'keşif listesi' değil haritadır. Satır/sütun sırası hiyerarşik kümelemeden gelir.")
ortak.sayfa_sonu("Mavi = birlikte hareket (pozitif), kırmızı = ters yönde (negatif), gri = yeterli ortak gözlem yok. "
                 "'Şimdi' sekmesi bugünkü, 'Önce' sekmesi karşılaştırma tarihindeki ilişkiyi, 'Fark' sekmesi aradaki değişimi gösterir. Yakın renk blokları "
                 "kümeleri ifade eder. 60g ve 250g'yi birlikte okuyun; 60g'de tek tek hücreler gürültülüdür.")
