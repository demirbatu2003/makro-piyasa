# DXY ile GBPUSD (ve diger DXY-iliskili) makas: islem yapilabilir mi?

Tarih: 2026-10-17. Veri: `toplayici.oku.gunluk_panel` (salt okunur), son gozlem 2026-10-16 (EURUSD/USDJPY 10-15).
Scriptler: `C:\Users\batuh\AppData\Local\Temp\claude\C--Users-batuh\855ecb88-1715-4598-a6ed-4838231487aa\scratchpad\dxy_pairs\` (s12run.py, bt.py, diag.py). Repo'daki baska hicbir dosya degistirilmedi.

## Kisa sonuc
- DXY-GBPUSD makasi ile islem yapma. Bu makas bagimsiz bir firsat degil; buyuk olcude EURGBP'nin baska bir gorunumu.
- On-kayitli kuralda iki cift formel olarak gecti (DXY-EURUSD, EURGBP), ama ikisi de saglam degil (Bolum 4). DXY-GBPUSD ve DXY-USDJPY kaldi.
- Hicbir cift Bonferroni duzeltmesini (4 test) gecemiyor.

## 1. s12 / analiz\makas.py ne gosteriyor (kod degistirilmeden calistirildi)
Parametreler: sayfa varsayilani (beta makas, kisa pencere 20g, uzun 250g, k=2).

| A / B | s12 z (20g) | durum | beta (250g OLS) |
|---|---|---|---|
| DXY / GBPUSD | +1.61 sigma (son 8 gun: 2.72, 2.42, 2.42, 2.36, 1.97, 1.90, 1.68, 1.61) | "Makas aciliyor" | -0.598 |
| GBPUSD / DXY (ters siralama) | +1.22 | Normal | -0.923 |
| DXY / EURUSD | +0.34 | Normal | -0.764 |
| DXY / USDJPY | +1.44 | Normal | +0.435 |

Kullanicinin gordugu "acilan makas": z bir hafta once 2.7 idi, simdi kapaniyor (1.61).

### Sayfanin kendi "geri donus" isabet oranlari (DXY/GBPUSD, |z|>=2, olay basina, 5 gun ayiklamali)
| ufuk | n | isabet | medyan kapanma |
|---|---|---|---|
| 5g | 57 | %56 | %0.08 |
| 10g | 57 | %67 | %0.23 |
| 20g | 56 | %55 | %0.27 |

Yon bazinda: DXY onde (z>=+2) 5/10/20g: %52/%56/%54 (n 26-27); GBPUSD onde (z<=-2): %60/%77/%57 (n=30). 10g'deki %67'nin buyuk kismi tek yonden geliyor.
Karsilastirma (benim hesabim): kosulsuz taban oran (her gun, z isareti yonunde) h=5/10/20 icin %50.4/%51.5/%49.8. |z|>=2 gunleri (ortusen, 205/168/86 gun) %59/%64/%59.

### Metodoloji kontrolu (lookahead / ortusme / maliyet)
- Lookahead: YOK. beta, korelasyon, 60g vol ve z'nin ortalama/std'si `.shift(1)` ile hesaplaniyor; ileri getiri t+1..t+h, olay gununu icermiyor. Kod yorumlari dogru.
- Tanim farki (onemli): s12 z'si "20 gunluk kumulatif GETIRI makasi"nin kendi 250g dagilimina gore z'sidir (getiri-momentumu asiri mi?). Fiyat SEVIYESI mean-reversion'i degildir. Bu yuzden asagidaki 60g seviye z'si ile ayni sayi cikmaz (bugun 60g-seviye z = +1.78, s12 z = +1.61).
- Ortusen olaylar: olaylar yalniz 5 gun arayla ayikliyor, ufuk ise 10-20 gun. Ardisik olaylarin ileri pencereleri ortusuyor; n=57 bagimsiz gozlem degil, guven araligi gorunenden genis.
- Maliyet: YOK. "Kapanma" > 0 sayiliyor; medyan 0.1-0.3% iken iki bacak maliyeti ~6-9 bp bunun bir kismini yer. Isabet orani != karlilik.
- Secim yanliligi: tarama son 250g korelasyonu esigi gecen ciftleri seciyor (bugunun bilgisiyle secim); 3 yon x 3 ufuk x cok cift ayni anda gosteriliyor, coklu test duzeltmesi yok.
- Zaman damgasi: panelde FX "Londra gece yarisi" kapanisi, DXY ABD kapanisi (ICE DX uzlasma penceresi 14:59-15:00 ET, kaynak ice.com/products/194). Asenkron kapanis, DXY-EURUSD'de sahte ilk-gun geri donusu uretiyor (Bolum 4).
- Sonuc: s12 isabet oranlari kesif amaclidir, islem sinyali degil; sayfada da uyari var.

## 2. DXY yapisi: DXY-GBPUSD makasi ~ EURGBP
- ICE formulu: DXY = 50.14348112 x EURUSD^-0.576 x USDJPY^0.136 x GBPUSD^-0.119 x USDCAD^0.091 x USDSEK^0.042 x USDCHF^0.036 (geometrik ortalama). Birden fazla kaynakta tutarli (Wikipedia, 5paisa, bsic.it; ICE'in 6 para birimi listesi). ICE metodoloji PDF'ini dogrudan dogrulayamadim: YARI-DOGRULANDI.
- Veriyle: DXY gunluk getirisinin EURUSD, GBPUSD, USDJPY'ye regresyonu R2 = 0.82; katsayilar EUR -0.57, GBP -0.15, JPY +0.14 (resmi: -0.576 / -0.119 / +0.136; CAD/SEK/CHF panelde yok).
- DXY'den beta-hedge ile GBPUSD cikarilinca (beta ort. -0.56, aralik -0.82..-0.25) kalan seri GBP'den bagimsiz olur; geriye agirlikli EUR (ve JPY) kalir. Gunluk artik getiri korelasyonlari (3,963 gun):
  - EURGBP (EURUSD-GBPUSD log farki) ile: **-0.65** (2012-2020: -0.66; 2021+: -0.60), R2 ~ 0.36-0.43
  - EURUSD ile -0.59, GBPUSD ile -0.00 (beta-hedge GBP'yi temizliyor), USDJPY ile +0.40.
- Yorum: makas, GBP'nin DXY'ye (agirlikli olarak EUR'a) gore degeri. Dolar hakkinda yeni bilgi tasimiyor. Bugun: DXY-GBPUSD makasi pozitif z (DXY zengin) = short DXY + short GBPUSD*0.6, yani kabaca long EURGBP; EURGBP'nin kendi z'si de -2.0 (long EURGBP). Ayni sinyal.

## 3. Enstrumanlar ve Turkiye'den erisim
| Enstruman | Bilgi | Durum |
|---|---|---|
| ICE DX vadeli | Carpan $1000 x endeks (~$100k notional), tick 0.005 = $5, Mar/Haz/Eyl/Ara, fiziki teslim (EUR, JPY, GBP, CAD, SEK, CHF), gunluk limit yok. ice.com/products/194 | dogrulandi |
| ICE Micro USDX (MDX) | $100 x endeks (~$10k), nakit uzlasi; spec tarihi 2026-08-29. ice.com/products/83049912 | dogrulandi (likidite bilinmiyor) |
| ETF UUP / UDN | Invesco DB US Dollar Index Bullish / Bearish; gider orani %0.75-0.78 (kaynaklar farkli, en yeni %0.75) | yaklasik; birincil kaynak dogrulanmadi |
| Broker CFD ("USDX/DXY") | spread/swap araci kuruma bagli | dogrulanamadi |
| Bilesen spot FX | EURUSD, GBPUSD, USDJPY, EURGBP; EURGBP ortalama spread ~0.9 pip (0.2-1.4) = ~1-1.5 bp (BrokerChooser/daytrading.com; Turkiye'ye ozgu degil) | genel tahmin |
| SPK lisansli forex | 2017 SPK tebligi: azami kaldirac 10:1, min. baslangic teminati 50.000 TL. 2026'da hala gecerli mi? | DOGRULANAMADI |
| VIOP doviz vadeli | USDTRY (1000 USD), EURTRY (1000 EUR), EURUSD (1000 EUR) (Borsa Istanbul egitim sunumu); GBPUSD, EURGBP, DXY dogruladigim listede YOK; guncel sartname dogrulanmadi | kismen |
| Turk araci kurumdan yurt disi ETF (UUP) | komisyon/erisim bilgisi bulunamadi | DOGRULANAMADI |

Not: VIOP'ta GBP veya EURGBP olmadigi icin bu makas VIOP'ta islenemez. Kucuk sermaye icin en makul vekil EURGBP spot (tek enstruman, tek spread). DX vadelisi ~$100k, Micro ~$10k notional; UUP yillik %0.75 gider ve kisa vadeli makas icin uygun degil.

## 4. On-kayitli backtest
Kurallar (sabit): makas = ln(A) - beta*ln(B); beta = son 250 gunluk getirilerde OLS, ayin ilk is gunu yenilenir; z = (makas - 60g ort)/60g std (60g pencerede makas o gunku beta ile yeniden hesaplanir, beta sicramasi yok); EURGBP icin makas = ln(EURUSD/GBPUSD). Giris |z|>=2 (kapanista sinyal, ertesi gunun getirisini kazanir; yon ortalamaya donus yonunde), cikis |z|<=0.5 veya 20 is gunu veya |z|>=4. Cift basina tek pozisyon. Cikis sonrasi yeniden giris icin once |z|<2 olmali (uygulama detayi, sonuc gormeden sabitlendi). Maliyet: 3 bp/bacak gidis-donus (iki bacakli ciftte 3*(1+|beta|) bp; EURGBP 3 bp). Carry: politika faizleri (FED, ECB, BoE, BoJ; panelde BoE/BoJ aylik) ile; DXY faizi = FED - (EUR/JPY/GBP agirlikli sepet faizi; CAD/SEK/CHF yok sayildi) -> YAKLASIK. IS 2012-2020, OOS 2021-2026-10. Sharpe: gunluk net P&L (tum gunler, sifirlar dahil) x sqrt(252). Getiriler A bacagi notional'i uzerinden bp, kaldiracsiz. Veri sonunda acik pozisyonlar piyasa degeriyle sayildi.

### OOS (2021-01 -> 2026-10) net, 3 bp maliyet
| Cift | n | isabet | ort net/islem (bp) | ort sure (gun) | Sharpe | maks dusus (bp) | toplam net (bp) | pozitif 6 ay | t-stat |
|---|---|---|---|---|---|---|---|---|---|
| DXY-EURUSD | 41 | %76 | +19.0 | 11.8 | 0.74 | -245 | +837 | 8/12 (%67) | 1.78 |
| DXY-GBPUSD | 33 | %64 | +14.7 | 14.0 | 0.34 | -279 | +484 | 8/12 (%67) | 0.82 |
| DXY-USDJPY | 32 | %59 | +16.8 | 15.2 | 0.29 | -581 | +537 | 7/12 (%58) | 0.69 |
| EURGBP (seviye) | 36 | %67 | +42.4 | 13.6 | 0.80 | -367 | +1528 | 9/12 (%75) | 1.96 |

### In-sample (2012-2020) net
| Cift | n | isabet | ort net (bp) | Sharpe | maks dusus (bp) |
|---|---|---|---|---|---|
| DXY-EURUSD | 57 | %75 | +19.3 | 0.61 | -358 |
| DXY-GBPUSD | 53 | %58 | +13.2 | 0.25 | -881 |
| DXY-USDJPY | 45 | %64 | +5.4 | 0.05 | -837 |
| EURGBP | 48 | %60 | +12.8 | 0.12 | -885 |

### Maliyet duyarliligi (OOS Sharpe) ve carry
| Cift | maliyetsiz | 3 bp | 6 bp (2x) | carry OOS toplam (bp) |
|---|---|---|---|---|
| DXY-EURUSD | 0.94 | 0.74 | 0.54 | -31 |
| DXY-GBPUSD | 0.45 | 0.34 | 0.23 | -86 |
| DXY-USDJPY | 0.36 | 0.29 | 0.21 | +0.5 |
| EURGBP | 0.86 | 0.80 | 0.75 | +25 |

Net rakamlar carry dahil. Carry'siz (3 bp) OOS Sharpe: 0.77 / 0.40 / 0.29 / 0.79. Maliyetsiz sutunda carry dahil, maliyet haric.

### Yil yil net P&L (bp, notional uzerinden; 2026 = 10-16'ya kadar)
| Yil | DXY-EUR | DXY-GBP | DXY-JPY | EURGBP |
|---|---|---|---|---|
| 2012 | 215 | -113 | -213 | 2 |
| 2013 | 79 | 424 | 289 | -243 |
| 2014 | -50 | -396 | -414 | 428 |
| 2015 | 436 | 432 | -100 | 373 |
| 2016 | 98 | 96 | 190 | -211 |
| 2017 | 164 | -108 | 1 | 230 |
| 2018 | -55 | -32 | -99 | 104 |
| 2019 | 150 | 191 | 347 | 181 |
| 2020 | 7 | 210 | 156 | -361 |
| 2021 | 268 | -118 | 217 | 160 |
| 2022 | 201 | 457 | 209 | 496 |
| 2023 | -14 | -199 | -237 | 317 |
| 2024 | -22 | 209 | 75 | 373 |
| 2025 | 213 | 91 | -38 | 227 |
| 2026 | 190 | 45 | 311 | -45 |

### Alti aylik net P&L (bp), OOS donemleri (2026H2 kismi)
| Donem | DXY-EUR | DXY-GBP | DXY-JPY | EURGBP |
|---|---|---|---|---|
| 2021H1 | 125 | -151 | 141 | -165 |
| 2021H2 | 143 | 33 | 76 | 325 |
| 2022H1 | 218 | 124 | 153 | 378 |
| 2022H2 | -16 | 333 | 56 | 118 |
| 2023H1 | 67 | -86 | -226 | 237 |
| 2023H2 | -81 | -114 | -12 | 80 |
| 2024H1 | -51 | 208 | 151 | 40 |
| 2024H2 | 29 | 1 | -76 | 334 |
| 2025H1 | 215 | -79 | 10 | 160 |
| 2025H2 | -2 | 170 | -48 | 67 |
| 2026H1 | 134 | 27 | 363 | -2 |
| 2026H2* | 56 | 18 | -52 | -42 |

IS alti aylik donemlerin tamami bt.py ciktisinda; ornek kotu donemler: EURGBP 2020H1 -674, DXY-GBP 2014H2 -503, DXY-JPY 2014H2 -422 / 2018H1 -362. Kisa pencerede sonuc dalgali: 6 aylik P&L'in pozitif olma orani %58-75 ama -100 ila -670 bp donemler normal.

### On-kayitli kabul kurali (OOS Sharpe >= 0.5 VE n >= 30 VE >=%60 pozitif 6 ay)
| Cift | Sharpe | n | pozitif 6 ay | Karar |
|---|---|---|---|---|
| DXY-EURUSD | 0.74 | 41 | %67 | gecti (formel) |
| DXY-GBPUSD | 0.34 | 33 | %67 | RED (Sharpe) |
| DXY-USDJPY | 0.29 | 32 | %58 | RED |
| EURGBP | 0.80 | 36 | %75 | gecti (formel) |

### Neden "gecti" demek yetmez
1. Bonferroni (4 test): tekil alfa 0.05 icin duzeltilmis esik 0.0125 (|t| >= ~2.5). OOS t-stat: DXY-EUR 1.78 (p~0.075), EURGBP 1.96 (p~0.05); hicbiri gecmiyor. 5.8 yillik veriyle Sharpe 0.5 esigi istatistiksel olarak anlamli degil.
2. DXY-EURUSD artefakt supheli (KESIF, on-kayitli degil): sinyali 1 gun daha geciktirince (t+2 getirisi) OOS Sharpe 0.74 -> 0.14, ort. islem +19 -> +3 bp. Neden: gunluk artik makasin 1. gecikme otokorelasyonu -0.34 (DXY-GBP -0.08, DXY-JPY -0.02, EURUSD-GBPUSD -0.03); gunluk sapmalar ertesi gun buyuk olcude geri donuyor. DXY'nin farkli saatte kapanmasi ve %57.6'sinin EUR olmasiyla tutarli. Gercek islemde (kapanista iki bacak) bu kazanc alinamaz. Ayni kesif: DXY-GBP lag+1 OOS Sharpe 0.12, DXY-JPY 0.20.
3. EURGBP: in-sample Sharpe 0.12 (n=48), OOS 0.80. Kural IS'te calismiyor, OOS'ta yuksek; bu istikrar degil, 2021-2025 rejiminin etkisi olabilir. Buyuk kayip donemleri var (2020H1 -674 bp). Sinyal gecikmesine dayanikli (lag+1 OOS Sharpe 0.65, t=1.58) ve 2x maliyette de 0.75: 4 testin icinde tek makul aday, ama kanitlanmis degil. DXY'ye ait degil, tek FX cross'u.
4. Buyukluk: EURGBP OOS toplam ~1528 bp / 5.8 yil = ~%2.6/yil notional (kaldiracsiz); maks dusus %3.7. 5x kaldiracla ~%13/yil, ~%18 dusus.
5. Islem sayisi OOS'ta ~6/yil; 6 aylik pencerede 2-4 islem var, kisa pencere sonuclari buyuk olcude sans.

### Bugun (2026-10-16 kapanisi)
- DXY-GBPUSD 60g-seviye z = +1.78 (son 5 gun: 2.34, 1.97, 2.29, 1.67, 1.78); beta -0.60. Kural 2026-10-09'da short makas (short DXY + short GBPUSD ~ long EURGBP) acardi; pozisyon bugun acik (5. gun), cikis icin z<=0.5 veya 20. gun beklenir. Su an yaklasik -11 bp. Yeni giris sinyali yok (|z|<2).
- EURGBP z = -2.00 (10-15; 10-16'da EURUSD verisi yok): kural long EURGBP, 10-02'den beri acik (9 gun), yaklasik -40 bp.
- DXY-EURUSD z = +0.35 (flat). DXY-USDJPY z = +1.50 (flat; son islem zaman cikisiyla -173 bp).
- "Kural ne derdi": EURGBP long; DXY-GBPUSD makasi ayri bir sinyal degil.

## 5. Sonuc (sade Turkce)
- DXY-GBPUSD makasini islem fikri olarak kullanma. Bu makas aslinda GBP'nin euro'ya gore degeri (EURGBP ile gunluk korelasyon -0.65); dolar hakkinda yeni bilgi vermiyor, ustelik DX vadelisi/CFD gerektiriyor ve iki bacak maliyeti var.
- On-kayitli testte DXY-GBPUSD (OOS Sharpe 0.34, t=0.8) ve DXY-USDJPY kaldi. DXY-EURUSD ve EURGBP formel kurali gecti ama: Bonferroni gecmiyor; DXY-EURUSD kazanci kapanis saati artefaktina benziyor (1 gun gecikmede Sharpe 0.14); EURGBP in-sample'da calismamis.
- Oneri: gercek parayla bu makasi islem yapma. Ilgini cekiyorsa tek makul aday EURGBP spot seviye mean-reversion'idir; onu bile once kagit uzerinde izle, yeni veri (2-3 yil, ~15+ islem) Sharpe ve p-degerini iyilestirirse kucuk pozisyonla dene. Onceki bulgularla (kripto pairs reddi, kosullu yon tahmini 0/10) tutarli supheci sonuc.
- Uygulanabilirlik: Turkiye'de EURGBP/DXY icin VIOP urunu dogrulayamadim (VIOP'ta USDTRY, EURTRY, EURUSD var). SPK lisansli forex kurumunda EURGBP spot teknik olarak mumkun (kaldirac 10:1 ve 50.000 TL min. teminat 2017 kuralina gore; guncel hali dogrulanmadi). Spread ~1 bp + swap, testteki 3 bp ile uyumlu. DX/Micro USDX kucuk sermaye icin buyuk/belirsiz; UUP yillik %0.75 gider, yurt disi hesap/komisyon dogrulanamadi.
- Dogrulanamayanlar: ICE metodoloji PDF'i, UUP/UDN birincil gider orani, SPK kaldirac siniri 2026 durumu, VIOP guncel sartnamesi, Turk araci kurum yurt disi ETF komisyonu, broker CFD spread/swap. CAD/SEK/CHF faizleri eksik (carry yaklasik).

## Kaynaklar
- ICE US Dollar Index Futures: https://www.ice.com/products/194
- ICE Micro USDX Futures: https://www.ice.com/products/83049912/Micro-USDX-Futures
- DXY formul/agirliklar: https://wikipedia.com/wiki/USD_Index , https://bsic.it/the-dollar-index-critical-analysis/ , https://5paisa.com/stock-market-guide/currency/what-is-dollar-index
- UUP/UDN gider orani: https://etfdb.com/etf/UUP/ , https://seekingalpha.com/symbol/UDN/expenses , https://etf.pionline.com/fund/UDN
- SPK kaldirac 2017: https://spk.gov.tr/duyurular/basin-duyurulari/2017/yatirim-hizmetleri-ve-faaliyetleri-ile-yan-hizmetlere-iliskin-esaslar-hakkinda-tebligde-iii-37-1-degisiklik-yapilmasina-dair-teblig-hakkinda
- VIOP doviz sozlesmeleri: https://www.borsaistanbul.com/files/VIOP_Doviz_Sozlesmeleri.pdf
- EURGBP spread: https://brokerchooser.com/broker-reviews/lynx-review/lynx-eurgbp-spread

## Kisa vade gorunumu (aylik)

Ayni kurallar/maliyetler (bt.py: 3 bp/bacak + yaklasik carry). Aylik net P&L = o ayin gunluk net P&L toplami (bp, notional uzerinden; giris/cikis maliyeti yarisi giris, yarisi cikis gunune yazilir). Islem = o ay GIRIS yapilan islem sayisi. 3a/6a = ayni ay dahil son 3/6 ayin toplami. 2026-10 kismi (10-16'ya kadar). Islem sayisi ayda 0-2: cogu ay P&L sifir, yani sonuc birkac islemden ibaret.

### (1) Son 24 ay: aylik net P&L, islem sayisi, yuvarlanan 3a / 6a (bp)

**DXY-EURUSD**

| Ay | Net bp | Islem | 3a | 6a |
|---|---|---|---|---|
| 2024-11 | 57 | 0 | 54 | 15 |
| 2024-12 | 11 | 1 | 65 | 29 |
| 2025-01 | 6 | 1 | 74 | 17 |
| 2025-02 | 57 | 0 | 74 | 128 |
| 2025-03 | 120 | 1 | 183 | 248 |
| 2025-04 | -43 | 1 | 134 | 208 |
| 2025-05 | 75 | 0 | 152 | 226 |
| 2025-06 | 0 | 0 | 32 | 215 |
| 2025-07 | -41 | 1 | 34 | 168 |
| 2025-08 | 17 | 0 | -24 | 127 |
| 2025-09 | 28 | 1 | 4 | 36 |
| 2025-10 | -39 | 1 | 5 | 39 |
| 2025-11 | 16 | 1 | 5 | -19 |
| 2025-12 | 18 | 0 | -5 | -2 |
| 2026-01 | -26 | 1 | 8 | 14 |
| 2026-02 | 42 | 0 | 35 | 40 |
| 2026-03 | 67 | 2 | 84 | 78 |
| 2026-04 | 57 | 0 | 166 | 174 |
| 2026-05 | 0 | 0 | 124 | 158 |
| 2026-06 | -6 | 1 | 51 | 134 |
| 2026-07 | 25 | 0 | 19 | 185 |
| 2026-08 | 0 | 0 | 19 | 142 |
| 2026-09 | 30 | 1 | 56 | 106 |
| 2026-10 | 0 | 0 | 30 | 49 |

**DXY-GBPUSD**

| Ay | Net bp | Islem | 3a | 6a |
|---|---|---|---|---|
| 2024-11 | -141 | 0 | -100 | -60 |
| 2024-12 | 0 | 0 | -100 | 1 |
| 2025-01 | 0 | 0 | -141 | -49 |
| 2025-02 | 0 | 0 | 0 | -100 |
| 2025-03 | 45 | 1 | 45 | -56 |
| 2025-04 | -124 | 0 | -79 | -220 |
| 2025-05 | 0 | 0 | -79 | -79 |
| 2025-06 | 0 | 0 | -124 | -79 |
| 2025-07 | 130 | 1 | 130 | 51 |
| 2025-08 | 0 | 0 | 130 | 51 |
| 2025-09 | 0 | 0 | 130 | 6 |
| 2025-10 | 0 | 0 | 0 | 130 |
| 2025-11 | 40 | 1 | 40 | 170 |
| 2025-12 | 0 | 0 | 40 | 170 |
| 2026-01 | 33 | 1 | 74 | 74 |
| 2026-02 | -3 | 1 | 31 | 71 |
| 2026-03 | 80 | 0 | 110 | 151 |
| 2026-04 | 0 | 0 | 77 | 151 |
| 2026-05 | 0 | 0 | 80 | 110 |
| 2026-06 | -83 | 1 | -83 | 27 |
| 2026-07 | 28 | 1 | -55 | 22 |
| 2026-08 | 0 | 0 | -55 | 25 |
| 2026-09 | 0 | 0 | 28 | -55 |
| 2026-10 | -11 | 1 | -11 | -65 |

**DXY-USDJPY**

| Ay | Net bp | Islem | 3a | 6a |
|---|---|---|---|---|
| 2024-11 | -144 | 1 | -144 | 2 |
| 2024-12 | -5 | 0 | -150 | -76 |
| 2025-01 | 191 | 1 | 41 | 117 |
| 2025-02 | 0 | 0 | 186 | 41 |
| 2025-03 | -27 | 1 | 164 | 14 |
| 2025-04 | -244 | 1 | -271 | -229 |
| 2025-05 | 94 | 0 | -177 | 8 |
| 2025-06 | -4 | 1 | -154 | 10 |
| 2025-07 | -30 | 0 | 60 | -211 |
| 2025-08 | 0 | 0 | -34 | -211 |
| 2025-09 | 86 | 1 | 56 | -98 |
| 2025-10 | 0 | 0 | 86 | 146 |
| 2025-11 | 0 | 0 | 86 | 52 |
| 2025-12 | -104 | 1 | -104 | -48 |
| 2026-01 | 24 | 0 | -80 | 6 |
| 2026-02 | 128 | 1 | 48 | 134 |
| 2026-03 | 115 | 2 | 268 | 164 |
| 2026-04 | 83 | 0 | 326 | 247 |
| 2026-05 | 0 | 0 | 198 | 247 |
| 2026-06 | 13 | 1 | 96 | 363 |
| 2026-07 | 49 | 0 | 62 | 388 |
| 2026-08 | 37 | 1 | 99 | 297 |
| 2026-09 | -37 | 1 | 49 | 145 |
| 2026-10 | -101 | 0 | -101 | -40 |

**EURGBP**

| Ay | Net bp | Islem | 3a | 6a |
|---|---|---|---|---|
| 2024-11 | 0 | 0 | -4 | 60 |
| 2024-12 | 188 | 2 | 186 | 334 |
| 2025-01 | 127 | 1 | 314 | 460 |
| 2025-02 | 0 | 0 | 314 | 311 |
| 2025-03 | 0 | 0 | 127 | 312 |
| 2025-04 | 23 | 1 | 23 | 338 |
| 2025-05 | 10 | 0 | 33 | 348 |
| 2025-06 | 0 | 0 | 33 | 160 |
| 2025-07 | 22 | 1 | 32 | 55 |
| 2025-08 | -15 | 0 | 6 | 40 |
| 2025-09 | 5 | 1 | 12 | 45 |
| 2025-10 | 57 | 1 | 47 | 79 |
| 2025-11 | -1 | 0 | 61 | 67 |
| 2025-12 | 0 | 0 | 56 | 67 |
| 2026-01 | -6 | 1 | -8 | 39 |
| 2026-02 | -41 | 0 | -47 | 13 |
| 2026-03 | 45 | 1 | -2 | 53 |
| 2026-04 | 0 | 0 | 4 | -4 |
| 2026-05 | 0 | 0 | 45 | -2 |
| 2026-06 | 0 | 0 | 0 | -2 |
| 2026-07 | -2 | 1 | -2 | 1 |
| 2026-08 | 0 | 0 | -2 | 43 |
| 2026-09 | 0 | 0 | -2 | -2 |
| 2026-10 | -40 | 1 | -40 | -42 |

### (2) Surdurulebilirlik testi: gecen 3a / 6a pozitifse ertesi ay da kazandiriyor mu? (2012-01 -> 2026-10, n ~ 172-175 ay)

Ertesi ay P&L, izleyen pencere pozitif (>0) ve negatif/sifir (<=0) iken. 'Isabet' = izleyen pencere isareti ile ertesi ay isareti ayni (sifir aylar isabetsiz sayilir, bu yuzden %50'nin altinda kalir).

| Cift | Pencere | Isabet | Poz. pencere: n, ertesi ay ort bp, % >0 | Neg. pencere: n, ertesi ay ort bp, % >0 |
|---|---|---|---|---|
| DXY-EURUSD | 3a | %47 | 119, +14.2, %55 | 56, +1.7, %38 |
| DXY-EURUSD | 6a | %48 | 119, +11.5, %55 | 53, +4.2, %36 |
| DXY-GBPUSD | 3a | %37 | 97, +10.2, %42 | 78, +2.5, %32 |
| DXY-GBPUSD | 6a | %37 | 102, +10.2, %40 | 70, +4.2, %36 |
| DXY-USDJPY | 3a | %30 | 98, -5.1, %35 | 77, +13.9, %39 |
| DXY-USDJPY | 6a | %31 | 105, +3.1, %33 | 67, +7.3, %42 |
| EURGBP | 3a | %39 | 102, +13.2, %47 | 73, +10.9, %36 |
| EURGBP | 6a | %33 | 105, -1.5, %41 | 67, +37.8, %46 |

Yorum: Surdurulebilirlik (momentum) kanit yok. Sadece DXY-EURUSD'de pozitif pencere sonrasi ertesi ay ortalamasi daha yuksek (+14 vs +2 bp; %55 vs %38 kazanan ay) - ama o cift zaten asenkron-kapanis artefakti suphelisi (Bolum 4). DXY-GBPUSD'de fark kucuk ve pozitif-pencere sonrasi bile ay kazanma orani %42 (<50%); DXY-USDJPY ve EURGBP'de iliski ters/gurultu. Edge'in 'calisirken islem yap' ile yakalanabilecegini destekleyen veri yok.

**Kural: bir cifti sadece izleyen 3a P&L > 0 ise ertesi ay islem et** (ay sonu itibariyle gecen 3a; pozitif degilse o ay flat). Aylik P&L (bp):

| Cift | Son 24 ay: kural / hep islem | Tum donem: kural / hep islem | Kuralla islem edilen ay (24 / tum) | 6 aylik bloklar son 24 ay (kural) | 6 aylik bloklar son 24 ay (hep) | Tum donem 6a bloklar pozitif: kural / hep (ort bp) |
|---|---|---|---|---|---|---|
| DXY-EURUSD | +411 / +471 | +1694 / +1880 | 21 / 119 | 151, 11, 200, 49 | 208, 39, 174, 49 | 20/30 (56) / 20/30 (63) |
| DXY-GBPUSD | -248 / -5 | +988 / +1188 | 13 / 97 | -265, 0, 110, -94 | -220, 130, 151, -65 | 14/30 (33) / 19/30 (40) |
| DXY-USDJPY | -360 / +123 | -498 / +694 | 16 / 98 | -415, 0, 95, -40 | -229, 146, 247, -40 | 11/30 (-17) / 18/30 (23) |
| EURGBP | +221 / +370 | +1345 / +2030 | 16 / 102 | 150, 79, -8, 0 | 338, 79, -4, -42 | 16/30 (45) / 19/30 (68) |

Sonuc: 'sadece calisirken islem et' filtresi hicbir ciftte hep-islem'den iyi degil (dort ciftte de tum donem ve cogunda son 24 ay daha dusuk); bunun nedeni P&L'in ay-ay bagimsiz/gurultulu olmasi, filtrenin sadece kazanc ayini kacirmasi. Dort bloktan (son 24 ay, 6'sar ay) en iyi durum hala dalgali.

### (3) Su an hangi cift 'sicak' (izleyen 3a > 0)? (2026-10, kismi ay dahil)

| Cift | 3a (bp) | 6a (bp) | Durum |
|---|---|---|---|
| DXY-EURUSD | +30 | +49 | sicak (kucuk; z=0.35, acik pozisyon yok) |
| DXY-GBPUSD | -11 | -65 | sicak degil (son aylar ters) |
| DXY-USDJPY | -101 | -40 | sicak degil (2026-04'e kadar iyiydi, son iki ay negatif) |
| EURGBP | -40 | -42 | sicak degil (long EURGBP acik pozisyon -40 bp) |

Sadece DXY-EURUSD 'sicak' ama bu cift lag+1 testinde cokuyor (Bolum 4) ve izleyen 3a'nin tamamina yakini birkac kucuk islemden. Bu bolumde de ayni sonuc: kisa vade penceresi 'calisan edge' gostermiyor; sonuclar ayda 0-2 islemle belirleniyor.

## Kripto ciftleri (kisa vade)

Ayni kurallar (bt.py run_pair: beta 250g OLS ayda bir, 60g seviye z, giris |z|>=2, cikis |z|<=0.5 / 20 gun / |z|>=4). Fark: gunluk kripto kapanisi (21:00 UTC), HAFTA SONLARI DAHIL, getiriler seviyelerden dogrudan (getiri_hesapla hafta sonu atmasi kullanilmadi); 20 "is gunu" = 20 takvim gunu. Maliyet: Binance VIP0 perpetual, 0.05% taker x 2 (giris+cikis) = ~10 bp/bacak gidis-donus; makas maliyeti 10*(1+|beta|) bp. Funding ve slippage YOK SAYILDI (funding buyuk olabilir; modelde sifir). ALTSEPET tek enstruman degil (10 perp bacak): maliyet tek bacak 10 bp sayildi ama gercekte 10 emir gerekir, kucuk sermayede pratik degil. SOL-ETH uygulanabilir alternatif. Veri: BTC/ETH ilk z 2018-05; SOL ve ALTSEPET ilk z 2021-05, yani bu iki cifte IN-SAMPLE donemi yok (hepsi 2021+). Sharpe gunluk x sqrt(252) (sqrt(365) ile isaret ayni).

### Ozet (net, 10 bp/bacak)
| Cift | Donem | n | isabet | ort net/islem (bp) | Sharpe | maks dusus (bp) | toplam (bp) |
|---|---|---|---|---|---|---|---|
| BTC-ETH | tum (2018-05+) | 68 | %46 | -160 | -0.47 | -11,892 | -10,914 |
| BTC-ETH | OOS 2021+ | 49 | %53 | -16 | -0.02 | -4,039 | -235 |
| SOL-ALTSEPET | tum (2021-05+) | 36 | %50 | -622 | -0.81 | -24,026 | -22,385 |
| SOL-ETH | tum (2021-05+) | 39 | %54 | -286 | -0.38 | -15,747 | -11,161 |

Maliyetsiz Sharpe: -0.43 / -0.78 / -0.35. Sorun maliyet degil, edge yok: kripto cift rejimlerinde |z|>=2 sonrasi trend cogu kez devam ediyor (ort. net islem -100..-600 bp).

### Son 24 ay aylik net P&L (bp) / giris sayisi / yuvarlanan 3a, 6a
BTC-ETH
| Ay | 24-11 | 24-12 | 25-01 | 25-02 | 25-03 | 25-04 | 25-05 | 25-06 | 25-07 | 25-08 | 25-09 | 25-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | 617 (1) | -43 (0) | -180 (1) | -680 (0) | 0 (0) | -990 (1) | 0 (0) | 0 (0) | -369 (1) | -992 (1) | 0 (0) | 475 (1) |
| 3a / 6a | 60/663 | -110/20 | 394/-520 | -903/-843 | -860/-971 | -1670/-1276 | -990/-1893 | -990/-1850 | -369/-2039 | -1361/-2351 | -1361/-2351 | -517/-886 |

| Ay | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | -181 (1) | -34 (0) | 245 (2) | -868 (1) | 394 (0) | 211 (2) | -488 (0) | 0 (0) | 31 (1) | 571 (1) | 532 (2) | -397 (1) |
| 3a / 6a | 294/-1067 | 260/-1101 | 30/-487 | -657/-363 | -229/31 | -264/-234 | 117/-540 | -277/-506 | -456/-720 | 602/718 | 1134/857 | 705/249 |

SOL-ALTSEPET
| Ay | 24-11 | 24-12 | 25-01 | 25-02 | 25-03 | 25-04 | 25-05 | 25-06 | 25-07 | 25-08 | 25-09 | 25-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | 858 (2) | -2528 (0) | 0 (0) | 0 (0) | 0 (0) | 313 (1) | -575 (0) | 0 (0) | 508 (1) | -177 (1) | -664 (0) | -199 (1) |
| 3a / 6a | 1083/485 | -1445/-2043 | -1670/-1498 | -2528/-1445 | 0/-1445 | 313/-1358 | -263/-2791 | -263/-263 | -67/246 | 331/69 | -332/-595 | -1039/-1106 |

| Ay | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | 1276 (1) | 0 (0) | 566 (1) | -891 (1) | 0 (0) | 0 (0) | -494 (1) | 197 (2) | 536 (0) | -652 (1) | 1094 (0) | 0 (0) |
| 3a / 6a | 414/745 | 1077/745 | 1842/803 | -325/89 | -325/752 | -891/951 | -494/-819 | -297/-622 | 240/-652 | 81/-413 | 978/681 | 442/681 |

SOL-ETH
| Ay | 24-11 | 24-12 | 25-01 | 25-02 | 25-03 | 25-04 | 25-05 | 25-06 | 25-07 | 25-08 | 25-09 | 25-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | 1437 (1) | 531 (1) | 1262 (1) | -54 (0) | 0 (0) | -322 (1) | 153 (0) | -151 (1) | 691 (2) | -624 (0) | 631 (1) | -245 (0) |
| 3a / 6a | 695/342 | 1226/-385 | 3230/1710 | 1739/2434 | 1208/2434 | -376/2854 | -169/1570 | -320/888 | 693/317 | -84/-252 | 699/379 | -237/455 |

| Ay | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net (n) | 17 (1) | -180 (1) | 0 (0) | 320 (1) | -10 (1) | -717 (0) | 0 (0) | -185 (1) | 865 (0) | 0 (0) | -222 (1) | -80 (0) |
| 3a / 6a | 403/320 | -407/291 | -163/-400 | 140/543 | 310/-98 | -407/-569 | -727/-586 | -902/-592 | 680/273 | 680/-47 | 643/-259 | -302/378 |

(*2026-10 kismi, 10-16'ya kadar. Kripto spread seviyesi gunde %5-10 oynayabildigi icin bp degerleri FX'ten ~10x buyuk; bir islem ayin sonucunu belirliyor.)

### Surdurulebilirlik (izleyen 3a / 6a isareti -> ertesi ay)
| Cift | Pencere | Isabet | Poz. pencere: n, ertesi ay ort bp, %>0 | Neg. pencere: n, ertesi ay ort bp, %>0 |
|---|---|---|---|---|
| BTC-ETH | 3a | %30 | 39, -161, %23 | 60, -50, %42 |
| BTC-ETH | 6a | %41 | 34, -96, %35 | 62, -110, %32 |
| SOL-ALTSEPET | 3a | %30 | 21, -272, %24 | 42, -397, %31 |
| SOL-ALTSEPET | 6a | %30 | 18, -433, %17 | 42, -151, %36 |
| SOL-ETH | 3a | %17 | 28, -468, %18 | 35, +55, %57 |
| SOL-ETH | 6a | %32 | 26, -279, %27 | 34, +142, %53 |

Momentum yok: pozitif 3a sonrasi ertesi ay ortalamasi her ciftte NEGATIF; SOL-ETH'de tersine donus gorunumu (pozitif pencere sonrasi %18 kazanc, negatif sonrasi %57).

### "Sadece izleyen 3a > 0 iken islem et" kurali (bp)
| Cift | Son 24 ay kural / hep | Tum donem kural / hep | Islem edilen ay (son 24 / tum) | 6a bloklar son 24 ay (kural) | (hep) | Tum donem 6a blok pozitif: kural / hep |
|---|---|---|---|---|---|---|
| BTC-ETH | -1246 / -2147 | -6278 / -10914 | 8 / 39 | -723, 0, -657, +135 | -1276, -886, -234, +249 | 3/17 / 4/17 |
| SOL-ALTSEPET | -2792 / -832 | -5709 / -22385 | 10 / 21 | -1670, -1239, -325, +442 | -1358, -1106, +951, +681 | 2/11 / 3/11 |
| SOL-ETH | -659 / +3118 | -13100 / -11161 | 13 / 28 | +1417, -868, -906, -302 | +2854, +455, -569, +378 | 2/11 / 5/11 |

Filtre BTC-ETH'de zarari azaltiyor ama pozitife cevirmiyor; digerlerinde yardimci olmuyor.

### Bugun (2026-10-16) ve "sicak" mi?
| Cift | z (kural, 60g seviye) | s12 z (20g getiri) | Acik pozisyon | 3a / 6a (bp) | Sicak (3a>0)? |
|---|---|---|---|---|---|
| BTC-ETH | +1.96 | +1.43 (Gemini ile ayni) | 10-14'te acildi, ikinci gun (-13 bp) | +705 / +249 | evet |
| SOL-ALTSEPET | -1.27 | -1.25 (Gemini ile ayni) | yok (son islem 09-05'te kapandi) | +442 / +681 | evet |
| SOL-ETH | +0.42 | +0.14 | yok (09-18 -> 10-08 zaman cikisi) | -302 / +378 | hayir |

"Sicak" = son 3 ay toplam P&L pozitif; yukaridaki testte bu ertesi ay icin sinyal degil.

### Gemini'nin %76.9 iddiasi (s12 makas_geri_donus_testi, kod degistirilmeden)
- SOL/ALTSEPET, k=2, 20g, beta makas: |z|>=2 olaylari n=13 (5g/10g/20g: 13/13/12). Kapanma orani: 5g %69.2 (9/13), **10g %76.9 (10/13)**, 20g %58.3 (7/12). Yani %76.9 = 13 olaydan 10'u, sadece 10 gunluk ufukta. Medyan kapanma 10g: +%6.2.
- Yon: SOL onde (z>=+2) olaylari n=5 ("yetersiz"), 10g/20g %100; ALTSEPET onde (z<=-2) n=8/7 (yetersiz), 20g %28.6. Iddia tek yonden ve 5 olaydan geliyor.
- Taban oran (her gun, z isareti yonunde): 5/10/20g = %51.0 / %51.0 / %50.2. |z|<1 gunleri %51/%51/%50; 1<=|z|<2 %49/%49/%53; |z|>=2 (ortusen 73/73/70 gun) %55/%56/%49. Fark 10g'de ~5 puan, 20g'de sifir. 13'te 10 icin tek yonlu binom p ~ 0.046; 3 ufuk x 3 yon x cok cift taramasi sonrasi anlamli degil.
- Ayni cift benim islem kuralimda (seviye z, maliyet dahil) Sharpe -0.81: kapanma orani karlilik demek degil.
- Karsilastirma: BTC/ETH n=29: 5g %41, 10g %59, 20g %55 (taban %49/%46/%46); SOL/ETH n=14: 5g %57, 10g %79, 20g %57.
