# Makro Pano — fikir taslağı (2026-10-16)

Durum: **fikir aşaması, kod yok.** Kararlar netleşince bu dosya güncellenecek.

## Amaç
Kripto, altın, döviz, TL faizleri, dünya borsaları, ülke faizleri ve haberleri tek ekranda, sürekli güncel görmek
ve **aralarındaki bağlantıları** izlemek. Trading botu değil; karar destek ve öğrenme aracı.

Ayırt edici açı: **TL bakış açısı** — her varlık hem USD hem TL bazında, TL mevduatın reel getirisiyle kıyaslı.

## Veri katmanları (önerilen kaynaklar, hepsi ücretsiz)

| Katman | Örnek | Kaynak | Güncelleme sıklığı |
|---|---|---|---|
| Kripto | BTC, ETH, top coinler, funding, stablecoin arzı | Binance / CoinGecko API | 1 dk (7/24 piyasa) |
| Döviz | USDTRY, EURTRY, DXY | Yahoo Finance, TCMB EVDS | 5-15 dk |
| Altın / emtia | XAU/USD, gram altın TL, gümüş, petrol | Yahoo Finance | 5-15 dk |
| Borsalar | BIST100, S&P500, Nasdaq, DAX, Nikkei, ... | Yahoo Finance (15 dk gecikmeli) | 15 dk, seans saatlerinde |
| Faizler | Politika faizleri, 10y tahvil faizleri, TL mevduat faizi | TCMB EVDS, FRED, merkez bankaları | Günlük |
| Haberler | Türkiye + küresel ekonomi + kripto | RSS, GDELT | 15 dk |

Not: "7/24 canlı" her katman için aynı anlamda değil. Kripto 7/24 işler, borsalar sadece seansta,
faizler ayda bir değişir. Her katman kendi doğal hızında güncellenecek.

## Bağlantı analizi (panonun asıl değeri)
- Rolling korelasyon matrisi (30/90 gün): hangi varlıklar birlikte hareket ediyor, bu ilişki değişiyor mu
- Olay işaretleri: haberler ve büyük hareketler grafik üstünde zaman çizgisinde
- Olay → tepki tablosu (event study): "BTC haftada ±%15 oynadığında diğerleri sonraki 1-30 günde ortalama ne yaptı"
- Uyarı: kısa pencerede korelasyon gürültülüdür; tek bir olaydan genelleme yapılmaz

## Fazlar (taslak)
1. Veri toplayıcı + temel pano (fiyatlar, USD/TL görünümü, reel getiri)
2. Bağlantı paneli (korelasyon, olay işaretleri)
3. Haber akışı + otomatik etiketleme
4. Event study + uyarılar (opsiyonel: Telegram)

## Kararlar (2026-10-16, kullanıcı)
- Ana amaç: **bağlantı keşfi**
- Ülkeler: Türkiye + ABD, Avrupa, Asya, gelişen piyasalar (hepsi)
- Çalışma yeri: **kendi PC** (zamanlanmış görev, statarb_hl_collect gibi)
- Haberler: **şimdilik yok** (sonraki faz)

## Bağlantı keşfi tasarımı (taslak)

Evren (~40 seri):
- Kripto: BTC, ETH, SOL, altcoin sepeti
- Döviz: USDTRY, EURUSD, DXY, USDJPY, USDCNY, USDBRL, USDINR, USDZAR
- Emtia: altın, gümüş, petrol (Brent), bakır
- Borsalar: BIST100, S&P500, Nasdaq, DAX, FTSE, Nikkei, Shanghai, Hang Seng, Bovespa, Nifty, JSE
- Faiz: ABD 2y/10y, Almanya 10y, Japonya 10y, politika faizleri (TCMB, Fed, ECB, BoJ, ...), VIX

Ekranlar:
1. Korelasyon haritası: 30/90/365 gün; "şimdi vs 1 yıl önce" farkı (hangi ilişki değişti)
2. İkili ilişki zaman çizgisi: iki varlık seç, yıllar boyu rolling korelasyon (ör. BTC–Nasdaq)
3. Ağ grafiği: güçlü bağlar çizgi, kümeler (risk-on, güvenli liman, ...)
4. Büyük hareket paneli: X 2σ+ oynadığında diğerleri aynı gün / sonraki hafta ne yaptı
5. Lead-lag: X bugün → Y yarın (saat dilimi düzeltmeli, anlamlılık testli)
6. Piyasa nabzı: bugünkü hareketler, canlı fiyatlar (kripto 7/24)

Metodoloji tuzakları:
- Fiyat değil **getiri** korelasyonu (fiyat seviyesi korelasyonu sahte çıkar)
- Saat dilimi: Asya ABD'den önce kapanır → "ABD bugün → Asya yarın" sahte öngörü gibi görünür
- 40 seri = 780 çift → bazıları şans eseri güçlü görünür; anlamlılık / çoklu test düzeltmesi
- TL bazında her şey USDTRY üzerinden birbirine bağlanır → bağlantılar USD (veya yerel para) bazında,
  TL görünümü ayrı
- Korelasyon nedensellik değildir

Frekans: bağlantı analizi **günlük** veriyle yapılır (10-20 yıl geçmiş Yahoo/FRED'den hemen çekilebilir,
beklemeye gerek yok). Dakikalık canlı güncelleme sadece "piyasa nabzı" ekranı için.

## Açık kararlar
- Arayüz: Streamlit (statarb dashboard'undaki gibi) önerilir
