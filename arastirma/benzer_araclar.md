# Cross-asset "bağlantı keşfi" panoları: benzer araçlar ve en iyi uygulamalar

Tarih: 2026-10-16. Yalnızca araştırma. Kaynak notu: [W] = bu oturumda web aramasıyla doğrulandı; [B] = genel bilgi / akademik literatür, bu oturumda doğrulanmadı. Koyfin, MacroMicro ve Bloomberg CORR/WCRS için arama sonuç vermedi; bu satırlar zayıf teyitli.

## 1) Özet

- Hazır araçlar çoğunlukla tek şey yapıyor: seçilen sepet için korelasyon matrisi + ikili rolling çizgi. "Şimdi vs 1 yıl önce" farkı, event-study ve lead-lag birleşimi hazır bir üründe yaygın görünmedi; bu pano için fark yaratabilir (aramamız sınırlı, kesin iddia değil).
- Profesyonellerin sık kullandığı şeyler sade [B]: rolling korelasyon (kısa + uzun pencere), beta, VIX rejimine koşullu korelasyon, eşik tabanlı koşullu getiri tabloları. Ağ grafikleri ve DCC-GARCH akademide yaygın, günlük karar ekranı olarak nadir.
- En büyük tuzak asenkron kapanış: ABD ve Asya borsaları aynı takvim gününde aynı saatte kapanmıyor; naif hizalama sahte lead-lag üretir. Gecikmeli (t-1, t, t+1) korelasyonlar birlikte gösterilmeli, kapanış saati notu eklenmeli.
- Korelasyon fiyat seviyesinde değil log-getiri (faiz/verimde bp değişim) üzerinde hesaplanmalı. TradingView'daki iyi göstergeler de log-return kullanıyor [W].
- Kriz dönemi korelasyon artışının bir kısmı volatilite artışının mekanik sonucu (Forbes-Rigobon), ama bu düzeltme de tartışmalı [W]. Otomatik "bulaşma" yorumu yapılmamalı; rejime göre ayrı göster.
- Pencere seçimi sonucu belirler: 60g ve 250g yan yana göstermek en ucuz ve dürüst çözüm. Çok çiftli taramada çoklu test sorunu var (50 varlık = 1225 çift).
- TRY için yerel para vs USD bazı sonucu kökten değiştirebilir; her ikisi de gösterilmeli [B].
- Kod bilmeyen, küçük bütçeli kullanıcı için DCC-GARCH ve Diebold-Yilmaz ilk faza girmemeli; rolling + EWMA yeterli ve açıklanabilir. MST için Spearman tercih [W].

## 2) Araç / proje tablosu

| İsim | Ücretsiz/ücretli | Ne gösteriyor | Bizim için fikir | Link |
|---|---|---|---|---|
| Portfolio Visualizer (Asset Correlations) [W, ikincil kaynak] | Ücretsiz katman (üçüncü taraf incelemeye göre ~25 varlık), ücretli üst katman | Korelasyon matrisi, tarih ve "correlation basis" seçimi, rolling korelasyon grafiği, autocorrelation, cointegration | Tarih seçici + matris + rolling çizgi üçlüsü; autocorrelation sekmesi lead-lag için ilham | https://algotrading101.com/learn/portfolio-visualizer-guide/ |
| TradingView: Correlation Matrix [AFD] | Ücretsiz (open-source script) | Grafik sembolünü 8 enstrümanla kıyaslar; yavaş/hızlı korelasyon, çift geçmişi, ortak gözlem yeterlilik bayrağı | İki pencere + veri yeterliliği uyarısı | https://id.tradingview.com/script/tqf4eAaM-Correlation-Matrix-AFD/ |
| TradingView: Crypto Correlation Dashboard [StrixEDGE] | Ücretsiz | Log-return korelasyonu, seçili çift için rolling çizgi | Log-return zorunlu; ikili timeline | https://in.tradingview.com/scripts/multi-asset/ |
| TradingView: Market Correlation Matrix [NikaQuant] | Ücretsiz | Altın, SPX, DXY, US10Y, QQQ gibi referanslara karşı canlı Pearson ve değişim | Küçük referans sepeti yaklaşımı | https://www.tradingview.com/script/eJcg3ndc-Market-Correlation-Matrix-NikaQuant/ |
| Koyfin, MacroMicro | Ücretsiz katman + ücretli [B] | Seri overlay ve ilişki grafikleri sunduğu biliniyor; bu oturumda doğrulanamadı | Kendi sitelerinden kontrol edilmeli | https://www.koyfin.com , https://en.macromicro.me |
| Bloomberg terminal (CORR/WCRS benzeri ekranlar) | Çok pahalı | Çapraz varlık korelasyon ekranları; fonksiyon adları doğrulanamadı | Ulaşılamaz; yalnız "profesyoneller de matris + rolling kullanıyor" referansı | doğrulanamadı |
| Mantegna MST yaklaşımı (Bonanno, Caldarelli, Lillo, Mantegna 2003) [W] | Akademik | Korelasyondan mesafe, minimum spanning tree; kümeler/hiyerarşi | Tam ağdan okunaklı; zamanla izlenebilir | https://arxiv.org/pdf/1703.00485 |
| Rank-correlation MST (arXiv 2005.03963) [W] | Akademik | Spearman/Kendall ile MST, Pearson'dan daha kararlı | MST'yi Spearman ile kur | https://ar5iv.labs.arxiv.org/html/2005.03963 |
| Diebold-Yilmaz connectedness [W] | Akademik | VAR varyans ayrıştırmasından "kimden kime" spillover tablosu ve toplam bağlantılılık endeksi | İleri faz: kim yayıcı, kim alıcı | https://eaf.ku.edu.tr/wp-content/uploads/2022/11/erf_wp_2207.pdf |
| Forbes-Rigobon "No Contagion, Only Interdependence" [W] | Akademik | Kriz korelasyonunun volatilite yanlılığı düzeltmesi | Kriz karşılaştırmalarında uyarı notu | https://www.nber.org/papers/w7267 |
| Nazir ve ark. 2021, DCC-GARCH vs rolling (Asya Shariah endeksleri) [W] | Akademik | DCC-GARCH volatilite değişimini rolling'den iyi yakalıyor (küçük, bölgesel çalışma) | Tek başına kanıt zayıf; DCC ileri faz | https://ejournal.unimap.edu.my/index.php/amci/article/download/174/141 |
| GitHub Streamlit/Dash makro panoları | - | Aramada somut repo bulunamadı [W] | Hazır şablon yok; Plotly + networkx + pandas ile kurulur | bulunamadı |

