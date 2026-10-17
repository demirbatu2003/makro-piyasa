# Makro Pano - Veri Fizibilite Raporu (2026-10-16)

Yöntem: "Doğrulandı = evet" ise bugün (2026-10-16) tek seferlik bir istekle canlı yanıt alındı. "Hayır" ise bilgi dokümantasyon/hafızadan; test edilmedi. Hiçbir script/veri dosyası bırakılmadı.

## 1. Özet

- **Tamamen ücretsiz yapılabilir mi: büyük ölçüde evet.** Fiyat/endeks/FX/emtia/kripto için Yahoo Finance (yfinance) + Binance public API yeterli; ABD faizleri, VIX, Fed/ECB politika faizi FRED'den (key'siz CSV); politika faizleri için BIS; TCMB verileri için EVDS (ücretsiz, kayıt + API key şart).
- **Doğrulanan:** 36 Yahoo ticker'ı (günlük geçmiş), BTC/SOL intraday, 20+ FRED serisi, BIS politika faizi (9 ülke/bölge), Binance klines, CoinGecko ping/global, ECB data-api.
- **En büyük boşluklar:**
  1. Türkiye 2y/10y tahvil faizi: FRED'de yok (doğrulandı), Yahoo'da yok. Ücretsiz ve temiz kaynak bulunamadı; EVDS'de olabilir (key gerekir, doğrulanmadı).
  2. Gelişen piyasa tahvilleri (BR, IN, CN, TR 10y): FRED'deki OECD serileri (IRLTLT01xxM156N) TR/BR/IN/CN için dönmüyor (HTML hata, doğrulandı). Sadece DE, JP, ZA çalışıyor ve bunlar AYLIK.
  3. TL mevduat faizi: yalnızca EVDS (key gerekli, hafızadan). Doğrulanmadı.
  4. Gram altın TL: hazır seri yok; XAU/USD x USDTRY / 31.1035 ile hesaplanır (GC=F ve TRY=X doğrulandı). Serbest piyasa/kuyumcu makası yansımaz.
  5. Stooq artık JavaScript doğrulaması istiyor (curl HTML challenge döndü) - script ile kullanılamaz, yedek sayma.
- Intraday: kripto Binance (1m, canlı), diğerleri Yahoo (1m/5m; hisse endekslerinde ~15 dk gecikme hafızadan; borsa saatleri dışında durur).

## 2. Tablo

Yahoo günlük başlangıç tarihleri `range=max` yanıtının ilk zaman damgasıdır (bu istekte aylık nokta döndü, yani ilk gün yaklaşık; `period1/period2` ile günlük çekilir, başlangıç aynıdır).

