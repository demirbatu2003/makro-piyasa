"""Makro Pano - Streamlit giris noktasi. Calistir: python -m streamlit run pano\app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(page_title="Makro Pano", layout="wide")

S = "sayfalar/"
sayfalar = [
    st.Page(S + "s0_genel_bakis.py", title="0 Genel Bakış ve Veri Sağlığı", url_path="genel-bakis", default=True),
    st.Page(S + "s1_korelasyon.py", title="1 Korelasyon Haritası", url_path="korelasyon"),
    st.Page(S + "s2_ikili.py", title="2 İkili İlişki", url_path="ikili"),
    st.Page(S + "s3_ag.py", title="3 Ağ ve Kümeler", url_path="ag"),
    st.Page(S + "s4_rejim.py", title="4 Rejim ve Beta", url_path="rejim"),
    st.Page(S + "s5_olay.py", title="5 Büyük Hareket (Event Study)", url_path="olay"),
    st.Page(S + "s6_leadlag.py", title="6 Lead-Lag", url_path="leadlag"),
    st.Page(S + "s7_nabiz.py", title="7 Piyasa Nabzı", url_path="nabiz"),
    st.Page(S + "s8_yavas.py", title="8 Yavaş / Bağlam", url_path="yavas"),
    st.Page(S + "s9_kavramlar.py", title="9 Kavramlar", url_path="kavramlar"),
    st.Page(S + "s10_benzer_gunler.py", title="10 Benzer Günler", url_path="benzer"),
    st.Page(S + "s11_beklenti.py", title="11 Koşullu Beklenti ve Şoklar", url_path="beklenti"),
    st.Page(S + "s12_makas.py", title="12 İkili Makas ve Göreli Değer", url_path="makas"),
]
# Özel sayfa: dosya yalnız bu bilgisayarda var (.gitignore); klonlanan sürümde yoksa atlanır.
if (Path(__file__).resolve().parent / "sayfalar" / "s13_stratejiler.py").exists():
    sayfalar.append(st.Page(S + "s13_stratejiler.py", title="13 Stratejiler", url_path="stratejiler"))
st.navigation(sayfalar).run()
