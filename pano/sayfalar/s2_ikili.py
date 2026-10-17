import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ortak  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from analiz import iliski, korelasyon, rejim  # noqa: E402


@st.cache_data(show_spinner="Rolling korelasyon hesaplanıyor...")
def rolling(dmg, baz, a, b, pencere, yontem):
    g = ortak.getiri_tum(dmg, baz)
    return korelasyon.ikili_rolling(g, a, b, pencere=pencere, yontem=yontem)


@st.cache_data(show_spinner=False)
def rolling_b(dmg, baz, x, y, pencere):
    g = ortak.getiri_tum(dmg, baz)
    return iliski.rolling_beta(g, x, y, pencere=pencere)


HAZIR = {"Son 1 ay": pd.DateOffset(months=1), "Son 3 ay": pd.DateOffset(months=3),
         "Son 1 yıl": pd.DateOffset(years=1), "Son 3 yıl": pd.DateOffset(years=3)}


def gun_araliklari(maske):
    """Ardışık True günlerinin (başlangıç, bitiş) listesi."""
    out, bas, onceki = [], None, None
    for t, v in maske.items():
        if v and bas is None:
            bas = t
        if not v and bas is not None:
            out.append((bas, onceki))
            bas = None
        onceki = t
    if bas is not None:
        out.append((bas, onceki))
    return out


ortak.sayfa_basi("2 İkili İlişki",
                 "Rolling korelasyon örtüşen pencerelerle hesaplanır; yan yana duran noktalar bağımsız değildir. Bant yaklaşıktır.")
a = ortak.kenar_cubugu()
kat, panel = ortak.yukle(a.dmg)
ev = ortak.evren_kodlari(kat)
et = ortak.kod_etiket(kat)

c1, c2 = st.columns(2)
with c1:
    x = st.selectbox("Varlık A", ev, index=ev.index("BTC"), format_func=et)
with c2:
    y = st.selectbox("Varlık B", ev, index=ev.index("NASDAQ"), format_func=et)
if x == y:
    st.info("Farklı iki varlık seçin.")
    st.stop()

g = ortak.getiri_tum(a.dmg, a.baz)
ortak_idx = g[[x, y]].dropna().index
if len(ortak_idx) < 100:
    st.warning("Bu çift için ortak gözlem çok az (n=%d)." % len(ortak_idx))
    st.stop()
bas_def, bit_def = ortak_idx[0].date(), ortak_idx[-1].date()
st.markdown("#### Tarih aralığı")
sec = st.radio("Hazır aralık", list(HAZIR) + ["Tümü", "Özel"], index=4, horizontal=True, key="s2_aralik",
               help="Seçilen aralık hem grafikleri hem aşağıdaki 'seçili aralığın tamamı' istatistiklerini belirler.")
if sec == "Özel":
    aralik = st.date_input("Özel aralık (başlangıç - bitiş)", (bas_def, bit_def), min_value=bas_def, max_value=bit_def, key="s2_ozel")
    bas, bit = (pd.Timestamp(aralik[0]), pd.Timestamp(aralik[1])) if len(aralik) == 2 else (pd.Timestamp(bas_def), pd.Timestamp(bit_def))
elif sec == "Tümü":
    bas, bit = pd.Timestamp(bas_def), pd.Timestamp(bit_def)
else:
    bit = pd.Timestamp(bit_def)
    bas = max(bit - HAZIR[sec], pd.Timestamp(bas_def))
st.caption("Seçili aralık: %s - %s" % (bas.date(), bit.date()))

oc1, oc2 = st.columns([1, 2])
with oc1:
    rpen = st.selectbox("Rolling pencere (iş günü)", [20, 60, 120, 250], index=[20, 60, 120, 250].index(a.pencere), key="s2_rpen",
                        help="Rolling beta grafiğinin penceresi; 20/120 seçilirse korelasyon grafiğine de eklenir.")
with oc2:
    kontrol_secenek = [k for k in ev if k not in (x, y)]
    kontroller = st.multiselect("Kontrol değişkenleri (kısmi korelasyon için)", kontrol_secenek, default=[], key="s2_kontrol",
                                format_func=et, help="Boşsa kısmi korelasyon hesaplanmaz. Öneri: DXY (dolar), SPX (risk iştahı).")
    st.caption("Öneri: DXY, SPX. Seçilen değişkenlerin etkisi çıkarıldıktan sonra A ile B arasında ne kaldığına bakılır.")

r60 = rolling(a.dmg, a.baz, x, y, 60, a.yontem)
r250 = rolling(a.dmg, a.baz, x, y, 250, a.yontem)
ekstra = rolling(a.dmg, a.baz, x, y, rpen, a.yontem) if rpen not in (60, 250) else None
sl = lambda d: d.loc[bas:bit]  # noqa: E731

