# Makro Pano - Tasarım Belgesi (v1 taslağı, 2026-10-16)

Durum: **yalnızca tasarım, kod yok.** Kaynaklar: `FIKIR.md` (kararlar), `arastirma/veri_fizibilite.md` (veri), `arastirma/benzer_araclar.md` (ekran ve metodoloji önerileri). Bu belge onlarla çelişirse onlar geçerlidir; belirsiz yerler Bölüm 7'de açık soru olarak duruyor.

---

## 1. Amaç ve kapsam dışı olanlar

Makro Pano, kullanıcının kendi Windows PC'sinde çalışan, ücretsiz kaynaklarla beslenen, **varlıklar arası bağlantıları keşfetmek ve öğrenmek** için kurulmuş yerel bir Streamlit panosudur. Kripto, FX, emtia, dünya borsaları, faizler ve VIX'i tek veri setinde toplar; hangi varlıkların birlikte hareket ettiğini, bu ilişkinin zamanla ve rejime göre nasıl değiştiğini gösterir. Her ekran korelasyonun nedensellik olmadığını ve örnek büyüklüğünü açıkça belirtir. Ayırt edici açı: Türkiye'deki yatırımcı için **yerel para / USD bazı geçişi** ve gram altın / USDTRY perspektifi. Bu bir karar destek ve öğrenme aracıdır; sinyal üretmez.