## 3) Gerçekten işe yarayan ekranlar ve metrikler

İşe yarayanlar [B]:
- Rolling korelasyon (kısa 60g + uzun 250g birlikte), çiftin zaman çizgisi.
- Beta / duyarlılık ("SPX %1 düşünce BTC ortalama ne yaptı"): korelasyondan daha eyleme dönük, çünkü büyüklüğü verir.
- Rejime koşullu korelasyon: VIX yüksek/düşük ya da piyasa düşerken. Çeşitlendirmenin en gerektiği anda bozulması en pratik bulgu.
- Event-study: eşik hareketi sonrası t+0, t+1, t+5 medyan getiri ve örnek sayısı. n küçükse açıkça belirt.
- Ortalama ikili korelasyon (tek sayı): "piyasa ne kadar tek faktörlü" göstergesi.

Gösterişli ama karar değeri düşük olabilenler:
- Tam bağlı ağ grafiği (hairball). MST veya eşik üstü kenarlar şart.
- Sıralanmamış büyük heatmap; kümeye göre sıralama (hierarchical clustering order) şart.
- Seviye (fiyat) korelasyonu; tek uzun pencere.
- DCC-GARCH çıktıları: yorumu ve bakımı zor, marjinal kazanç kanıtı zayıf.

## 4) Metodoloji tuzakları ve çözümleri

1. Asenkron kapanış. Tokyo/Avrupa/ABD farklı saatte kapanır; kripto 7/24, FX yaklaşık 24/5. Naif gün-sonu hizalaması "Asya ABD'yi önceki gün izliyor" gibi sahte lead-lag verir. Çözüm: (a) t-1, t, t+1 gecikmelerini birlikte göster (Dimson tarzı); (b) kripto/FX için borsa kapanışına en yakın sabit saat fiyatı; (c) çok günlük (örtüşmeyen) getiriler asenkronluğu azaltır ama gözlemi düşürür; (d) her sonuca kapanış saati notu [B].
2. Fiyat vs getiri. Seviye serileri trend taşır; korelasyon sahtedir. Log-getiri kullan [W]; faiz/verimde bp değişim.
3. Çoklu test / sahte korelasyon. 1225 çiftte %5 düzeyinde ~60 şans eseri bulgu beklenir. Çözüm: ekonomik olarak mantıklı hipotezlere odaklan, güven aralığı ve örnek sayısı göster, lead-lag bulgusunu sonraki dönemde tekrar test et, gerekirse FDR düzeltmesi [B].
4. Kriz dönemi. Volatilite artınca ölçülen korelasyon mekanik olarak yükselir (Forbes-Rigobon); düzeltme de eleştirildi (Corsetti ve ark., Pesaran-Pick) ve sonraki uygulamalarda sonuçlar karışık [W]. Çözüm: korelasyonu VIX rejimine göre ayrı göster; otomatik "bulaşma" yorumu yok.
5. DCC-GARCH vs rolling. Bulduğumuz tek doğrudan karşılaştırma küçük ve bölgesel, DCC lehine [W]; rolling pencere 150-300 gün aralığında benzer sonuç veren bir çalışma var [W]. Öneri: EWMA korelasyon (lambda ~0.94-0.97) basit orta yol [B]; DCC ileri faz. DCC de asenkronluğu çözmez [B].
6. MST. Spearman/Kendall daha kararlı ağaç verir [W]. MST yalnız n-1 kenar gösterir, çoğu ilişkiyi gizler; "bağlı değil" anlamına gelmez. Pencereler arası kenar sürekliliğini (kararlılık %) raporla [B].
7. Yerel para vs USD. USD getirisi = yerel getiri + kur getirisi; ortak USD faktörü korelasyonu değiştirir. TRY için özellikle belirgin. Her ülke borsası için yerel/USD anahtarı; Türkiye'li kullanıcı için ikisini yan yana göster [B].
8. Veri hijyeni: tatil günleri, eksik veri (ortak gözlem sayısını göster), uç değerler (Spearman veya winsorize), politika faizi gibi seyrek değişen adım serilerinde rolling korelasyon anlamsız; olay bazlı bak [B].