# VIX yüksek rejim gölgesi
vix = panel["VIX"].reindex(g.index)
gergin = (rejim.vix_rejimi(vix) == "gergin")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.06,
                    subplot_titles=("Rolling korelasyon (%s)" % a.yontem.capitalize(),
                                    "Normalize seviye (ilk ortak gün = 100, %s bazı)" % a.baz))
seri_listesi = [("60g", r60, "#d95f02", "rgba(217,95,2,0.15)"), ("250g", r250, "#1b5fb5", "rgba(27,95,181,0.15)")]
if ekstra is not None:
    seri_listesi.append(("%dg" % rpen, ekstra, "#2a9d8f", "rgba(42,157,143,0.12)"))
for ad, r, renk, dolgu in seri_listesi:
    d = sl(r)
    fig.add_trace(go.Scatter(x=d.index, y=d["ust"], line=dict(width=0), showlegend=False, hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d["alt"], fill="tonexty", fillcolor=dolgu, line=dict(width=0),
                             showlegend=False, hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d["korelasyon"], name="%s rolling" % ad, line=dict(color=renk, width=1.6),
                             customdata=d["n"], hovertemplate="%{x|%Y-%m-%d}<br>r=%{y:.2f}<br>n=%{customdata}<extra>" + ad + "</extra>"),
                  row=1, col=1)
fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)
for s, e in gun_araliklari(gergin.loc[bas:bit]):
    fig.add_vrect(x0=s, x1=e, fillcolor="rgba(200,30,30,0.10)", line_width=0, row=1, col=1)

lv = ortak.seviye_tum(a.dmg, a.baz)[[x, y]].loc[bas:bit].dropna()
for kod, renk in [(x, "#2a9d8f"), (y, "#8e44ad")]:
    if len(lv):
        fig.add_trace(go.Scatter(x=lv.index, y=100 * lv[kod] / lv[kod].iloc[0], name=kod, line=dict(color=renk, width=1.3)),
                      row=2, col=1)
fig.update_yaxes(range=[-1, 1], row=1, col=1)
fig.update_layout(height=700, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=1.08))
ortak.goster(fig)
st.caption("Kırmızı gölge: VIX > 25 (gergin rejim, sabit eşik). Açık renkli bant: Fisher z yaklaşık %95 aralığı "
           "(örtüşen pencereler bağımsız gözlem varsayar; gerçek belirsizlik daha geniştir). Bant ve noktaların yanındaki n hover'da görünür.")

# beta ve özet sayılar
from analiz.rejim import beta_tablosu  # noqa: E402

gs = g.loc[bas:bit, [x, y]]
bt = beta_tablosu(gs, x, pencere=a.pencere)
bt_tum = beta_tablosu(gs, x)
son = (r60 if a.pencere == 60 else r250).dropna(subset=["korelasyon"]).tail(1)
m1, m2, m3, m4 = st.columns(4)
if len(son):
    m1.metric("Son %dg korelasyon" % a.pencere, "%.2f" % son["korelasyon"].iloc[0], "n=%d" % son["n"].iloc[0], delta_color="off")
else:
    m1.metric("Son %dg korelasyon" % a.pencere, "yetersiz veri")
b = bt.loc[y] if y in bt.index else None
m2.metric("Beta (%s ~ %s), son %dg" % (y, x, a.pencere), "-" if b is None or not np.isfinite(b["beta"]) else "%.2f" % b["beta"],
          "" if b is None else "se %.2f, n=%d" % (b["se"], b["n"]), delta_color="off")
b2 = bt_tum.loc[y]
m3.metric("Beta, seçili aralığın tamamı", "-" if not np.isfinite(b2["beta"]) else "%.2f" % b2["beta"],
          "se %.2f, n=%d" % (b2["se"], b2["n"]) if np.isfinite(b2["se"]) else "", delta_color="off")
m4.metric("Ortak gözlem (aralık)", int(len(gs.dropna())))
st.caption("Beta: %s %%1 hareket ederse %s ortalama beta kadar %% hareket eder (faiz serileri bp birimindedir). "
           "Yerel baz: iki seri farklı para birimindeyse (ör. BIST100 TL) sonuç kur etkisini de içerir." % (x, y))


# ---- seçili aralığın tamamı için tek korelasyon
st.subheader("Seçili aralığın tamamı için tek korelasyon")
oz = iliski.aralik_ozeti(g, x, y, bas, bit)


def _f(v):
    return "-" if not np.isfinite(v) else "%.2f" % v


