# Arayüz düzeltme listesi

Kullanıcının verdiği işler. **Şimdi yapılmayacak**, en sonda topluca yapılacak (kullanıcı söyleyince).

## Genel bakış / Veri sağlığı (Ekran 0)
1. ✅ yapıldı (2026-10-17) - Zaman damgalarındaki `T` harfini kaldır, yerine boşluk koy (`2026-10-17 10:10:32Z`). `Z` kalabilir.
2. ✅ yapıldı (2026-10-17) - UTC zamanın yanına Türkiye saatini de ekle (UTC+3).
3. ✅ yapıldı (2026-10-17) - "Bayat eşik" ifadesi kötü bir Türkçe çeviri: İngilizcesi (staleness threshold) yazılsın ya da kaldırılsın. Aynı şey "bayatlık" sütunları için de geçerli.

## Korelasyon Haritası (Ekran 1)
5. ✅ yapıldı (2026-10-17) - Haritalar çok küçük ve okunmuyor. Tıklayınca büyüsün (yeni pencere ya da yerinde büyütme). Ayrıca varsayılan boyut da büyütülsün.
6. ✅ yapıldı (2026-10-17) - Haritalarda x ve y eksenindeki varlık isimleri geri planda kalıyor ve zor okunuyor: yazıları büyüt ve kalınlaştır (tam ekranda da okunaklı olsun). Hücre içi sayılar da okunaklı olsun.

7. ✅ yapıldı (2026-10-17) - Harita büyütülünce (Büyük göster / tam ekran) kapatınca eski haline dönmüyor, sayfa "sıçıyor" (kaydırma konumu atlıyor). Düzelt.
8. ✅ yapıldı (2026-10-17) - Korelasyon haritalarında zoom/pan'e izin verme; plotly araç çubuğundaki zoom vb. butonları kaldır.
9. ✅ yapıldı (2026-10-17) - Soldaki (y ekseni) bir varlığa tıklayınca o varlığın tüm satırı seçilsin/vurgulansın, takip kolay olsun. Kullanıcı: "Vurgula" seçim kutusu OLMASIN; sadece haritada tıklayınca vurgulansın (hücre ya da mümkünse soldaki isim).

## Varlık bilgi kartları (Genel bakış + Korelasyon haritası)
11. ✅ yapıldı (2026-10-17) Kullanıcı varlıkların çoğunu bilmiyor. Bir varlığa tıklayınca küçük bir buton çıksın, butona basınca o varlığın detaylı bilgi kartı açılsın: ne olduğu (ör. ALTSEPET nedir), alınıp satılabilir mi (doğrudan mı, ETF/vadeli üzerinden mi, hiç mi), nerede işlem gördüğü (borsa/platform, saatler), Türkiye'den nasıl erişilir, neyi etkiler / neden panoda. Tüm ~45 seri için. Mevcut ajan bitince başlanacak (aynı dosyalara dokunuyor).

## Kavramlar sayfası (yeni)
12. ✅ yapıldı (2026-10-17) - Yeni sayfa "Kavramlar". SADECE kullanıcının verdiği kavramlar (kendiliğinden ekleme yok): VIX, beta, korelasyon, Spearman, Pearson, normalize, Fisher (Fisher z). Her biri detaylı, sade Türkçe açıklama + matematiği (formül) + panodan örnek. Kullanıcı yeni kavram verdikçe eklenecek.

## Yeni varlıklar
13. BIST30 endeksini ekle (toplayıcı + katalog + bilgi kartı + panolar). Yahoo kodu muhtemelen XU030.IS, doğrulanacak. ŞİMDİ YAPMA, kullanıcı söyleyince.

## İkili İlişki (Ekran 2)
14. Tarih aralığı seçici şu an sadece grafiği kırpıyor; korelasyon hep son 60g/250g. İstenen: seçilen tarih aralığının TAMAMI için tek bir korelasyon (+ n, Fisher %95 aralığı, beta) gösterilsin; ayrıca aralık seçici daha görünür olsun ve hazır kısayollar (son 1 ay / 3 ay / 1 yıl / 3 yıl / tümü) eklensin. Opsiyonel: pencere uzunluğu (60/250 dışında, örn. 20/120) seçilebilsin. ŞİMDİ YAPMA (Gemini repo üzerinde çalışıyor), kullanıcı söyleyince.

## Yeni istatistikler (GPT önerisinden seçilenler)
15. Kısmi korelasyon (partial correlation): iki varlık arasındaki ilişkiyi seçilen kontrol değişken(ler)i (örn. DXY, SPX) çıkarıldıktan sonra göster. "Gerçek bağ mı, ortak sebep mi?" Hem ikili ilişki sayfasında (kontrol seçimi) hem mümkünse matris olarak.
16. Kriz anı ilişkisi: sert düşüş günlerinde (örn. bir varlığın alt %10 günleri) korelasyon / ortak düşüş oranı vs normal günler. Quantile regression yerine anlaşılır "exceedance correlation / downside correlation" versiyonu.
17. Rolling beta'nın zaman içindeki grafiği (şu an sadece son değer gösteriliyor), güven bandıyla.
(Atlananlar: Kendall Tau, Granger, Mutual Information, Cointegration — gerekçe sohbette.) ŞİMDİ YAPMA: Gemini bitince, kullanıcı söyleyince tek paket.

## Hatalar
10. ✅ yapıldı (2026-10-17) - KÖK NEDEN: masaüstü .bat'ın siyah konsol penceresi kapatılınca sunucu ölüyordu ('Connection error'); ek: okumalar DB'ye yazıyordu, nabız yazımı tüm önbelleği geçersiz kılıyordu (giderildi). Pano 5-10 dk açık kaldıktan sonra hata veriyor (2026-10-17). Hata metni kullanıcıdan bekleniyor. Şüphe: oku.katalog() her okumada DB'ye yazıyor → saatlik nabız göreviyle "database is locked" çakışması; ya da uyku/bağlantı kopması.

## Tüm sayfalar
4. ✅ yapıldı (2026-10-17) - "Bu pano bir bağlantı keşfi ve öğrenme aracıdır; al-sat önerisi değildir. Gösterilen ilişkiler geçmiş veriye aittir, gelecekte devam etmeyebilir ve nedensellik göstermez." yorumunu her sayfadan tamamen kaldır.
