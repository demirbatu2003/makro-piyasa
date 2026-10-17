# analiz: Makro Pano v1 analiz kütüphanesi

Saf fonksiyonlar (pandas/numpy/scipy), I/O ve Streamlit yok. Girdi: `toplayici/oku.py`'nin
`katalog()` ve `gunluk_panel()` çıktıları. Kullanım: `makro-pano` klasörü path'te olmalı,
`from analiz import getiriler, korelasyon, ...`. Test: `python -m pytest analiz/testler -q` (24 test).

Kural özeti: ileri doldurma yok; ikili tam gözlem; pencere = iş günü satırı (hafta sonu seviyeleri getiriden ÖNCE atılır; kripto Pzt getirisi = Cuma->Pzt);
min gözlem 60g->40, 250g->150; fiyat log-getiri, faiz bp.

## getiriler (tüm ekranlar)
- `getiri_hesapla(panel, katalog, max_bosluk_gun=5, hafta_sonu_at=True)` seviye -> log-getiri / bp
- `usd_cevir(panel, katalog, kodlar=None)` yerel seviye -> USD (usd_kur_kodu, usd_kur_ters). Sıra: önce `usd_cevir`, sonra `getiri_hesapla` (baz anahtarı)
- `haftalik_seviye(panel)`, `haftalik_getiriler(panel, katalog)` örtüşmeyen haftalık getiri (Ekran 6 haftalık)

## korelasyon (Ekran 1, 2, 7)
- `korelasyon_matrisi(getiri, pencere=None, bitis=None, yontem='spearman', min_gozlem=None)` -> `(corr, n)` (Ekran 1)
- `iki_nokta_karsilastirma(getiri, pencere=60, geri=250, yontem, min_gozlem, bitis)` -> dict simdi/onceki/fark/n_*/fark_p (Ekran 1 fark modu)
- `ortalama_ikili_korelasyon(corr)` tek sayı özeti (Ekran 1, 7)
- `ikili_rolling(getiri, a, b, pencere=60, yontem, min_gozlem)` -> korelasyon, n, alt, ust (Ekran 2)
- `anlamlilik_tablosu(corr, n, alpha=0.05)` -> a, b, r, n, p, q, fdr_anlamli (v2 keşif listesi)
- `ortak_gozlem(getiri)`, `min_gozlem_varsayilan(pencere)`

## ag (Ekran 3)
- `mst_kenarlari(corr, kategori=None)` -> `(kenarlar[a,b,rho,uzaklik], dugumler[kod,kategori,derece,x,y], elenenler)`
- `kenar_listesi_ciz(kenar, dugumler)` Plotly segment koordinatları; `mst_degisim(k1, k2)` iki zaman noktası farkı
- `kenar_kararliligi(getiri, pencere=250, adim=20)` kenar görülme oranı
- `hiyerarsik_kumeleme(corr, yontem='average')` -> kodlar, Z, sira (dendrogram/heatmap sırası); `kume_etiketleri(sonuc, k)`; `matrisi_sirala(m, sira)` (Ekran 1 sıralaması da)
- `uzaklik_matrisi(corr)`: d = sqrt(2(1-rho))

## rejim (Ekran 2 gölgeleme, Ekran 4)
- `vix_rejimi(vix_seviye, esikler=(15, 25))` -> sakin/normal/gergin
- `rejim_korelasyonlari(getiri, rejim, yontem, min_gozlem=40, min_rejim_gun=60)` -> `({rejim: (corr, n)}, ozet)`
- `beta_tablosu(getiri, referans, pencere=None, bitis=None)` -> beta, se, t, r, n

## olay (Ekran 5)
- `olaylari_bul(seri, k=2, sigma_pencere=60, yon, ayikla_gun=5)` (sigma ex-ante, bugün hariç)
- `olay_tepkileri(getiri, tetik, k=2, ufuklar=(0,1,5,20), yon, min_olay=20)` -> `(olaylar, ozet)`; ozet: yon, hedef, ufuk, n, ortalama, medyan, q25, q75, ci_alt, ci_ust, poz_orani, ayni_yon_orani, yetersiz

## leadlag (Ekran 6)
- `capraz_korelasyon(getiri, x, y, gecikmeler=(-1,0,1), yontem, katalog=None)` -> gecikme, r, n, p, alt, ust, anlamli, uyari. k>0: X, Y'yi k adım önden gider. p değerleri çoklu test düzeltmesizdir.
- `kapanis_uyarisi(katalog, x, y)`

## saglik_yardimci (Ekran 0)
- `seri_sagligi(panel, katalog=None, bugun=None, bayat_esik_is_gunu=3)` -> ilk, son, gozlem, bayatlik, eksik_is_gunu, en_uzun_bosluk_gun, durum

## istatistik
- `fisher_bant`, `korelasyon_p`, `bh_fdr` (ortak yardımcılar)

## benzer (Ekran 10 Benzer Günler)
- Analog / koşullu taban oranı; tahmin değil. `ozellik_tablosu`, `zskor` (genişleyen, 500g ısınma), `hedef_seviyeleri`, `ileri_getiriler(seviye, ufuk)`,
  `analog_bul` (Öklid, aday kesimi H+5, ±20g bağımsızlık), `analiz`/`karsilastir` (analog vs koşulsuz), `walk_forward`, `walk_forward_ozet`, `walk_forward_yorum`, `bugunun_durumu`.
- Özellik için son gözlem en fazla 5 takvim günü taşınır; sonuçlarda ileri doldurma yok. Ayrıntı: modül docstring'i.