Kapsam dışı (v1 ve genel):
- Trading botu, al-sat sinyali, pozisyon / alım-satım önerisi, "şunu al" türü metin. Yok.
- Haberler, RSS, GDELT, haber etiketleme (sonraki faz; v1-v3 içinde de yok, ayrı karar gerekir).
- Otomatik "bulaşma / kriz" yorumu üretmek.
- DCC-GARCH, Diebold-Yilmaz, wavelet (v3 sonrası, gerekirse).
- Ücretli veri, scraping (Investing.com, WGB vb.), Stooq (bot koruması nedeniyle kullanılamıyor).
- Gelişen piyasa 10y tahvilleri (BR / IN / CN) ve TR 2y/10y günlük serisi (ücretsiz güvenilir kaynak yok; TR yalnız EVDS'den sonra, o da doğrulanmadı).
- Bulut barındırma, çok kullanıcılı erişim, Telegram uyarıları (v1'de yok).
- Bu belge kod, veri indirme veya kurulum içermez.

---

## 2. Varlık evreni

"v1'de mi" sütunu: **evet** = v1'de toplanır ve günlük korelasyon hesabına girer; **evet (bağlam)** = toplanır ama günlük korelasyon matrisine girmez; **EVDS sonrası** = kullanıcı EVDS API key'ini alınca eklenir; **hariç** = ücretsiz güvenilir kaynak yok.
Kodların tamamı `veri_fizibilite.md`'den alınmıştır. Frekans "G" = günlük.

### 2.1 Kripto

| Kategori | Varlık | Kaynak | Ticker / seri | Frekans | v1'de mi | Not |
|---|---|---|---|---|---|---|
| Kripto | BTC | Binance (ana) / Yahoo (yedek, uzun geçmiş) | BTCUSDT / BTC-USD | G + 1m nabız | evet | Binance 2017-08, Yahoo 2014-10; uzun geçmiş için Yahoo |
| Kripto | ETH | Binance / Yahoo | ETHUSDT / ETH-USD | G + 1m nabız | evet | Binance sembolü hafızadan, ilk çalıştırmada doğrulanacak |
| Kripto | SOL | Binance / Yahoo | SOLUSDT / SOL-USD | G + 1m nabız | evet | Geçmiş 2020-04'ten |
| Kripto | Altcoin sepeti | Binance | top-N USDT paritesi, kendi hesabımız | G | evet | Eşit ağırlıklı, kendi kurduğumuz endeks; N ve seçim kuralı açık soru (Bölüm 7). CoinGecko uzun geçmiş vermiyor (365 gün sınırı) |

### 2.2 Döviz

| Kategori | Varlık | Kaynak | Ticker / seri | Frekans | v1'de mi | Not |
|---|---|---|---|---|---|---|
| FX | USDTRY | Yahoo | TRY=X | G | evet | Yahoo 2005-02. Resmi TCMB kuru EVDS'de (`TP.DK.USD.A.YTL`), kuruluşta key'siz boş döndü |
| FX | USDTRY resmi (TCMB) | EVDS | TP.DK.USD.A.YTL | G | EVDS sonrası | Yahoo ile çapraz kontrol amaçlı |
| FX | EURUSD | Yahoo | EURUSD=X | G | evet | |
| FX | DXY | Yahoo | DX-Y.NYB | G | evet | FRED alternatifi DTWEXBGS farklı endeks, kullanılmaz |
| FX | USDJPY | Yahoo | JPY=X | G | evet | |
| FX | USDCNY | Yahoo | CNY=X | G | evet | Onshore/offshore ayrımı yok |
| FX | USDBRL | Yahoo | BRL=X | G | evet | |
| FX | USDINR | Yahoo | INR=X | G | evet | |
| FX | USDZAR | Yahoo | ZAR=X | G | evet | |

### 2.3 Emtia

| Kategori | Varlık | Kaynak | Ticker / seri | Frekans | v1'de mi | Not |
|---|---|---|---|---|---|---|
| Emtia | Altın XAU/USD | Yahoo (vadeli) | GC=F | G | evet | Spot yok (XAUUSD=X 404). Front-month roll sıçraması içerir |
| Emtia | Gram altın TL | Türetilmiş | GC=F x TRY=X / 31.1035 | G | evet | Resmi seri yok; kuyumcu / serbest piyasa makası yansımaz. İki bileşenin ortak tarih kesişiminde hesaplanır |
| Emtia | Gümüş | Yahoo | SI=F | G | evet | Vadeli |
| Emtia | Brent | Yahoo / FRED | BZ=F / DCOILBRENTEU | G | evet | Ana: BZ=F (diğer vadelilerle aynı saat mantığı); FRED DCOILBRENTEU uzun geçmiş için, 1 gün gecikmeli spot |
| Emtia | Bakır | Yahoo | HG=F | G | evet | COMEX vadeli |

### 2.4 Borsalar

| Kategori | Varlık | Kaynak | Ticker / seri | Frekans | v1'de mi | Not |
|---|---|---|---|---|---|---|
| Borsa (TR) | BIST100 | Yahoo | XU100.IS | G | evet | TRY bazlı; USD bazı USDTRY ile hesaplanır |
| Borsa (ABD) | S&P500 | Yahoo | ^GSPC | G | evet | Vadeli ES=F (v1'de kullanılmaz) |
| Borsa (ABD) | Nasdaq | Yahoo | ^IXIC | G | evet | |
| Borsa (Avrupa) | DAX | Yahoo | ^GDAXI | G | evet | |
| Borsa (Avrupa) | FTSE100 | Yahoo | ^FTSE | G | evet | |
| Borsa (Asya) | Nikkei225 | Yahoo | ^N225 | G | evet | |
| Borsa (Asya) | Shanghai Comp. | Yahoo | 000001.SS | G | evet | Veri kalitesi şüpheli (boşluk / gecikme); sağlık şeridinde izlenir |
| Borsa (Asya) | Hang Seng | Yahoo | ^HSI | G | evet | |
| Borsa (GOP) | Bovespa | Yahoo | ^BVSP | G | evet | |
| Borsa (GOP) | Nifty50 | Yahoo | ^NSEI | G | evet | Yedek ^BSESN (Sensex) |
| Borsa (GOP) | JSE | Yahoo (proxy) | ^J203.JO (All Share) / STX40.JO (Top40 ETF) | G | evet (proxy) | Gerçek Top40 endeksi ücretsiz yok; hangisinin ana olacağı ilk veri kalite kontrolünde seçilir (All Share 2012-03, ETF 2009-01) |

### 2.5 Faizler, politika faizleri, VIX

| Kategori | Varlık | Kaynak | Ticker / seri | Frekans | v1'de mi | Not |
|---|---|---|---|---|---|---|
| Faiz | ABD 2y | FRED | DGS2 | G (~1 gün gecikme) | evet | getiri yerine bp değişim |
| Faiz | ABD 10y | FRED (+Yahoo canlı) | DGS10 / ^TNX | G | evet | Günlük analizde DGS10; ^TNX yalnızca nabız ekranında |
| Faiz | Almanya 10y | FRED | IRLTLT01DEM156N | **Aylık** | evet (bağlam) | Günlük korelasyona girmez; yalnız yavaş / bağlam görünümü |
| Faiz | Japonya 10y | FRED | IRLTLT01JPM156N | **Aylık** | evet (bağlam) | Aynı |
| Faiz | G. Afrika 10y | FRED | IRLTLT01ZAM156N | **Aylık** | evet (bağlam) | Aynı |
| Faiz | Türkiye 2y / 10y | EVDS (?) | seri kodu bilinmiyor | ? | EVDS sonrası | EVDS'te varlığı doğrulanmadı; bulunamazsa "hariç" kalır |
| Faiz | Brezilya / Hindistan / Çin 10y | - | FRED IRLTLT01xx dönmedi | - | hariç | Panoda "veri yok" olarak gösterilir, scraping yok |
| Faiz | TL mevduat faizi | EVDS | seri kodu doğrulanmadı | Haftalık | EVDS sonrası | Günlük korelasyonda sınırlı; reel getiri paneli için |
| Politika faizi | Fed | FRED / BIS | DFEDTARU (üst hedef) / WS_CBPOL (US) | G / aylık | evet (olay) | Rolling korelasyon yok, olay günü analizi |
| Politika faizi | ECB | FRED | ECBDFR (mevduat) | G | evet (olay) | |
| Politika faizi | BoE | BIS | WS_CBPOL M.GB | aylık/G | evet (olay) | |
| Politika faizi | BoJ | BIS | WS_CBPOL M.JP | aylık/G | evet (olay) | |
| Politika faizi | PBoC (LPR 1y) | BIS | WS_CBPOL M.CN | aylık/G | evet (olay) | |
| Politika faizi | TCMB (1 haftalık repo) | BIS | WS_CBPOL M.TR | aylık/G | evet (olay) | EVDS'te daha ayrıntılı seri var (doğrulanmadı) |
| Politika faizi | Brezilya Selic | BIS | WS_CBPOL M.BR | aylık/G | evet (olay) | |
| Politika faizi | Hindistan repo | BIS | WS_CBPOL M.IN | aylık/G | evet (olay) | Son veri 2026-06, gecikmeli; sağlık şeridinde işaretlenir |
| Politika faizi | G. Afrika repo | BIS | WS_CBPOL M.ZA | aylık/G | evet (olay) | |
| Rejim | VIX | FRED (uzun) / Yahoo (nabız) | VIXCLS / ^VIX | G | evet | Rejim tanımında VIXCLS kullanılır |

Not: BIS politika faizleri tek endpoint (WS_CBPOL, 9 ülke/bölge); basamaklı serilerdir. Sürekli rolling korelasyon hesaplanmaz.

Günlük korelasyon evreni (v1): kripto 4 + FX 8 (USDTRY dahil, EURUSD, DXY, JPY, CNY, BRL, INR, ZAR) + emtia 5 (gram altın dahil) + borsa 11 + faiz 2 (DGS2, DGS10) + VIX = **yaklaşık 31 seri**. Çift sayısı 465 civarıdır; çoklu test kuralları Bölüm 5'te.

---

## 3. Veri hattı

### 3.1 Toplama sıklığı
- **Günlük geçmiş:** günde bir kez (öneri: Türkiye saatiyle 08:00, yani ABD kapanışından ve FRED güncellemesinden sonra) Windows Task Scheduler görevi yfinance, FRED CSV, BIS ve Binance 1d kline'larını çeker. Açık `start=` tarihi verilir (`range=max` aylık nokta döndürebiliyor).
- **Kripto intraday nabız:** Binance 1m / 1h kline, yalnızca "Piyasa nabzı" ekranı ve sabit saat hizalama için. Saatlik zamanlanmış görev (statarb_hl_collect gibi). Diğer varlıklar için intraday v1'de saklanmaz; nabız ekranında Yahoo'dan o an çekilen (~15 dk gecikmeli) değer "canlı" değil "gecikmeli" etiketiyle gösterilir ve veri tabanına yazılmaz (canlı veri ile tarihsel veriyi karıştırmama kuralı).
- **Aylık seriler** (DE/JP/ZA 10y, BIS): haftada bir kontrol yeterli.
- Arayüz (Streamlit) veri toplamaktan bağımsızdır; yalnızca saklanan veriyi okur.

### 3.2 Saklama: SQLite (tek dosya)
**Seçim: tek bir SQLite dosyası** (`makro-pano\veri\makro.sqlite`).
Gerekçe:
- Günlük seriler küçük (31 seri x ~20 yıl x 250 gün = birkaç yüz bin satır); parquet'in sütunlu performans avantajına ihtiyaç yok.
- Upsert (aynı tarihi güncelle) ve "son tarihten sonrasını ekle" işlemleri SQL ile basit ve atomik; parquet'te dosya yeniden yazmak gerekir, yarım yazma riski var.
- Veri sağlığı için ek tablolar (son çekim zamanı, hata günlüğü) aynı dosyada durur; Streamlit tek bağlantıyla okur.
- Kullanıcı kod bilmiyor: tek dosya yedeklemek (kopyala) kolay.
- Kripto 1m verisi sadece son N gün tutulur (öneri 30 gün), dosya şişmez; ihtiyaç olursa ayrı bir dosya.

Tablolar (kavramsal): `seri_katalog` (kod, ad, kaynak, kategori, frekans, kapanış saati notu, v1 bayrağı), `gunluk` (seri, tarih, kapanış, çekim_zamanı), `kripto_nabiz` (sembol, zaman, fiyat), `cekim_gunlugu` (kaynak, seri, başlangıç, sonuç, hata metni), `politika_olaylari`.

Ham kapanış saklanır; log-getiri ve korelasyon hesapları okuma anında yapılır (ham veriyi bozmamak için).

### 3.3 Eksik gün telafisi
- PC kapalıyken kaçan günler için görev "boşluk doldurma" mantığıyla çalışır: her seri için veri tabanındaki son tarihi bulur, o tarihten (3 gün geri bindirmeyle, revizyonlar için) bugüne kadar olanı çeker.
- Zamanlanmış görev "kaçırılan çalıştırmayı mümkün olan en kısa sürede başlat" seçeneğiyle kurulur; ayrıca Streamlit açıldığında veri yaşı eşiği aşıyorsa kullanıcıya "Güncelle" düğmesi gösterilir.
- Binance 1m verisi geçmişe dönük çekilebilir (kline başlangıç zamanı verilir), bu yüzden intraday de bir süre kapalı kalma sonrası doldurulabilir; sınırı 1000 mum / istek olduğundan parça parça çekilir.
- Doldurulamayan boşluk kalırsa (kaynak vermiyorsa) silent değil, sağlık şeridinde "eksik: tarih aralığı" olarak yazılır.

### 3.4 Saat dilimi ve kapanış hizalama kuralı
- Tüm zaman damgaları UTC saklanır; günlük seriler **yerel seans takvim tarihi** ile anahtarlanır (örn. Nikkei 2026-10-16 seansı = 2026-10-16).
- Her seriye `seri_katalog`'ta yaklaşık kapanış saati notu eklenir (Asya erken, Avrupa orta, ABD en geç; kripto 7/24; FX ~24/5; vadeliler kendi seans kapanışı).
- Günlük korelasyon matrisi: takvim tarihine göre **ikili tam gözlem** (pairwise complete); her hücrenin yanında ortak gözlem sayısı tutulur. Bir tarafın tatil olduğu günler o çiftte düşer (zorla doldurma / ileri taşıma yok).
- Kripto günlük getirisi UTC 00:00 kapanışı yerine mümkünse **sabit saat referansı** kullanır: v1 varsayılanı Binance 1h kline'dan 21:00 UTC mumu (ABD kapanışına yakın; yaz saati kayması notu ekranda). Bu yaklaşım asenkronluğu azaltır, tam çözmez; bu bir açık soru değil varsayılan kuraldır, ama değiştirilebilir.
- Lead-lag ekranında t-1, t, t+1 gecikmeleri her zaman birlikte gösterilir; ayrıca haftalık (örtüşmeyen 5 günlük) getiri seçeneği.
- Faizler (FRED) 1 gün gecikmeli yayımlanabilir; bu serilerin "son gözlem tarihi" ayrı tutulur, eksik son günler için tahmin / doldurma yapılmaz.

### 3.5 Hata yönetimi
- Her kaynak çağrısı: zaman aşımı + 3 deneme, artan bekleme (FRED yavaşlığı ve yfinance hız limiti için). Seri bazında izole: bir seri çökerse diğerleri devam eder.
- Başarısız seri son iyi veriyle gösterilir, sağlık şeridinde kırmızı işaret ve son başarılı güncelleme zamanı yazılır; bozuk veri üzerine yazılmaz.
- Doğrulama kontrolleri (yazmadan önce): tarih tekrarı, tarihin geleceğe uzanması, fiyat <= 0, tek günde ±%50 üzeri getiri (şüpheli işaretlenir, silinmez, kullanıcı görür).
- yfinance kırılırsa (kütüphane güncellemesi gerekir): ana sayfada "kaynak X çalışmıyor" uyarısı; Claude'un kütüphaneyi güncellemesi ayrı bir bakım işi (kullanıcıdan komut istemez).
- Binance: api.binance.com engellenirse yedek `data-api.binance.vision` (hafızadan, ilk kurulumda doğrulanacak) ve Yahoo kripto yedeği.
- Tüm hatalar `cekim_gunlugu` tablosuna ve düz metin log dosyasına yazılır (kullanıcı kod bilmediği için sağlık sayfasında okunabilir).
- Anahtar yönetimi: EVDS key'i, kullanıcının makine ortam değişkeninde / yerel ayar dosyasında tutulur; depoya veya belgeye yazılmaz.

### 3.6 Konum: kripto-veri mi, makro-pano mu?
**Öneri: makro verisi `C:\Users\batuh\makro-pano\veri\` altında ayrı kalsın, `C:\Users\batuh\kripto-veri\` içine karışmasın.** Gerekçe: farklı kaynak / sıklık / yaşam döngüsü, makro-pano silinirse veya taşınırsa tek klasör; kripto-veri büyük ve statarb ile paylaşılan bir arşiv, orada dosya karışıklığı riski var. Yapılacak iki şey: (a) `kripto-veri\VERI_KATALOGU.md`'ye makro-pano'nun veri yolunu gösteren tek satırlık not eklemek (katalog kuralına uymak için; yalnızca kullanıcı onaylarsa); (b) kripto-veri'de BTC/ETH/SOL günlük verisi zaten varsa, makro-pano onu **kopyalamaz**, ilk kurulumda karşılaştırma yapıp yapmama kararı açık soru olarak bırakılır (varsayılan: makro-pano kendi Binance çekimini yapar, bağımsız kalır; içeriği şu an kontrol edilmedi).

---

## 4. Ekranlar

Sayfa sırası (sol menü, yukarıdan aşağı): 0 Genel Bakış ve Veri Sağlığı, 1 Korelasyon Haritası, 2 İkili İlişki, 3 Ağ ve Kümeler, 4 Rejim ve Beta, 5 Büyük Hareket (Event Study), 6 Lead-Lag, 7 Piyasa Nabzı, 8 Yavaş / Bağlam (aylık seriler ve politika faizleri).

Ortak kontroller her sayfada sol kenar çubuğunda: tarih aralığı, para birimi bazı (USD / yerel para / TL), pencere (60g / 250g), varlık sınıfı filtresi. Ortak üst şerit: **veri sağlığı şeridi** (son güncelleme zamanı, eksik / bayat seri sayısı, kırmızı uyarı). Her sayfanın altında "Bu sayfayı nasıl okumalı" kutusu ve sabit nedensellik uyarısı bulunur.

### Ekran 0 - Genel Bakış ve Veri Sağlığı
- **Amaç:** Verinin güvenilir olup olmadığını ve panonun nasıl okunacağını göstermek.
- **Gösterir:** seri başına son tarih, bayatlık (gün), toplam gözlem, eksik tarih sayısı, son çekim hatası; kaynak durumu (yfinance, Binance, FRED, BIS, EVDS "kurulmadı"); veri yok olan kalemler (BR/IN/CN 10y, TR tahvil) açıkça "veri yok" olarak listelenir.
- **Kontroller:** "Şimdi güncelle" düğmesi, bayat eşik (varsayılan 3 iş günü).
- **Metodoloji notu:** Shanghai ve JSE kalite şüphesi, Hindistan repo gecikmesi burada işaretlenir.
- **Uyarı metni:** "Bu pano bir bağlantı keşfi ve öğrenme aracıdır; al-sat önerisi değildir. Gösterilen ilişkiler geçmiş veriye aittir, gelecekte devam etmeyebilir ve nedensellik göstermez."

### Ekran 1 - Korelasyon Haritası
- **Amaç:** Hangi varlıklar birlikte hareket ediyor ve bu son bir yılda nasıl değişti.
- **Gösterir:** üç yan yana panel: "şimdi" matrisi, "1 yıl önce" matrisi, **fark matrisi** (şimdi - 1 yıl önce). Satır / sütunlar hierarchical clustering sırasına göre dizilir. 60g ve 250g pencereler yan yana. Ortak gözlem sayısı yetersiz hücreler gri. Tek sayı özet: ortalama ikili korelasyon (kısa vs uzun).
- **Kontroller:** pencere çifti (60g / 250g), karşılaştırma tarihi (varsayılan 1 yıl önce), baz (USD / yerel), korelasyon türü (Spearman varsayılan, Pearson seçenek), varlık sınıfı filtresi, fark matrisinde yalnız istatistiksel olarak ayırt edilebilir değişimleri göster.
- **Metodoloji notu:** log-getiri (faizlerde bp değişim); çiftler tam gözlem; ~465 çiftte şans eseri büyük değerler beklenir; "keşif" listesi değil harita.
- **Uyarı metni:** "465 çiftten bir kısmı yalnızca şans eseri güçlü görünür. Kısa pencere (60g) gürültülüdür; 250g ile birlikte okuyun. Korelasyon nedensellik değildir."

### Ekran 2 - İkili İlişki
- **Amaç:** İki varlığın ilişkisinin yıllar içindeki seyri (örn. BTC-Nasdaq, USDTRY-BIST100).
- **Gösterir:** 60g ve 250g rolling korelasyon aynı grafikte, kaba güven bandı, yüksek VIX dönemleri gölgeli; altta iki varlığın normalize fiyat çizgisi; yanında tek sayılık beta ve ortak gözlem sayısı.
- **Kontroller:** iki varlık seçici, baz (USD / yerel), pencere, tarih aralığı, korelasyon türü.
- **Metodoloji notu:** güven bandı yaklaşık (Fisher z); örtüşen pencereler olduğundan bant bağımsız gözlem varsayar, gerçekte daha geniştir.
- **Uyarı metni:** "Rolling korelasyon örtüşen pencerelerle hesaplanır; yan yana duran noktalar bağımsız değildir. Bant yaklaşıktır."

### Ekran 3 - Ağ ve Kümeler
- **Amaç:** Varlıkların hangi kümelerde toplandığını okunur biçimde görmek (risk-on, güvenli liman, vb. kullanıcı yorumuyla).
- **Gösterir:** Spearman tabanlı **MST** (düğüm rengi = varlık sınıfı, kenar kalınlığı = korelasyon) ve yanında **dendrogram**. İki zaman noktası yan yana; değişen kenarlar vurgulu; kenar kararlılığı yüzdesi (pencereler arasında kaç kez aynı kenar).
- **Kontroller:** zaman noktası 1 ve 2, pencere, baz, varlık sınıfı filtresi.
- **Metodoloji notu:** mesafe d = sqrt(2(1-rho)); MST yalnız n-1 kenar gösterir ve çoğu ilişkiyi gizler.
- **Uyarı metni:** "Ağaçta kenar yok demek 'bağlı değil' demek değildir; yalnızca en güçlü ve ağaç yapısına uyan bağlar çizilir."

### Ekran 4 - Rejim ve Beta
- **Amaç:** Korelasyonun VIX rejimine göre değişimini ve duyarlılığı (büyüklüğü) göstermek.
- **Gösterir:** (a) VIX düşük / orta / yüksek rejime koşullu korelasyon matrisleri (yan yana), (b) **beta tablosu**: seçilen referans varlığın (S&P500, DXY, USDTRY, BTC vb.) %1 hareketine karşı diğerlerinin ortalama tepkisi, standart hata ve gözlem sayısıyla.
- **Kontroller:** referans varlık, rejim eşikleri (Bölüm 5), pencere, baz.
- **Metodoloji notu:** kriz dönemi korelasyon artışının bir kısmı mekanik olarak volatilite artışından gelir (Forbes-Rigobon), bu düzeltme tartışmalıdır; ekranda düzeltme uygulanmaz, rejimler ayrı gösterilir.
- **Uyarı metni:** "Yüksek VIX rejiminde korelasyonların yükselmesi 'bulaşma' kanıtı değildir; kısmen volatilite artışının ölçüm etkisidir. Rejim başına gözlem sayısı azsa sonuç güvenilmezdir."

### Ekran 5 - Büyük Hareket (Event Study)
- **Amaç:** "X 2σ+ oynadığında diğerleri aynı gün ve sonraki günlerde ne yaptı."
- **Gösterir:** t+0, t+1, t+5 için medyan getiri, dağılım (çeyrekler), olay sayısı n, hedef varlıkların tabloda sıralanması; n küçükse "yetersiz veri" etiketi. Politika faizi karar günleri için ayrı sekme (olay bazlı).
- **Kontroller:** tetikleyici varlık, yön (yukarı / aşağı / her ikisi), eşik (σ katı), σ penceresi, ardışık olayları ayıklama süresi.
- **Metodoloji notu:** σ yalnız geçmiş veriyle (ex-ante, kayan) hesaplanır; çakışan olaylar ayıklanır; aynı gün ve sonraki gün ayrı gösterilir.
- **Uyarı metni:** "Olay sayısı küçükse medyan anlamsızdır. Tek bir olaydan genelleme yapılmaz; sonuçlar sonraki dönemde tekrar doğrulanmadan 'kural' sayılmamalıdır."

### Ekran 6 - Lead-Lag (sınırlı)
- **Amaç:** Ekonomik olarak mantıklı çiftlerde gecikmeli ilişki var mı.
- **Gösterir:** t-3...t+3 çapraz korelasyon çubuk grafiği, her gecikme için güven aralığı ve n; kapanış saati notu (iki varlığın yaklaşık kapanış saatleri yan yana).
- **Kontroller:** çift seçici (önerilen çift listesi: örn. ABD -> Avrupa / Asya borsaları, DXY -> gelişen piyasa FX, BTC -> Nasdaq), frekans (günlük / haftalık örtüşmeyen), baz.
- **Metodoloji notu:** Granger testi ve benzeri v1'de yok; ilk fazda yalnız gecikmeli çapraz korelasyon. Tüm çiftleri tarayıp "en iyi lead-lag"ı listelemek yok.
- **Uyarı metni:** "Asya ABD'den önce kapandığı için 'ABD bugün, Asya yarın' görünümü çoğu zaman saat farkından kaynaklanır, öngörü değildir."

### Ekran 7 - Piyasa Nabzı
- **Amaç:** Bugünün özet resmi; sade.
- **Gösterir:** birkaç sayı: ortalama ikili korelasyon (60g vs 250g), VIX, DXY, USDTRY, BTC-S&P500 60g korelasyonu, her birinin tarihsel yüzdelik dilimi ("olağan dışı" bayrağı); kripto için Binance'tan son fiyat ve son 24 saat hareketi; diğer varlıklar için gecikmeli son değer (etiketli).
- **Kontroller:** yenile düğmesi, TL / USD bazı.
- **Metodoloji notu:** canlı değer ile tarihsel veri aynı yerde karıştırılmaz; canlı değer veri tabanına yazılmaz.
- **Uyarı metni:** "Kripto dışındaki fiyatlar ~15 dk gecikmeli ve yalnız seans saatlerinde güncellenir. 'Olağan dışı' bayrağı bir işlem sinyali değildir."

### Ekran 8 - Yavaş / Bağlam
- **Amaç:** Günlük analize giremeyen yavaş serileri bağlam olarak göstermek.
- **Gösterir:** DE / JP / ZA 10y (aylık) zaman çizgisi ve aylık getiri / bp değişimle aylık korelasyon (n küçük uyarısı); politika faizi karar tarihleri çizgisi, ilgili ülkenin FX ve borsası üstüne bindirilmiş; TL mevduat faizi ve reel getiri paneli (EVDS sonrası, v2).
- **Kontroller:** ülke seçici, tarih aralığı.
- **Metodoloji notu:** adım serilerde sürekli rolling korelasyon yok; olay bazlı bakılır.
- **Uyarı metni:** "Aylık seriler günlük serilerle doğrudan karşılaştırılamaz. Örnek sayısı küçüktür."

---

## 5. Metodoloji kuralları

**Getiri tanımları**
- Fiyat serileri: günlük log-getiri r = ln(P_t / P_{t-1}). Fiyat seviyesi korelasyonu hiçbir ekranda gösterilmez.
- Faizler (DGS2, DGS10, aylık 10y'ler): günlük / aylık bp değişim (Δy x 100, y yüzde cinsindeyse). VIX: log-değişim (rejim tanımı için seviye).
- Politika faizleri: korelasyona girmez; karar günleri olay olarak işlenir.
- Gram altın: GC=F x TRY=X / 31.1035, log-getirisi hesaplanır; bu seri USDTRY'ye mekanik bağlıdır (kendi ekranlarında not).

**Baz (para birimi)**
- Varsayılan analiz **USD bazı** (TL her şeyi USDTRY üzerinden birbirine bağladığı için). Yerel para borsalar için yerel getiri ve USD getirisi (yerel getiri + kur getirisi) anahtarı; Türkiye için TL görünümü ayrı. Yerel / USD sonuç farkı büyükse ekranda belirtilir.
- Kur dönüşümü yalnızca verisi olan borsa-kur çiftlerinde (BIST100/USDTRY, Nikkei/JPY=X, DAX/EURUSD=X, FTSE/GBP: **GBPUSD ticker'ı raporlarda yok, v1'de FTSE yerel bazda kalır veya ticker doğrulanınca eklenir**, Bovespa/BRL=X, Nifty/INR=X, JSE/ZAR=X, Shanghai ve Hang Seng için CNY=X; Hang Seng HKD gerektirir, raporlarda yok, yerel baz kalır).

**Pencereler**
- Kısa 60 işlem günü ve uzun 250 işlem günü yan yana; tek pencere sunulmaz. Minimum ortak gözlem: 60g pencere için 40, 250g için 150; altında hücre gri.
- Fark modu: "şimdi" = son pencere, "karşılaştırma" = 250 işlem günü önce biten aynı uzunlukta pencere (varsayılan).
- Event study σ penceresi: 60 gün kayan, yalnız geçmiş veri.

**Korelasyon türü**
- Varsayılan Spearman (MST ve uç değerlere dayanıklılık); Pearson seçenek. Uç değerler için ayrıca winsorize seçeneği (varsayılan kapalı).
- EWMA (lambda 0.94-0.97) v2'de ekran 2 için üçüncü bir çizgi olarak değerlendirilir.

**Anlamlılık ve çoklu test**
- Her korelasyon ortak gözlem sayısı n ile birlikte gösterilir; yaklaşık %95 güven aralığı Fisher z ile (örtüşen pencere uyarısıyla).
- Matris ekranında "anlamlı" boyaması yok; bunun yerine n yetersizse gri. Çoklu test: ~465 çiftte %5 düzeyinde ~23 şans eseri bulgu beklendiği açıkça yazılır.
- Sıralı "en yüksek korelasyonlar" listesi yalnız FDR (Benjamini-Hochberg) düzeltmesinden sonra ve "keşif listesi" etiketiyle, ayrıca bölünmüş örneklemde (ilk yarı / ikinci yarı) tekrarlanan bulgular işaretlenerek gösterilir; v1'de bu liste yerine yalnız harita sunulur, liste v2'ye ertelenir.
- Lead-lag: yalnız ekonomik olarak mantıklı önceden tanımlı çiftler; bulgu sonraki dönemde tekrar test edilmeden "kural" sayılmaz.
- Event study: n < 20 ise "yetersiz veri"; çakışan olaylar ayıklanır.

**Rejim tanımı (VIX)**
- VIXCLS'e göre, tarihsel yüzdelik dilim: düşük = alt %33, orta = %33-67, yüksek = üst %33 (tam geçmiş üzerinden; **bakış-ileri sızıntı notu:** tam örneklem yüzdeliği ileriye bakar; v1 varsayılanı sabit mutlak eşik: düşük < 15, orta 15-25, yüksek > 25, kullanıcı değiştirebilir). Her rejimde minimum 60 gün gözlem aranır.
- Rejimler ayrı gösterilir; birleştirme / "bulaşma" yorumu yok.

**Kısa açıklama metinleri (arayüze konacak)**
- Korelasyon, iki serinin birlikte hareket etme eğilimidir; biri diğerine neden olduğunu göstermez. Ortak bir üçüncü etken (USD, risk iştahı) iki seriyi birlikte oynatabilir.
- Korelasyon sabit değildir; kriz ve rejim değişimlerinde bozulabilir.
- Gram altın ve TL bazlı her şey USDTRY'den etkilenir; TL bazında ilişki yükselmesi çoğu zaman TL faktörüdür.
- Asenkron kapanış sahte öngörü üretebilir.

---

## 6. Fazlar ve kabul kriterleri

### v1 - Veri hattı + keşif panosu (yalnız doğrulanmış kaynaklar)
**Kapsam:** yfinance, Binance public klines, FRED CSV, BIS WS_CBPOL. Bölüm 2'deki "evet" ve "evet (bağlam)" serileri. Ekranlar 0-8 (Ekran 8'in TL mevduat kısmı hariç). SQLite, günlük + saatlik zamanlanmış görevler, boşluk doldurma, sağlık şeridi. EVDS için sadece yer: `seri_katalog`'ta "EVDS sonrası" bayraklı satırlar ve ayar dosyasında boş key alanı; kod yolu key yoksa sessizce atlar.

**Bitti neye benziyor:**
1. Tüm "evet" serileri veri tabanında, en az 10 yıllık (Yahoo / FRED'in verdiği kadar) günlük geçmişle yüklü; her serinin ilk çalıştırma raporu (başlangıç tarihi, gözlem sayısı, eksik gün) Ekran 0'da görünüyor.
2. PC 3-5 gün kapalı bırakıldıktan sonra görev çalıştığında eksik günler otomatik dolduruluyor (elle müdahale yok); doldurulamayan boşluk varsa sağlık şeridinde yazıyor.
3. Bir kaynak kasıtlı olarak bozulduğunda (ör. ağ kapalı) pano çökmüyor, son iyi veriyi gösteriyor ve uyarı veriyor.
4. Ekran 1 fark modu, 60g / 250g yan yana ve ortak gözlem sayılı gri hücrelerle çalışıyor; hiçbir ekranda fiyat seviyesi korelasyonu yok.
5. Bilinen ilişkiler sağduyu testinden geçiyor (örn. S&P500-Nasdaq yüksek pozitif, DXY-EURUSD negatif, VIX-S&P500 negatif); geçmezse hata aranır.
6. Gram altın serisi elle hesapla (GC=F x TRY=X / 31.1035) bir iki tarihte tutuyor.
7. Her ekranda uyarı metni ve nedensellik notu var; "al/sat" ifadesi hiçbir yerde yok.
8. BR/IN/CN 10y ve TR tahvil "veri yok" olarak dürüstçe listeli.
9. Kullanıcı, Claude'un yardımı olmadan panoyu başlatıp kapatabiliyor (tek çift tıklanan başlatıcı; kurulum sonrası kullanıcıya tek sayfalık Türkçe kullanım notu).

### v2 - EVDS, TL perspektifi, derinleşme
Kapsam: EVDS key geldikten sonra USDTRY resmi kur, TL mevduat faizi, olası TR tahvil / altın serileri (varlığı kontrol edilir); reel getiri paneli (TL mevduat vs enflasyon vs varlık getirileri; enflasyon serisinin kaynağı henüz belirlenmedi); EWMA korelasyon; FDR düzeltmeli "keşif listesi"; log-getiri için bölünmüş örneklem tekrar testi; FTSE / Hang Seng için kur bazı ticker'ları doğrulanıp eklenir.
**Bitti:** EVDS serileri sağlık şeridinde yeşil, TR serilerinin gerçekten var olup olmadığı kayıt altında (yoksa "hariç" kesinleşir); TL perspektifi sayfası USD / TL anahtarıyla tutarlı; keşif listesi bölünmüş örneklemde tekrarlanmayanları işaretliyor.

### v3 - Olgunlaştırma
Kapsam: Telegram / yerel uyarı (opsiyonel), daha zengin lead-lag (kullanıcı onaylarsa), ağ ekranında zaman içinde kenar kararlılığı animasyonu, yedek kaynaklar (ECB yield curve, MOF Japan günlük CSV gibi hafızadan bilinen günlük DE/JP 10y alternatifleri **doğrulandıktan sonra**), haber fazı için ayrı tasarım belgesi.
**Bitti:** en az 6 ay kesintisiz çalışma kaydı; kırılan kaynak sayısı ve düzeltme süresi kayıtlı; haber fazı kararı kullanıcıya sunulmuş.

DCC-GARCH ve Diebold-Yilmaz: bu fazların dışında; ancak kullanıcı v2 sonrası açıkça isterse ve basit yöntemlerin yetmediği gösterilirse.

---

## 7. Kullanıcıya açık sorular

1. **Altcoin sepeti nasıl kurulsun?** Seçenekler: Binance'ta hacme göre ilk N USDT paritesi, ya da sabit bir liste. **Önerilen varsayılan:** sabit liste, N = 10, eşit ağırlık, listeye girenler başlangıç tarihleri farklıysa sepet yalnızca o tarihte verisi olan coinlerle hesaplanır; hayatta kalma yanlılığı (bugün büyük olanları seçmek) ekranda uyarı olarak yazılır.
2. **Başlangıç tarihi / geçmiş uzunluğu?** Çoğu seri 2000'lerden önce başlıyor ama kripto 2017/2020. **Önerilen varsayılan:** tüm seriler için 2010'dan itibaren (uzun geçmiş, ama kriptoda ortak gözlem kısa kalır; ekran bunu n ile gösterir). Daha uzun istersen toplama süresi ve veri boyutu artar.
3. **Kripto günlük kapanış referansı.** UTC 00:00 mi, yoksa borsa kapanışına yakın sabit saat (21:00 UTC) mı? **Önerilen varsayılan:** 21:00 UTC (asenkronluğu azaltır); istersen ikisi arasında ekran anahtarı olur.
4. **Zamanlanmış görevlerin saatleri ve PC'nin açık kalma düzeni.** PC günde ne zaman açık? **Önerilen varsayılan:** günlük toplama 08:00 (Türkiye saati), kripto nabzı saatlik; PC kapalıysa açıldığında kaçırılan görev çalışsın. Bu, statarb_hl_collect ve statarb_paper görevleriyle aynı PC'de çakışmayacak biçimde ayrı bir görev adı alır.
5. **Makro verisinin konumu.** `makro-pano\veri\` içinde ayrı mı kalsın, yoksa `kripto-veri\` altına mı gitsin? Ayrıca BTC/ETH/SOL için kripto-veri'deki mevcut arşive bağlanıp bağlanmama. **Önerilen varsayılan:** makro-pano içinde ayrı, kripto-veri'ye dokunma; yalnız `VERI_KATALOGU.md`'ye makro-pano yolunu gösteren bir satır eklemek için onayın.

Not (soru değil, bekleyen bilgi): EVDS API key'i alınması elle yapılmalı (evds2.tcmb.gov.tr, ücretsiz profil). v1 key'e bağlı değildir; key geldiğinde v2 başlar. Bu belge Türkiye tahvil 2y/10y ve TL mevduat serilerinin EVDS'te gerçekten bulunacağını varsaymaz.