| Varlık | Kaynak | Ticker / seri | Günlük başlangıç | Intraday / gecikme | Not | Doğrulandı |
|---|---|---|---|---|---|---|
| BTC | Binance / Yahoo | BTCUSDT / BTC-USD | Binance 2017-08; Yahoo 2014-10 | 1m, canlı (Binance) | Binance key'siz; Yahoo daha eski geçmiş | evet |
| ETH | Binance / Yahoo | ETHUSDT / ETH-USD | 2017-08 / 2017-11 | 1m canlı | | evet (Yahoo), Binance sembolü hafıza |
| SOL | Binance / Yahoo | SOLUSDT / SOL-USD | 2020-04 | 1m canlı (SOLUSDT 1m çekildi) | | evet |
| Altcoin sepeti | Binance + CoinGecko | top-N USDT paritesi, kendi endeksini hesapla; CoinGecko /global | Binance coin bazlı | canlı | CoinGecko ücretsiz API uzun geçmişi reddediyor (hata 10012, 365 gün sınırı). Hazır altcoin endeksi ücretsiz yok; eşit ağırlıklı sepeti Binance'tan kur | evet (Binance, CG ping/global) |
| USDTRY | Yahoo / TCMB | TRY=X / EVDS TP.DK.USD.A.YTL | Yahoo 2005-02 | ~canlı | TCMB resmi kuru için EVDS (key); key'siz istek boş döndü | Yahoo evet, EVDS hayır |
| EURUSD | Yahoo / ECB | EURUSD=X | 2003-12 | canlı | ECB referans kuru 1999- (hafıza) | evet |
| DXY | Yahoo | DX-Y.NYB | 1985 | ~canlı | FRED alternatifi DTWEXBGS (farklı endeks) | evet (Yahoo) |
| USDJPY | Yahoo | JPY=X | 1996-11 | canlı | FRED DEXJPUS 1971- (hafıza) | evet |
| USDCNY | Yahoo | CNY=X | 2001-07 | canlı | onshore/offshore ayrımı yok | evet |
| USDBRL | Yahoo | BRL=X | 2003-12 | canlı | | evet |
| USDINR | Yahoo | INR=X | 2003-12 | canlı | | evet |
| USDZAR | Yahoo | ZAR=X | 2003-12 | canlı | | evet |
| Altın XAU/USD | Yahoo (vadeli) | GC=F (XAUUSD=X 404 verdi) | 2000-09 | canlı (vadeli, hafta içi) | Spot ticker yok; front-month roll sıçraması içerir. FRED GOLDAMGBD228NLBM dönmüyor | evet |
| Gram altın TL | Türetilmiş | GC=F x TRY=X / 31.1035 | 2005 | canlı | Resmi seri yok; GRAMALTIN.IS 404. EVDS'de altın serisi olabilir (hafıza) | bileşenler evet |
| Gümüş | Yahoo | SI=F | 2000-09 | canlı | vadeli | evet |
| Brent | Yahoo / FRED | BZ=F / DCOILBRENTEU | Yahoo 2007-08; FRED 1987-05 | vadeli canlı | FRED günlük spot, 1 gün gecikmeli, daha uzun | evet |
| Bakır | Yahoo | HG=F | 2000-09 | canlı | COMEX vadeli | evet |
| BIST100 | Yahoo | XU100.IS | 1997-07 | ~15 dk | TRY bazlı | evet |
| S&P500 | Yahoo | ^GSPC | 1984-12 | ~15 dk; vadeli ES=F | | evet |
| Nasdaq | Yahoo | ^IXIC | 1984-11 | ~15 dk | | evet |
| DAX | Yahoo | ^GDAXI | 1987-12 | ~15 dk | | evet |
| FTSE100 | Yahoo | ^FTSE | 1985-01 | ~15 dk | | evet |
| Nikkei225 | Yahoo | ^N225 | 1984-12 | ~15 dk | | evet |
| Shanghai Comp. | Yahoo | 000001.SS | 1997-07 | gecikmeli/kırılgan | Yahoo'da bu endekste geçmiş boşluk/gecikme sorunları olabilir (hafıza) | evet (veri geliyor) |
| Hang Seng | Yahoo | ^HSI | 1986-11 | ~15 dk | | evet |
| Bovespa | Yahoo | ^BVSP | 1993-05 | ~15 dk | | evet |
| Nifty50 | Yahoo | ^NSEI | 2007-09 | ~15 dk | Yedek ^BSESN (Sensex, 1997) | evet |
| JSE Top40 | Yahoo | ^J203.JO (All Share) / STX40.JO (Top40 ETF) | 2012-03 / 2009-01 | gecikmeli | Gerçek Top40 endeksi ücretsiz yok; All Share veya ETF proxy | evet |
| ABD 2y | FRED | DGS2 | 1976-06 | günlük, ~1 gün gecikme | Yahoo'da 2y yok (^IRX 13 hf, ^FVX 5y) | evet |
| ABD 10y | FRED / Yahoo | DGS10 / ^TNX | 1962 / 1985 | ^TNX ~canlı | | evet |
| Almanya 10y | FRED | IRLTLT01DEM156N | 1956 | AYLIK | Günlük ücretsiz kaynak yok; ECB yield curve SDMX euro AAA eğrisi günlük (hafıza) | evet (aylık) |
| Japonya 10y | FRED / MOF | IRLTLT01JPM156N | 1989 | AYLIK | MOF Japan sitesi günlük CSV (hafıza) | evet (aylık) |
| Türkiye 2y/10y | EVDS (?) | key gerekir | ? | ? | Ücretsiz günlük kaynak bulunamadı; FRED TR serisi dönmedi | hayır |
| BR / IN / CN 10y | - | FRED IRLTLT01xx dönmedi | - | - | Boşluk. Investing.com/WGB scraping kırılgan, kullanım şartı sorunlu | hayır (denendi, yok) |
| G. Afrika 10y | FRED | IRLTLT01ZAM156N | 1957 | AYLIK | | evet |
| Fed funds | FRED | DFEDTARU (üst hedef) | 2008-12 | günlük | BIS ile 1954- | evet |
| ECB | FRED / ECB API | ECBDFR (mevduat) | 1999-01 | günlük | ECB data-api key'siz çalışıyor | evet |
| BoE | BIS | WS_CBPOL M.GB | 1946 | aylık/günlük | FRED IRSTCI01GBM156N piyasa faizi (1978-) | evet |
| BoJ | BIS | WS_CBPOL M.JP | 1946 | aylık/günlük | FRED INTDSRJPM193N 2017'de bitiyor | evet |
| PBoC | BIS | WS_CBPOL M.CN (LPR 1y) | 1996-01 | günlük/aylık | | evet |
| TCMB politika | BIS / EVDS | WS_CBPOL M.TR (1 haftalık repo) | 2002-02 | günlük/aylık | EVDS ayrıntılı seri (hafıza) | BIS evet |
| Brezilya Selic | BIS | WS_CBPOL M.BR | 1986-06 | günlük/aylık | BCB SGS API (seri 432) alternatif, key'siz (hafıza) | BIS evet |
| Hindistan repo | BIS | WS_CBPOL M.IN | 1946- (son veri 2026-06, gecikmeli) | | | evet |
| G. Afrika repo | BIS | WS_CBPOL M.ZA | 1980-12 | | | evet |
| TL mevduat faizi | EVDS | seri kodu doğrulanmadı | ? | haftalık | Sadece EVDS (hafıza) | hayır |
| VIX | FRED / Yahoo | VIXCLS / ^VIX | 1990 | ^VIX ~canlı | | evet |