z1, z2, z3, z4 = st.columns(4)
z1.metric("Spearman (tüm aralık)", _f(oz["spearman"]), "Fisher %%95: [%s, %s]" % (_f(oz["sp_alt"]), _f(oz["sp_ust"])), delta_color="off")
z2.metric("Pearson (tüm aralık)", _f(oz["pearson"]), "Fisher %%95: [%s, %s]" % (_f(oz["pe_alt"]), _f(oz["pe_ust"])), delta_color="off")
z3.metric("Beta (tüm aralık)", _f(oz["beta"]), "[%s, %s]" % (_f(oz["beta_alt"]), _f(oz["beta_ust"])), delta_color="off")
z4.metric("n (ortak gün)", oz["n"])
st.caption("Bu üç değer yukarıdaki 'Son %dg' metriklerinden FARKLIDIR: onlar yalnız son pencereyi, bunlar seçili tarih aralığının TAMAMINI kullanır. "
           "Fisher aralığı ve beta aralığı (±1,96 se) günlerin bağımsız olduğunu varsayar; seri korelasyonu varsa gerçek belirsizlik daha geniştir." % a.pencere)

# ---- kısmi korelasyon
if kontroller:
    st.subheader("Ham ve kısmi korelasyon (%s)" % a.yontem.capitalize())
    kd = iliski.kismi_korelasyon(g.loc[bas:bit], x, y, kontroller, yontem=a.yontem)
    k1, k2, k3 = st.columns(3)
    k1.metric("Ham korelasyon", _f(kd["ham"]), "aynı %d günde, kontrolsüz" % kd["n"], delta_color="off")
    k2.metric("Kısmi korelasyon", _f(kd["r"]), "Fisher %%95: [%s, %s]" % (_f(kd["alt"]), _f(kd["ust"])), delta_color="off")
    k3.metric("n (A, B ve kontroller ortak)", kd["n"])
    if np.isfinite(kd["r"]) and np.isfinite(kd["ham"]):
        st.caption("Kontrol: %s. Kısmi korelasyon, A ve B'nin kontrol değişkenlerine verdiği tepki çıkarıldıktan sonra kalan (artık) ilişkidir. "
                   "Ham değerden belirgin düşüyorsa ilişkinin büyük kısmı ortak sebepten (kontrol) gelir; düşmüyorsa doğrudan bağ daha olasıdır. "
                   "Doğrusal çıkarma yapılır; nedensellik göstermez." % ", ".join(kontroller))
    else:
        st.warning("Seçilen aralıkta bu kombinasyon için yeterli ortak gözlem yok.")

# ---- rolling beta
st.subheader("Rolling beta (%s ~ %s, %dg)" % (y, x, rpen))
rb = rolling_b(a.dmg, a.baz, x, y, rpen).loc[bas:bit].dropna(subset=["beta"])
if len(rb):
    fb = go.Figure()
    fb.add_trace(go.Scatter(x=rb.index, y=rb["ust"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fb.add_trace(go.Scatter(x=rb.index, y=rb["alt"], fill="tonexty", fillcolor="rgba(142,68,173,0.15)", line=dict(width=0),
                            showlegend=False, hoverinfo="skip"))
    fb.add_trace(go.Scatter(x=rb.index, y=rb["beta"], name="beta", line=dict(color="#8e44ad", width=1.6), customdata=rb["n"],
                            hovertemplate="%{x|%Y-%m-%d}<br>beta=%{y:.2f}<br>n=%{customdata}<extra></extra>"))
    fb.add_hline(y=0, line_dash="dot", line_color="gray")
    fb.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
    ortak.goster(fb)
    st.caption("Bant: beta ± 1,96 OLS standart hatası (pencere içi günleri bağımsız varsayar; örtüşen pencereler nedeniyle yan yana noktalar bağımsız değildir). "
               "%s %%1 oynarsa %s ortalama beta kadar %% oynar." % (x, y))
else:
    st.info("Seçilen aralık ve pencere için rolling beta üretilemedi (yetersiz gözlem).")

if "GRAMALTIN" in (x, y) or "USDTRY" in (x, y):
    st.info("Gram altın ve TL bazlı her şey USDTRY'den mekanik olarak etkilenir; bu çiftte ilişki yükselmesi çoğu zaman TL faktörüdür.")
ortak.sayfa_sonu("Üst grafik iki varlığın korelasyonunun zaman içindeki seyrini gösterir: 60g hızlı ama gürültülü, 250g yavaş ve "
                 "stabildir. Gölgeli bantlar belirsizliktir. Alt grafik iki varlığın fiyatını aynı başlangıç değerine (100) "
                 "indirger; korelasyon getiriler üzerinden hesaplanır, fiyat seviyeleri üzerinden değil.")