## 5) Planlanan ekranlar için öneriler

Rolling korelasyon haritası (şimdi vs 1 yıl önce): TUT, DEĞİŞTİR
- İki matrisin yanında fark matrisi (şimdi - 1 yıl önce). Kümeye göre sırala. Ortak gözlem yetersizse hücreyi gri yap. 60g ve 250g seçeneği.

İkili rolling korelasyon zaman çizgisi: TUT
- 60g ve 250g aynı grafikte, yüksek VIX dönemleri gölgeli. Yerel/USD anahtarı. Kaba güven bandı.

Ağ / küme grafiği: DEĞİŞTİR
- Tam ağ yerine Spearman tabanlı MST; düğüm rengi = varlık sınıfı, kenar kalınlığı = korelasyon. Yanında dendrogram. İki zaman noktasını yan yana göster, değişen kenarları vurgula; kararlılık yüzdesi.

Event-study ("X 2σ hareket ettiğinde"): TUT, KURALLARLA
- σ ex-ante (kayan) hesaplansın, bakış-ileri sızıntısı olmasın. Medyan + dağılım (yalnız ortalama değil), örnek sayısı, aynı gün/ertesi gün ayrımı, çakışan olayları ayıkla. n küçükse "yetersiz veri".

Lead-lag testi: SINIRLA
- Önce gecikmeli çapraz korelasyon (t-3...t+3) çubuk grafiği; asenkronluk notu zorunlu. Ekonomik olarak mantıklı çiftlerle başla. Granger gibi testleri ilk fazda ekleme.

Canlı piyasa nabzı: TUT, SADE
- Birkaç sayı: ortalama ikili korelasyon (kısa vs uzun), VIX, DXY, USD/TRY, BTC-SPX korelasyonu; tarihsel yüzdelik dilimiyle "olağan dışı" bayrağı.

EKLE:
- VIX rejimine koşullu korelasyon matrisi.
- Beta/duyarlılık tablosu.
- Yerel/USD anahtarı ve veri sağlığı şeridi (son güncelleme, eksik veri).

ERTELE / ÇIKAR:
- DCC-GARCH, Diebold-Yilmaz, wavelet.
- Seviye (fiyat) korelasyonu; politika faizleri için sürekli rolling korelasyon.

Anti-pattern listesi:
- Otomatik "bulaşma/kriz" yorumu üretmek.
- Tek pencere, tek sayı, güven bandı yok.
- Çok sayıda çiftte en yüksek korelasyonu "keşif" diye sunmak.
- Kapanış saati farkını yok sayıp günlük getiriyi doğrudan hizalamak.
- Okunmayan hairball ağ, sıralanmamış büyük heatmap.
- Canlı veriyi tarihsel veriyle farklı kaynak/saatle karıştırmak.

## Kaynaklar
- Mantegna MST ve inceleme: https://arxiv.org/pdf/1703.00485
- Rank-correlation MST: https://ar5iv.labs.arxiv.org/html/2005.03963
- Korelasyon ağları ve entropi: https://arxiv.org/pdf/2004.09448
- Forbes-Rigobon: https://www.nber.org/papers/w7267
- Diebold-Yilmaz retrospektif: https://eaf.ku.edu.tr/wp-content/uploads/2022/11/erf_wp_2207.pdf
- DCC vs rolling (Nazir ve ark. 2021): https://ejournal.unimap.edu.my/index.php/amci/article/download/174/141
- Rolling pencere duyarlılığı (DCCA): https://arxiv.org/pdf/2408.17200
- Portfolio Visualizer rehberi: https://algotrading101.com/learn/portfolio-visualizer-guide/
- TradingView: https://id.tradingview.com/script/tqf4eAaM-Correlation-Matrix-AFD/ , https://in.tradingview.com/scripts/multi-asset/ , https://www.tradingview.com/script/eJcg3ndc-Market-Correlation-Matrix-NikaQuant/

Sınırlılık: Web araması sınırlıydı; Koyfin/MacroMicro/Bloomberg doğrulanamadı; açık kaynak Streamlit/Dash örnek repo bulunamadı. [B] etiketli maddeler genel bilgidir, kullanmadan önce kontrol edilmelidir.