## 3. Sorunlu kalemler ve alternatifler

- **yfinance kırılganlığı:** Resmi olmayan API; Yahoo ara sıra formatı/hız limitini değiştirir, kütüphane güncellemesi gerekir. `range=max` + günlük istekte aylık nokta dönebiliyor (bu testte noktalar az çıktı) - açık `start=` tarihi ver. Önlem: yerel cache + hata durumunda son veriyi göster.
- **Türkiye tahvil 2y/10y:** En zayıf nokta. Seçenekler: (a) EVDS key al, tahvil serilerini ara (ücretsiz); (b) TUR ETF'i risk proxy'si (USD bazlı, faiz değil); (c) TCMB politika faizi + USDTRY'yi stres göstergesi olarak kullan. Ücretli: Bloomberg/Refinitiv (bütçe dışı, fiyat araştırılmadı).
- **BR/IN/CN 10y:** Ücretsiz günlük güvenilir kaynak yok. Alternatif: para birimi + borsa + politika faizi; yield eksikliğini panoda "veri yok" göster. Scraping önerilmez.
- **DE/JP 10y günlük:** FRED'de aylık; aylık veri günlük korelasyon analizi için yetersiz. Günlük için ECB yield curve ve MOF Japan CSV (hafıza, doğrulanmadı). ^TNX tek günlük tahvil faizi referansı kalır.
- **Politika faizi geçmişi:** BIS WS_CBPOL 9 ülke/bölgede çalışıyor (doğrulandı, ücretsiz, key'siz), tek kaynak ve tutarlı. Hindistan son veri 2026-06 (gecikmeli). Basamaklı seri: getiri korelasyonu yerine "karar günü event study" için uygun.
- **Gram altın:** Hesaplanır. Vadeli roll sıçraması ve Türkiye iç piyasa primi yansımaz.
- **TL mevduat faizi:** Sadece EVDS; yoksa TCMB haftalık bülten. Günlük seri değil, korelasyonda sınırlı.
- **Shanghai / JSE:** Yahoo verisi geliyor ama kalite şüpheli (tatil boşlukları, gecikme). JSE için gerçek Top40 yok. Saat dilimi farkı: Asya/Avrupa/ABD kapanışları aynı gün hizalanmaz, lead-lag hesabında kaydırma dikkatli yapılmalı.
- **Ölü/kısıtlı kaynaklar (doğrulandı):** Stooq (bot koruması), FRED GOLDAMGBD228NLBM (dönmüyor), CoinGecko ücretsiz geçmiş (365 gün sınırı), INTDSRINM193N FRED isteği zaman aşımı, frankfurter.app eski adres 301 yönlendirme.
- **Binance:** Bazı ülkelerde api.binance.com kısıtlı olabilir; bu makinede çalıştı. Yedek: data-api.binance.vision (hafıza).
- **EVDS:** Kullanıcı kaydı elle bir kez yapmalı (evds2.tcmb.gov.tr, ücretsiz profil, API key). Key'siz istek boş döndü (doğrulandı).
- **FRED yavaşlığı:** Toplu testte bir seri timeout oldu; cache + retry koy.

## 4. Önerilen kaynak yığını (5 kaynak)

1. **yfinance (Yahoo):** tüm FX, emtia, endeksler, VIX, ^TNX, kripto yedek, TUR ETF. Günlük + intraday. Ücretsiz, key yok.
2. **Binance public klines (key'siz):** BTC/ETH/SOL + altcoin sepeti, 1m-1d, canlı nabız ekranı. CoinGecko sadece /global gibi anlık veri için.
3. **FRED CSV (fredgraph.csv?id=..., key'siz) veya pandas-datareader:** ABD 2y/10y, Fed faizi, ECB faizi, DE/JP/ZA 10y (aylık), Brent günlük, VIX uzun geçmiş.
4. **BIS WS_CBPOL (SDMX CSV):** 9 merkez bankası politika faizi (TR, BR, IN, ZA, CN, JP, US, Euro, UK) tek endpoint.
5. **TCMB EVDS (ücretsiz key):** USDTRY resmi kur, TL mevduat faizi, olası TR tahvil/altın serileri (varlığı doğrulanmadı).

Bütçe: 0 TL. Zayıf/eksik kalacaklar: TR 2y/10y tahvil (EVDS'ye bağlı), BR/IN/CN 10y, günlük DE/JP 10y, gerçek JSE Top40, hazır altcoin endeksi. Bunlar ücretli veri gerektirir; fiyatlar araştırılmadı.
