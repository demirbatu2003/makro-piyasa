# Makro Pano s11 (Beklenti) ve s12 (Makas): bugun ne diyor, ise yariyor mu?

Tarih: 2026-10-17. Veri: toplayici.oku (salt okunur), son gozlem 2026-10-16, USD baz, tum kategoriler (sayfa varsayilanlari).
Hicbir repo dosyasi degistirilmedi, git calistirilmadi. Scriptler: `C:\Users\batuh\AppData\Local\Temp\claude\C--Users-batuh\855ecb88-1715-4598-a6ed-4838231487aa\scratchpad\s11_s12\` (common.py, a1/a2.py, wf11.py, wf11b.py, b1/b2/b3.py).
Onceki calismalar (tekrar edilmedi): s10 walk-forward 0/10 (analiz\benzer.py); `arastirma\dxy_pairs_arastirma.md` (DXY/G10 FX ve kripto ciftleri, "%76,9" iddiasi n=13).

## Kisa sonuc
- s11 yeni bir "tahmin" degil: tarihsel sok olaylarinin sonrasina bakan bir olay calismasi (event study). s10'un k-NN'inden farkli yontem, ama ayni tur iddia ("kosullu olasilik, taban orandan farkli mi?") ve ayni sonuc: walk-forward'da deger katmiyor.
- s12 bugun 1 "asiri" + 4 "acilan" cift gosteriyor. Taban oran ve maliyet sonrasi tek basina kullanilabilir bir sey cikmadi. Yeni ciftlerde (EURUSD/USDJPY, USDZAR/BOVESPA) edge yok / gurultu.
- Kisa vadeli kullanilabilir bir sey: YOK. Dikkat: s11'in en "guclu" gorunen sonuclari (Asya borsalari) zaman dilimi (kapanis saati) etkisi, islem fikri degil.

## 1. s11 ne yapiyor (sade anlatim)
Iki bolum, ikisi de k-NN degil:
1. Canli sok tarayicisi: son 10 is gununde bir varlik kendi (60 gunluk, bugun haric) oynakligindan 1.8 kat fazla hareket ettiyse "sok" der. Sonra "gecmiste ayni varlik ayni yonde sok yasadiginda, diger 31 varligin sonraki 1/5/20 gunu nasil gecti?" diye bakar: medyan getiri, "yukari oran" ve bunun kosulsuz taban orandan farki (DeltaP).
2. Coklu kosul motoru: "SPX 5 gunde -1 sigmadan fazla dustu (+ istege bagli ikinci kosul / VIX rejimi)" kosulunun gecmis gunlerini bulur, ayni sekilde kosullu/kosulsuz karsilastirir.

### Bugunun cikti (varsayilan ayarlar: pencere 10g, k=1.8, ufuk 5g)
Aktif sok sayisi: 18 (son 10 is gunu). En yeni: NASDAQ -2.17% (z -2.09, 10-16), BIST100 -2.90% (z -1.91, 10-16), NIKKEI -5.04% (z -2.76, 10-15), NIFTY +2.30% (+2.38), USDTRY (+2.18), FTSE +1.40% (+2.01), US10Y -9bp (-1.92), XAGUSD -6.30% (z -2.90, 10-14). 10-05: BOVESPA +11.85% (z +7.96) ve USDBRL -4.43% (z -7.87) (secim sonrasi gercek bir sicrama olabilir; 60 gunluk sigma ile 8 sigma, tek olay).
Sayfa otomatik olarak en yeni soku secer: NASDAQ asagi (|z|>=1.8), gecmiste 144 bagimsiz olay (5 gun ayiklamali).

Tablo (t+5 is gunu, kosullu "yukari %" / kosulsuz / DeltaP puan / kosullu medyan; n=144 civari):
| Hedef | Kosullu | Kosulsuz | DeltaP | Medyan |
|---|---|---|---|---|
| USDCNY | 56.9 | 48.2 | +8.8 | +0.02% |
| USDJPY | 58.3 | 53.8 | +4.6 | +0.22% |
| DXY | 55.6 | 52.1 | +3.4 | +0.16% |
| SPX | 56.9 | 60.2 | -3.3 | +0.32% |
| BTC (n=79) | 40.5 | 53.1 | -12.6 | -0.40% |
| ETH (n=79) | 44.3 | 52.1 | -7.8 | -1.39% |
| FTSE | 40.3 | 54.4 | -14.1 | -0.40% |
| HANGSENG | 36.8 | 52.4 | -15.6 | -1.20% |
| NIKKEI | 21.5 | 55.3 | -33.8 | -1.62% |
t+1: NIKKEI 11.6% yukari (DeltaP -40.5), HANGSENG 22.9% (-28.4), NIFTY -22.3, FTSE -20.1, DAX -19.8. t+20: hicbir hedefte anlamli sapma yok (NIKKEI -18.1 hari; JSE +7.4, BOVESPA +5.6). Tum tablo 32 hedef x 3 ufuk x her sok icin yeniden uretilebilir (a2.py).
Tab 2 varsayilani (SPX 5g < -1 sigma, t+20): n=200 donem, koşul bugun AKTIF. En yuksek DeltaP: BOVESPA +11.1, JSE +9.4, NIFTY +6.6, FTSE +5.2; en dusuk: VIX -19.6 (VIX dusme egilimi), USDZAR -9.2, USDBRL -7.6, SHANGHAI -7.5. SPX'in kendisi: 66.5% vs 66.9% (DeltaP -0.35).

### Metodoloji kontrolu
- Lookahead: YOK (sigma, z ve kosul maskeleri `.shift(1)`; ileri getiri t+1..t+H, olay gununu icermiyor; olay secimi yalniz gecmis, bugunun sok'u kendi istatistigine girmiyor: ufuk dolmamis olaylar zaten dislaniyor). Teknik olarak temiz.
- Ortusme: olaylar yalniz 5 gun arayla ayikliyor ama ufuklar 5/20/60 gun. t+20 ve t+60'ta olaylarin ileri pencereleri ortusuyor, n=144/200 bagimsiz gozlem degil (etkin n belki 40-80). Kosulsuz havuz (n~4300) neredeyse tamamen ortusen pencereler; guven araligi gosterilmiyor.
- Anlamlilik: n=144 ile tek bir yuzde farkinin standart hatasi ~4-5 puan (ortusmeyle 6-8). 32 hedef x 3 ufuk x ~36 tetikleyici x 2 yon taranirken |DeltaP|<10 beklenen gurultu. Coklu test duzeltmesi yok. "n<15 yetersiz" esigi cok dusuk (15 olayda hata payi +-13 puan).
- Zaman dilimi (kritik): Asya borsalari ABD'den once kapanir. "NASDAQ dustu -> NIKKEI/HANGSENG ertesi gun dusuyor" gercek ama sozde: ABD seansi sirasinda Nikkei vadelisi zaten fiyatladi. Kapanistan-kapanisa islem fikri degil. Sayfa bunu uyarmiyor.
- Maliyet: yok. Ufuk ve fiyat getirisi baz alinmis, islem yok.
- BOVESPA +11.85% / z=7.96 tek gun; 60g sigma ile olcu cok yuksek, sayfa "outlier / veri hatasi?" uyarmiyor.

### s10 ile iliski
Kopya degil: s10 = 8 makro ozellikli Oklid k-NN, s11 = 1-2 kosullu olay calismasi. Ayni felsefe (analog / kosullu taban oran). s10'un 0/10 sonucu s11 icin de gecerli cikti (asagida).

### Walk-forward (2016'dan itibaren, yalniz t'den onceki tamamlanmis olaylar, n>=15, taban oran de ayni ilke)
Yontem (wf11.py): her sok gunu t (tetikleyici basina olaylar H gunden seyrek, ortusme yok), gecmis tamamlanmis olaylardan DeltaP hesapla; |DeltaP|>=10 ise sayfanin yonunu (DeltaP>0 -> yukari) tahmin et ve gerceklesen t+1..t+H yonuyle karsilastir. Taban: "kosulsuz havuzun cogunluk yonu". US2Y/US10Y/VIX/USDHKD cikarildi. Net P&L: yon x getiri - 5bp.
| Test | N tahmin | Isabet | Taban isabeti | Fark | Net ort (bp) |
|---|---|---|---|---|---|
| Tab1 sok, H=5, tum hedefler | 15462 | 54.0% | 52.6% | +1.3 | +24 |
| Tab1 sok, H=5, Asya/BIST/EM borsalari haric | 9033 | 51.5% | 54.0% | -2.5 | +7 |
| Tab1 sok, H=20, tum | 7143 | 53.5% | 53.6% | -0.1 | -13 |
| Tab1 sok, H=20, Asya vb. haric | 4466 | 52.7% | 54.9% | -2.3 | -41 |
| Tab2 tum varlik 5g/-+1 sigma, H=20 haric | 2259 | 49.4% | 56.0% | -6.7 | -120 |
| Tab2 varsayilan (SPX 5g < -1 sigma), H=20, tum | 97 | 58.8% | 51.5% | +7.2 | +51 |
| Ayni, Asya haric | 7 | 42.9% | 57.1% | n yok | n yok |
- Sonuc: sayfanin DeltaP'si ex-ante olarak taban orani gecmiyor. Tek "pozitif" satirlar Asya zaman-dilimi etkisinden geliyor (Tab2 varsayilanin 97 tahmininin 90'i Asya/EM hedefi).
- DeltaP buyudukce isabet artmiyor (H=20: DeltaP 10-15 -> 52.3%, 20-30 -> 52.0%, >30 -> n=8). Yani "buyuk DeltaP = guvenilir" dogru degil.
- Kisa pencere / suruculuk (H=20, Asya haric): 129 ay, taban orani gecen ay orani %44, ortalama fark -1.4 puan. Yillar: 2020 -12 puan, 2021 -11, 2022 -7, 2023 +1, 2024 +4, 2025 +18, 2026 (10-16'ya) -5. Son 24 ay: pozitif 15 / negatif 9 ay ama 2026 de 9 aydan 6 si negatif; aylik fark -50..+41 puan arasinda sallaniyor. Su an (2026-07 -> 09) uc ay ust uste negatif.
- Surdurulebilirlik yok: iyi yil (2025) ardindan 2026 negatif.

## 2. s12 (Makas): bugun ne diyor
Varsayilan: beta-ayarli makas, 20g kisa pencere, 250g ex-ante dagilim, min |r|=0.55 (Spearman), k=2, kapanma ufku 10 gun. Taranan cift: 41. Asiri (|z|>=2): 1. Acilan (1.5<=|z|<2): 4.

| A / B | r_250 | z | durum | Sayfa "kapanma %" (n) | Taban kapanma % (tum gunler) | Fark (puan) |
|---|---|---|---|---|---|---|
| EURUSD / GBPUSD | 0.86 | -2.01 | A geride / B onde | 61.0 (59) | 51.4 | +9.6 |
| EURUSD / USDJPY | -0.59 | -1.67 | makas aciliyor | 52.5 (61) | 52.6 | -0.1 |
| DXY / GBPUSD | -0.75 | +1.61 | makas aciliyor | 66.7 (57) | 49.4 | +17.3 |
| USDZAR / BOVESPA | -0.55 | +1.60 | makas aciliyor | 56.5 (62) | 53.2 | +3.3 |
| EURUSD / DXY | -0.82 | -1.57 | makas aciliyor | 58.6 (87) | 53.9 | +4.7 |
Normal ama yakin: DXY/USDJPY +1.44, BTC/ETH +1.43 (n=29), USDZAR/FTSE +1.30, SOL/ALTSEPET -1.25 (sayfadaki %76.9 = n=13).
- dxy_pairs dosyasinda zaten olanlar (ozet, tekrar yok): DXY/GBPUSD, EURUSD/DXY, DXY/USDJPY, EURUSD/GBPUSD (EURGBP), BTC/ETH ve SOL/ALTSEPET: hicbiri Bonferroni'yi gecmedi, EURUSD/DXY kapanis saati artefakti, kripto ciftlerinde net negatif. YENI olanlar: EURUSD/USDJPY, USDZAR/BOVESPA (ve yakin: USDZAR/FTSE).
- "Taban kapanma" = z'nin isaretinin tersine makasin sonraki 10 gunde gitmesi, her gun icin. %50'nin ustunde cikiyor (51-54%): sayfanin "%56-%67 kapanma" yuzdeleri hem taban oran farki ~3-17 puan, hem de n~60 ile standart hata ~6.5 puan; tek basina anlamli degil (DXY/GBPUSD +17 puan ~2.6 sigma, onceki dosyada zaten reddedildi: Bonferroni, ortusme, EURGBP kopyasi).

### Kapanma % mi net karli % mi? (basit kural, 10g, maliyet: FX 3bp/bacak, kripto 10, borsa/emtia 5; bacak maliyeti beta ile agirliklandi)
Kural: |z|>=2 kapanista gir (flat iken), ortalamaya dogru yon, 10 is gunu tut, maliyet cikista. Tum tarih ~2011-2026.
| Cift | n islem | Brut pozitif % | Net karli % | Brut ort bp | Maliyet bp | Net ort bp | t | 1 gun gecikmeli net ort |
|---|---|---|---|---|---|---|---|---|
| EURUSD/GBPUSD | 55 | 61.8 | 61.8 | +32.5 | 5.0 | +27.5 | 1.7 | +18 |
| EURUSD/USDJPY | 60 | 50.0 | 48.3 | +17.7 | 4.1 | +13.7 | 0.7 | +10 |
| DXY/GBPUSD | 57 | 68.4 | 66.7 | +25.2 | 4.7 | +20.5 | 1.7 | +22 |
| USDZAR/BOVESPA | 57 | 57.9 | 57.9 | +69.1 | 4.0 | +65.1 | 1.3 | +44 |
| EURUSD/DXY | 75 | 58.7 | 52.0 | +10.1 | 6.1 | +4.1 | 0.7 | -4 |
| USDZAR/FTSE (yakin) | 56 | 66.1 | 66.1 | +103.9 | 4.8 | +99.0 | 1.8 | +33 |
Maliyet "kapanma %" ile "net karli %" arasini sadece dusuk-hareketli ciftlerde acar (EURUSD/DXY 58.7 -> 52.0; EURUSD/USDJPY 50 -> 48). Asil sorun maliyet degil, edge'in zaten taban orana yakin olmasi.

### Yeni ciftlerde ayrinti
EURUSD/USDJPY (bugun z -1.67, esik altinda: sinyal YOK)
- 60 islem, ort net +13.7 bp, t=0.7. IS 2011-2020: n=36, +19.9bp, %50 karli, t=0.69. 2021+: n=24, +4.3bp, %46 karli, t=0.19. Son islemler: 2026-09-16 -89, 2026-10-01 -35 (bugun acik, -35bp).
- Son 24 ay aylik net P&L (bp): -85, +99, 0, 0, -96, -106, -39, 0, 0, 0, 0, 0, 0, 0, 0, 0, +56, 0, 0, +70, +7, 0, -89, -35 (2024-11 -> 2026-10). Toplam -218, 4 pozitif / 6 negatif / 14 sifir ay. Islem sayisi 1-2 / ay veya hic.
- Kalicilik (tum tarih, ~200 ay): son 3a>0 iken ertesi ay ort -2.2 bp (n=63), <=0 iken +7.1 bp (n=136). Momentum yok, hatta ters. "Sadece sicakken islem": toplam -141 bp vs hep islem +821 bp. Su an 3a=-125, 6a=-48: sicak degil.
USDZAR/BOVESPA (bugun z +1.60, esik altinda: sinyal YOK; B bacagi +11.75% 20g, 10-05 BOVESPA +11.85% tek gunluk sicrama bunu surukluyor)
- 57 islem, ort net +65 bp, t=1.3. IS 2011-2020: n=38, +56.6bp, %60.5, t=1.05. 2021+: n=19, +82bp, %52.6, t=0.79. Tek olay etkisi: 2025'te iki islem ort +956 bp (Ocak 2025 ay P&L +1867); onsuz 2021+ ortalama yaklasik 0'a yakin. Yil yil net ort: 2020 -176, 2022 -27, 2023 -83, 2024 -124, 2025 +956.
- Son 24 ay aylik net P&L (bp): -257, -197, +1867, +45, 0 x12, -77, +113, -8, -19, 0, +139, +50, 0 (2024-11 -> 2026-10). Toplam +1656 ama tek ay (2025-01) +1867; geri kalan 23 ay toplam -211. 5 pozitif / 5 negatif / 14 sifir ay.
- Kalicilik: son 3a>0 iken ertesi ay ort +5.6 (n=68), <=0 iken +25.4 (n=131); sicak degil iken daha iyi. "Sadece sicakken": +380 vs hep +3711. Su an 3a=+189, 6a=+162 (sicak ama tek islemin kazanci).
- Uygulama: USDZAR perakende CFD'de genis spread + swap (carry ZAR icin buyuk); BOVESPA USD cinsinden = EWZ benzeri; test 3bp/5bp varsayimi iyimser. Bu cifte tek karar veren tek buyuk olay var.
USDZAR/FTSE (esik altinda, 1.30): 2021+ n=19 +221bp t=1.66; son 24 ay +3624 ama 2024-11 (+2125) ve 2025-01 (+1489) iki ay; sonra 2026'da -90, -164, -59, -1, -36, +78, +160. Aynisi.

### Genel tarama (37 cift, ayni kural, post-hoc)
- 32/37 ciftte ort net > 0 (medyan +32 bp/islem); ort t=0.87; sadece 3 cift t>2 (USDZAR/JSE 2.8, USDZAR/SPX 2.1, XAUUSD/JSE 2.1; GRAMALTIN/JSE 2.0, USDZAR/DAX 1.9 hemen altinda). 37 test icin Bonferroni esigi t~3.2: hicbiri gecmiyor. USDZAR iceren 8 cift ort t=1.59, digerleri 0.67.
- Pozitif egilim muhtemelen makro/ZAR karakteri (20g getiri makasi gercekten biraz geri donuyor) + bugunun korelasyonuyla secim yanliligi. Maliyet varsayimi ZAR/JSE icin gercekci degil.
- Metaller: XAGUSD/BAKIR (z -0.95, n=58, net +140bp/islem t=1.2), XAUUSD/XAGUSD (net +0.2). Borsa: SPX/NASDAQ net -38 (t -2.6), SPX/DAX +52 (t 1.7), DAX/FTSE +32 (t 1.0). Bugun hicbiri sinyalde degil.

## 3. Kisa vade gorunumu ozeti
| Cift | Bugun sinyal | Son 24 ay net (bp) | Pozitif/negatif/sifir ay | Sicak (3a>0)? | Kalicilik |
|---|---|---|---|---|---|
| EURUSD/USDJPY | yok (z -1.67; acik islem -35bp) | -218 | 4/6/14 | Hayir (-125) | yok / ters |
| USDZAR/BOVESPA | yok (z +1.60) | +1656 (tek ay +1867) | 5/5/14 | Evet (+189) ama tek olay | yok |
| USDZAR/FTSE | yok (z +1.30) | +3624 (iki ay) | 6/5/13 | Evet (+160) | zayif |
| EURUSD/GBPUSD (ref) | esikte (z -2.01) | -71 | 2/5/17 | Hayir (0) | belirsiz |
Sonuc: kisa pencerede kar iki-uc ay + birkac islemden geliyor; "calisiyor ve devam ediyor" kanit yok.

## 4. Sayfa metinleri yaniltici mi? Gemini'ye oneriler
s11:
1. "Takip eden ufuk" tablosunda zaman dilimi uyarisi ekle: ABD hisse soklari sonrasi Asya t+1 "dusus" tarihsel dogru ama onceden fiyatlanmis; kapanistan kapanisa islem fikri degil.
2. DeltaP sutununu "n_etkin" (ortusme duzeltmeli) ve guven araligi ile goster; "n<15 yetersiz" esigini en az 30 yap, kosul: |DeltaP| < 2 x SE ise gri.
3. "En yuksek DeltaP'ye gore sirala" varsayilanini kaldir ya da "32 hedef x 3 ufuk taraniyor: ilk siradakiler cogunlukla tesadufi" uyarisi koy; en az Benjamini-Hochberg duzeltmesi uygula.
4. t+20/t+60 icin olaylari ufuk kadar (en az H gun) ayiklayarak ortusmeyi kaldir (sadece 5 gun ayiklaniyor).
5. Ilk metin "Tum volatilite ve esik hesaplari ex-ante" dogru; ama sayfaya "walk-forward testinde taban orani gecmedi (2016-2026)" notu eklenebilir.
6. Outlier uyarisi: z>5 olan tek gunluk hareketlerde (BOVESPA +11.85%, z=7.96) "veri hatasi / olay" etiketi.
7. Sayfa_sonu metni "diger varliklarin nasil tepki verdigi" diyor: fiyat tepkisi ile islem edilebilir getiri farkli; maliyet eklenmedigini yaz.
s12:
1. Ust sayac `asiri_sayisi` / `acilan_sayisi` 2.0 ve 1.5'i sabit kodluyor, z-esik kaydirgacini yok sayiyor (s12_makas.py satir 74-75); `makas_durumu` da ayni sekilde varsayilan 2.0 kullaniyor. Kaydiraciya bagla.
2. "kapanma_orani" yaninda ZORUNLU olarak taban orani goster ("tum gunlerde ayni ufukta kapanma %51-54"); su an %56-%77 yuzdeleri %50 baz alinmis gibi okunuyor. Fark = tesadufi olabilir (n~60, SE ~6.5 puan).
3. "Net karli %" ve maliyet sutunu ekle (FX 3bp, kripto 10bp/bacak, borsa 5bp), "medyan kapanma" bp cinsinden.
4. Ortusen olaylar: 10-20 gunluk ufuk icin olaylari ufuk kadar ayikla ya da n'i "etkin n" olarak yaz. n<10 esigi kucuk (n=13 olan SOL/ALTSEPET %76.9 vitrine cikiyor): en az 30.
5. Tarama bugunun 250g korelasyonuna gore ciftleri seciyor (gecmise donuk secim yanliligi) ve onlarca cift x 3 ufuk x 3 yon tarandiginda coklu test duzeltmesi yok; "kesif amaçlidir, islem sinyali degildir" uyarisini tablonun hemen ustune tasi.
6. Birbirinin kopyasi ciftleri (XAUUSD/GRAMALTIN, EURUSD/DXY: DXY'nin %57.6'si EURUSD, EURUSD/GBPUSD ~ EURGBP) isaretle; DXY ciftlerinde kapanis saati artefaktini belirt.
7. Kripto ve ALTSEPET ciftlerinde "survivorship (2026-10-16 hacmi) + funding yok" uyarisi.
