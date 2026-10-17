"""Kavramlar sayfasının içeriği. Yeni kavram eklemek için KAVRAMLAR listesine bir sözlük ekleyin.

Alanlar (hepsi markdown metni; 'canli' hariç isteğe bağlı):
  id        : kısa benzersiz anahtar
  baslik    : sekme ve başlık adı
  kisa      : içindekiler için tek cümle
  ne        : ne olduğu
  neden     : neden önemli / piyasada nasıl kullanılır
  okuma     : nasıl okunur (değer aralıkları)
  formuller : st.latex ile gösterilecek LaTeX satırları (liste)
  semboller : [(sembol, anlam), ...]
  not_      : formülle ilgili kısa uyarı (isteğe bağlı)
  ornek     : adım adım küçük örnek hesap (markdown)
  panoda    : [str, ...] panoda nerede kullanıldığı
  iliski    : [str, ...] diğer kavramlarla ilişki
  canli     : s9_kavramlar.py içindeki CANLI sözlüğünde bir anahtar (yoksa boş bırakın)
"""

KAVRAMLAR = [
    {
        "id": "vix",
        "baslik": "VIX",
        "kisa": "ABD borsasında önümüzdeki 30 günde beklenen dalgalanmanın ölçüsü; 'korku endeksi'.",
        "ne": (
            "VIX (CBOE Volatility Index), S&P 500 endeksi opsiyonlarının fiyatlarından türetilen, önümüzdeki 30 gün için "
            "**beklenen (implied) volatilite**dir ve yıllık yüzde olarak ifade edilir. Geçmişte ne olduğunu değil, "
            "opsiyon piyasasının önümüzdeki dönem için ne beklediğini gösterir.\n\n"
            "Gündelik benzetme: hava durumu tahmini gibi düşünün. Bugün yağmur yağıp yağmadığına değil, yağmur "
            "ihtimaline bakıyorsunuz. Opsiyon alıcıları 'sigorta' ödüyor; piyasa endişelendikçe bu sigorta pahalanır ve "
            "VIX yükselir. Bu yüzden ona 'korku endeksi' denir.\n\n"
            "VIX doğrudan alınıp satılamaz, çünkü bir fiyat hesabıdır. Ona maruz kalmak için VIX vadelileri (futures), "
            "VIX opsiyonları veya bunlara dayanan ETP'ler kullanılır."
        ),
        "neden": (
            "Piyasada risk iştahının en bilinen göstergelerinden biridir. Hisse senedi düşerken VIX genelde yükselir "
            "(ters ilişki), bu yüzden stres anlarında portföy korunması ve risk limitleri için izlenir. "
            "Pozisyon büyüklüğü ayarlamak, 'piyasa sakin mi gergin mi' sorusunu cevaplamak ve rejimleri ayırmak için kullanılır.\n\n"
            "Bir çıkarım da yapılabilir: VIX 20 ise piyasa bir yıl için yaklaşık %20 standart sapmalı "
            "hareket bekliyor demektir. Bunu zamana indirmek için karekök kuralı kullanılır (aşağıda)."
        ),
        "okuma": (
            "Kabaca okuma (kesin sınırlar değildir, bu panodaki eşiklerle uyumludur):\n\n"
            "- **15'in altı:** sakin piyasa, düşük korku.\n"
            "- **15 - 25:** normal dalgalanma.\n"
            "- **25'in üstü:** gergin piyasa; 30-40 ve üstü ciddi stres (2008 ve Mart 2020 gibi dönemlerde 60-80 görüldü).\n\n"
            "Örnek yorum: VIX = 20 ise piyasa yıllık yaklaşık %20 volatilite bekliyor. Günlük karşılığı "
            "20 / √252 ≈ %1,26; aylık karşılığı 20 / √12 ≈ %5,8 olur. Bu 1 standart sapmadır; yani hareketin yaklaşık "
            "%68 olasılıkla bu bandın içinde kalması beklenir (normal dağılım varsayımı; gerçekte kuyruklar daha kalındır)."
        ),
        "formuller": [
            r"\mathrm{VIX} \approx 100 \times \sqrt{\sigma^2}",
            r"\sigma^2 \approx \frac{2}{T}\sum_i \frac{\Delta K_i}{K_i^2}\, Q(K_i)",
            r"\text{günlük} \approx \frac{\mathrm{VIX}}{\sqrt{252}}, \qquad \text{aylık} \approx \frac{\mathrm{VIX}}{\sqrt{12}}",
        ],
        "semboller": [
            ("σ²", "30 günlük beklenen varyans (opsiyon fiyatlarından çıkarılır)."),
            ("T", "vadeye kalan süre (yıl cinsinden; VIX için 30 gün)."),
            ("K_i", "i. opsiyonun kullanım (strike) fiyatı."),
            ("ΔK_i", "komşu strike'lar arasındaki aralık."),
            ("Q(K_i)", "o strike'taki out-of-the-money opsiyonun (put veya call) piyasa fiyatı."),
            ("100", "sonucu yüzde puana çevirir."),
        ],
        "not_": (
            "Önemli not: yukarıdaki formül basitleştirilmiş bir özettir. CBOE'nin gerçek hesabı daha ayrıntılıdır "
            "(iki vadeyi 30 güne interpole eder, faiz ve forward düzeltmesi içerir, belirli strike'ları seçer). "
            "Ana fikir: opsiyon fiyatları varyans swap tipi bir ağırlıklandırmayla (1/K²) toplanır, "
            "karekökü alınır ve 100 ile çarpılır."
        ),
        "ornek": (
            "Küçük örnek (formülün kendisini değil, okumayı gösterir):\n\n"
            "1. VIX = 20 olsun.\n"
            "2. Yıllık beklenen volatilite = %20.\n"
            "3. Bir yılda ~252 işlem günü var, günlük = 20 / √252 = 20 / 15,87 ≈ %1,26.\n"
            "4. Bir ay = 1/12 yıl, aylık = 20 / √12 = 20 / 3,46 ≈ %5,8.\n"
            "5. Sonuç: piyasa, S&P 500 için bir ayda yaklaşık ±%5,8'lik tipik bir hareket fiyatlıyor."
        ),
        "panoda": [
            "**4 Rejim ve Beta:** VIX seviyesine göre üç rejim kurulur: `< 15` sakin, `15 - 25` normal, `> 25` gergin. "
            "Eşikler sayfadaki iki kutudan değiştirilebilir (varsayılan 15 ve 25). Eşikler sabit mutlak değerdir; "
            "yüzdelik kullanılsaydı geleceğe bakmış olurdu. Kod: `analiz/rejim.py` içinde `vix_rejimi`.",
            "**2 İkili İlişki:** Rolling korelasyon grafiğinde VIX > 25 olan günler kırmızı gölgeyle işaretlenir.",
            "**7 Piyasa Nabzı:** VIX'in son seviyesi ve geçmişe göre yüzdeliği gösterilir.",
            "VIX burada seviye olarak kullanılır; getirisi alınmaz (rejim için seviye anlamlıdır).",
        ],
        "iliski": [
            "Gergin (yüksek VIX) rejimde varlıklar arası korelasyonlar çoğu zaman yükselir. Bunun bir kısmı volatilitenin "
            "kendisinden gelen ölçüm etkisidir, tek başına 'bulaşma' kanıtı değildir (4. sayfadaki uyarı).",
            "VIX, S&P 500'ün volatilitesidir; **Beta** ve **Korelasyon** kavramlarıyla birlikte, hisse düşerken varlıkların "
            "nasıl hareket ettiğini rejime göre ayırmak için kullanılır.",
        ],
        "canli": "vix",
    },
    {
        "id": "beta",
        "baslik": "Beta",
        "kisa": "Bir varlık, referans bir varlık %1 oynadığında ortalama kaç % oynar.",
        "ne": (
            "Beta, bir varlığın (y) bir referans varlığın (x) hareketine ne kadar **duyarlı** olduğunu söyleyen katsayıdır. "
            "Referans %1 oynadığında y ortalama beta kadar % oynar.\n\n"
            "Gündelik benzetme: bir minibüs (referans) hızlanınca arkasına bağlı römorkun (y) ne kadar savrulduğunu düşünün. "
            "Beta 1 ise römork aynı hızla gider, 2 ise iki kat savrulur, 0,5 ise yarısı kadar. "
            "Beta negatifse römork ters yöne gider."
        ),
        "neden": (
            "Klasik finansta referans genelde piyasa endeksidir (ör. S&P 500) ve beta, bir hissenin piyasa riskine ne kadar "
            "maruz olduğunu verir. Portföy riskini ayarlamada kullanılır: beta > 1 olan varlık piyasadan daha saldırgan, "
            "beta < 1 olan daha savunmacıdır. Hedge oranı (bir pozisyonu korumak için ne kadar karşı pozisyon açılacağı) "
            "de betadan hesaplanır.\n\n"
            "Önemli fark: **korelasyon** ilişkinin gücünü (yönünü ve sıkılığını) ölçer, **beta** ise büyüklüğünü ölçer."
        ),
        "okuma": (
            "- **Beta = 1:** referansla aynı büyüklükte hareket.\n"
            "- **Beta > 1:** referanstan daha oynak (ör. 1,5: referans %1 artarsa y ortalama %1,5 artar).\n"
            "- **0 < Beta < 1:** referansı izler ama daha yumuşak.\n"
            "- **Beta ≈ 0:** referanstan bağımsız.\n"
            "- **Beta < 0:** ters yönde (ör. VIX'in hisse senedine göre betası genelde negatiftir).\n\n"
            "Betanın yanında **standart hata (se)** da okunmalıdır: beta ± 1,96 × se kabaca %95 aralığı verir. "
            "Aralık sıfırı içeriyorsa ilişki istatistiksel olarak belirgin değildir."
        ),
        "formuller": [
            r"y_t = \alpha + \beta\, x_t + \varepsilon_t",
            r"\beta = \frac{\mathrm{Cov}(x,y)}{\mathrm{Var}(x)} = \rho \cdot \frac{\sigma_y}{\sigma_x}",
        ],
        "semboller": [
            ("y_t", "t gününde incelenen varlığın getirisi."),
            ("x_t", "t gününde referans varlığın getirisi."),
            ("α", "referanstan bağımsız ortalama getiri (sabit terim)."),
            ("β", "beta; x'teki 1 birimlik değişime y'nin ortalama tepkisi."),
            ("ε_t", "açıklanamayan kısım (hata)."),
            ("ρ", "x ve y arasındaki korelasyon."),
            ("σ_x, σ_y", "x ve y getirilerinin standart sapması (oynaklık)."),
        ],
        "not_": "Betayı korelasyonla bağlayan ikinci satır önemlidir: beta = ρ × σ_y / σ_x.",
        "ornek": (
            "1. Diyelim ρ = 0,6 (orta güçte pozitif ilişki).\n"
            "2. y'nin günlük standart sapması σ_y = %2, referansın σ_x = %1.\n"
            "3. β = 0,6 × 2 / 1 = **1,2**.\n"
            "4. Yorum: referans %1 artarsa y ortalama %1,2 artar.\n"
            "5. Aynı korelasyonla y daha sakin olsaydı (σ_y = %0,5) β = 0,6 × 0,5 / 1 = 0,3 olurdu. "
            "Yani korelasyon aynı kalsa bile beta, y'nin oynaklığına göre değişir."
        ),
        "panoda": [
            "**4 Rejim ve Beta, bölüm (b) Beta tablosu:** referans varlık seçilir (varsayılan SPX); her varlık için "
            "`y = a + beta * x + e` OLS ile tahmin edilir. Pencere kenar çubuğundaki 60g / 250g seçimidir; "
            "grafikte hata çubuğu ±1,96 × se'dir. Kod: `analiz/rejim.py` içinde `beta_tablosu` (sütunlar: beta, se, t, r, n). "
            "En az 30 ortak gözlem yoksa NaN gösterilir.",
            "**2 İkili İlişki:** seçilen iki varlık için beta, son pencere ve seçili aralığın tamamı için ayrıca gösterilir.",
            "Faiz serilerinde birim bp'dir (baz puan); fiyat serilerinde getiriler log-getiridir.",
        ],
        "iliski": [
            "**Korelasyonla ilişki:** β = ρ × σ_y / σ_x. Korelasyon -1 ile +1 arasına sıkışır, beta sınırsızdır. "
            "Korelasyon düşük ama beta büyük olabilir (çok oynak bir varlık) ya da tersi.",
            "Tablodaki `r` sütunu aynı pencerenin Pearson korelasyonudur; beta bu yüzden Pearson mantığına dayanır "
            "(uç değerlere duyarlıdır).",
        ],
        "canli": "beta",
    },
    {
        "id": "korelasyon",
        "baslik": "Korelasyon",
        "kisa": "İki varlığın birlikte hareket etme eğiliminin -1 ile +1 arasında özeti.",
        "ne": (
            "Korelasyon, iki serinin **birlikte ne kadar hareket ettiğini** gösteren bir sayıdır. Değeri her zaman -1 ile +1 "
            "arasındadır. +1: biri artınca diğeri de hep artar; -1: biri artınca diğeri hep düşer; 0: belirgin bir birliktelik yok.\n\n"
            "Gündelik benzetme: dondurma satışları ile havanın sıcaklığı birlikte artar (pozitif korelasyon). "
            "Hava soğudukça kalın mont satışları artar (sıcaklıkla negatif korelasyon). Ama dondurmanın havayı ısıttığını söyleyemeyiz: "
            "korelasyon nedensellik göstermez."
        ),
        "neden": (
            "Portföy çeşitlendirmesinin temelidir: birbirine düşük korelasyonlu varlıklar birlikte tutulursa toplam risk azalır. "
            "Ayrıca hangi varlıkların aynı faktörle (ör. küresel risk iştahı) hareket ettiğini bulmak, bir hedge adayı seçmek "
            "ya da piyasa yapısının zamanla değişip değişmediğini izlemek için kullanılır.\n\n"
            "Önemli: korelasyon **getiriler** (günlük % değişim) üzerinden hesaplanır, fiyat seviyeleri üzerinden değil. "
            "Seviyeleri zamanla yükselen iki seri, aralarında gerçek bir ilişki olmasa da yüksek korelasyon gösterir (sahte korelasyon)."
        ),
        "okuma": (
            "Kabaca (mutlak değer için): 0 - 0,2 çok zayıf, 0,2 - 0,4 zayıf, 0,4 - 0,6 orta, 0,6 - 0,8 güçlü, 0,8 - 1 çok güçlü.\n\n"
            "Örnek yorumlar: 0,75 = birlikte hareket etme eğilimi güçlü. -0,4 = orta güçte ters ilişki. 0,05 = pratikte ilişki yok.\n\n"
            "Korelasyon sabit değildir; zamanla değişir. Bu yüzden pano 60 ve 250 günlük pencereler kullanır. "
            "Kısa pencere hızlı ama gürültülü, uzun pencere yavaş ve stabildir. Örneklem küçükse (n küçük) değer güvenilmezdir "
            "(bkz. Fisher z)."
        ),
        "formuller": [
            r"\rho_{xy} = \frac{\mathrm{Cov}(x,y)}{\sigma_x\,\sigma_y}",
            r"\mathrm{Cov}(x,y) = \frac{1}{n-1}\sum_{t=1}^{n}(x_t-\bar{x})(y_t-\bar{y})",
        ],
        "semboller": [
            ("ρ_xy", "x ve y arasındaki korelasyon (örneklemden tahmin edilince çoğu zaman r yazılır)."),
            ("Cov(x,y)", "kovaryans: ikisinin ortalamalarından sapmalarının ortak yönü."),
            ("σ_x, σ_y", "standart sapmalar; kovaryansı ölçekten arındırır, böylece sonuç -1 ile 1 arasına girer."),
            ("x̄, ȳ", "ortalamalar."),
            ("n", "gözlem sayısı."),
        ],
        "ornek": (
            "x = [1, 2, 3, 4], y = [2, 1, 4, 3] olsun.\n\n"
            "1. Ortalamalar: x̄ = 2,5; ȳ = 2,5.\n"
            "2. Sapmalar: x için [-1,5; -0,5; 0,5; 1,5], y için [-0,5; -1,5; 1,5; 0,5].\n"
            "3. Çarpımlar: [0,75; 0,75; 0,75; 0,75], toplam 3. Kovaryans = 3 / (4-1) = 1.\n"
            "4. σ_x = σ_y = √(5/3) ≈ 1,29. Çarpımları 5/3 ≈ 1,667.\n"
            "5. ρ = 1 / 1,667 = **0,6**. İki seri orta-güçlü pozitif ilişkili."
        ),
        "panoda": [
            "**1 Korelasyon Haritası:** tüm varlıklar arası korelasyon matrisi; ayrıca 'şimdi' ile geçmiş bir nokta "
            "arasındaki fark matrisi. Farkın anlamlı olup olmadığı iki örneklem Fisher-z testiyle (p < 0,05) süzülür. "
            "Kod: `analiz/korelasyon.py` içinde `iki_nokta_karsilastirma`.",
            "**2 İkili İlişki:** seçilen iki varlık için 60g ve 250g rolling korelasyon ve Fisher z bandı.",
            "**3 Ağ ve Kümeler:** Spearman korelasyonlarından çıkarılan MST (minimum spanning tree) ve dendrogram.",
            "**4 Rejim ve Beta:** VIX rejimine göre (sakin / normal / gergin) ayrı korelasyon matrisleri.",
            "**6 Lead-Lag:** bir varlığın gecikmeli değeri ile diğerinin bugünkü değeri arasındaki çapraz korelasyon.",
            "Ayarlar (kenar çubuğu): Pencere 60g / 250g (varsayılan 250g), Korelasyon yöntemi Spearman / Pearson "
            "(varsayılan Spearman), Baz USD / Yerel. Her hücrede en az 40 (60g) veya 150 (250g) ortak gözlem aranır.",
        ],
        "iliski": [
            "Korelasyonun iki ana türü vardır: **Pearson** (değerlerin kendisi, doğrusal ilişki) ve **Spearman** (sıralar). "
            "Panonun varsayılanı Spearman'dır.",
            "**Beta** = ρ × σ_y / σ_x; korelasyon yön ve gücü, beta büyüklüğü verir.",
            "Korelasyonun belirsizliği **Fisher z** ile ölçülür.",
        ],
        "canli": "korelasyon_ozet",
    },
    {
        "id": "pearson",
        "baslik": "Pearson",
        "kisa": "Doğrusal ilişkiyi ölçen klasik korelasyon; uç değerlere duyarlıdır.",
        "ne": (
            "Pearson korelasyonu, iki serinin **doğrusal** ilişkisini ölçer. Değerlerin kendisini (ham getirileri) kullanır. "
            "Korelasyon bölümündeki formül tam olarak Pearson'dır.\n\n"
            "Gündelik benzetme: iki değişkeni nokta bulutu olarak çizin. Pearson, bu bulutun ne kadar bir doğru çizgiye "
            "yakın durduğunu ölçer. Nokta bulutu bir çizgiye yapışıksa Pearson yüksektir; çizgi etrafında dağınıksa düşüktür."
        ),
        "neden": (
            "En yaygın, en eski ve en bilinen korelasyondur; beta ve regresyon ile doğrudan bağlıdır. "
            "Veriler yaklaşık normal dağılmışsa ve uç değer yoksa en verimli (en az belirsiz) tahmindir.\n\n"
            "Zayıf noktası: **uç değerlere (outlier) duyarlıdır**. Finansal getirilerde kriz günleri gibi aşırı büyük "
            "hareketler vardır; tek bir gün korelasyonu belirgin biçimde değiştirebilir. Ayrıca yalnızca doğrusal ilişkiyi görür."
        ),
        "okuma": (
            "Değer aralığı -1 ile +1'dir (bkz. Korelasyon). Pearson'ın özel yorumu: değer, noktaların bir **doğruya** "
            "ne kadar yakın olduğunu söyler. r² ise bir serinin değişiminin diğeri tarafından doğrusal olarak açıklanan oranıdır; "
            "r = 0,6 ise r² = 0,36, yani değişimin yaklaşık %36'sı açıklanır.\n\n"
            "Pearson ile Spearman arasında büyük fark varsa, genelde birkaç uç değer ya da doğrusal olmayan bir ilişki vardır."
        ),
        "formuller": [
            r"r = \frac{\sum_{t}(x_t-\bar{x})(y_t-\bar{y})}{\sqrt{\sum_t (x_t-\bar{x})^2}\;\sqrt{\sum_t (y_t-\bar{y})^2}}",
        ],
        "semboller": [
            ("r", "Pearson korelasyon katsayısı."),
            ("x_t, y_t", "t. gözlemde iki serinin ham değerleri (burada getiriler)."),
            ("x̄, ȳ", "ortalamalar."),
            ("Σ", "tüm gözlemler üzerinden toplam."),
        ],
        "ornek": (
            "x = [1, 2, 3, 4, 5], y = [2, 1, 4, 3, 100] olsun (son değer bir uç değer).\n\n"
            "1. Ortalamalar: x̄ = 3; ȳ = 22.\n"
            "2. Sapmalar: x için [-2, -1, 0, 1, 2], y için [-20, -21, -18, -19, 78].\n"
            "3. Çarpımlar toplamı: 40 + 21 + 0 - 19 + 156 = 198.\n"
            "4. Kareler toplamı: x için 10; y için 400 + 441 + 324 + 361 + 6084 = 7610.\n"
            "5. r = 198 / √(10 × 7610) = 198 / 275,9 ≈ **0,72**.\n\n"
            "Pearson sayıların büyüklüğünden etkilendi: 100 değeri sonucu aşağı çekti. "
            "Aynı veride Spearman 0,80 çıkar (Spearman sekmesine bakın)."
        ),
        "panoda": [
            "Kenar çubuğunda **Korelasyon yöntemi** seçeneklerinden biridir (varsayılan Spearman, Pearson seçenek).",
            "**2 İkili İlişki** ve **1 Korelasyon Haritası** ekranları seçime göre hesaplanır. Rolling Pearson: "
            "`analiz/korelasyon.py` içinde `ikili_rolling` (yontem='pearson').",
            "Beta tablosundaki `r` sütunu her zaman Pearson'dır (OLS ile tutarlı olması için).",
        ],
        "iliski": [
            "**Pearson ve Spearman farkı:** Pearson değerin kendisine, Spearman sırasına bakar. Ayrıntı Spearman sekmesinde.",
            "Beta = Pearson ρ × σ_y / σ_x; yani beta, Pearson'ın büyüklüğe çevrilmiş halidir.",
        ],
        "canli": "pearson_spearman",
    },
    {
        "id": "spearman",
        "baslik": "Spearman",
        "kisa": "Değerler yerine sıralara bakan korelasyon; uç değerlere dayanıklıdır. Panonun varsayılanı.",
        "ne": (
            "Spearman (rank) korelasyonu, değerleri sıralarıyla değiştirip bu sıralar üzerinden Pearson hesaplar. "
            "En küçük gözlem 1, bir sonraki 2... diye sıralanır. Böylece 'ne kadar büyük' önemsizleşir, "
            "sadece 'hangisi daha büyük' önem kazanır.\n\n"
            "Gündelik benzetme: bir yarışta iki hakem aynı sporcuları sıraya diziyor. Sporcuların tam süreleri değil, "
            "kimin kaçıncı geldiği karşılaştırılıyor. Birinin süresi tuhaf derecede kötü bile olsa sadece 'son sıra' olur, "
            "sonucu bozmaz."
        ),
        "neden": (
            "Finansal getirilerde kalın kuyruk (fat tail) vardır: nadir ama çok büyük hareketler. Pearson bunlardan çok etkilenir, "
            "Spearman çok daha az. Ayrıca yalnız doğrusal değil, **monoton** (hep aynı yöne giden ama eğri olabilen) "
            "ilişkileri de yakalar.\n\n"
            "Bedeli: normal veride Pearson biraz daha verimlidir ve Spearman'ın betayla doğrudan matematiksel bağı yoktur."
        ),
        "okuma": (
            "Değer aralığı Pearson ile aynıdır: -1 ile +1. +1: sıralar birebir aynı (monoton artan ilişki), -1: tam ters sıra, 0: sıralar ilişkisiz.\n\n"
            "Pearson ve Spearman yakınsa ilişki doğrusala yakındır ve uç değerler sonucu bozmuyordur. Spearman belirgin biçimde "
            "Pearson'dan büyükse genelde uç değerler Pearson'ı aşağı çekiyordur ya da ilişki doğrusal olmayan ama monotondur. "
            "Pearson belirgin biçimde Spearman'dan büyükse birkaç aşırı gün Pearson'ı şişiriyor olabilir."
        ),
        "formuller": [
            r"\rho_s = \mathrm{Pearson}\big(\mathrm{rank}(x),\ \mathrm{rank}(y)\big)",
            r"\rho_s = 1 - \frac{6\sum_t d_t^2}{n\,(n^2-1)}",
        ],
        "semboller": [
            ("ρ_s", "Spearman korelasyon katsayısı."),
            ("rank(x)", "x serisinin sıra numaraları (1 = en küçük)."),
            ("d_t", "t. gözlemde iki serinin sıraları arasındaki fark."),
            ("n", "gözlem sayısı."),
        ],
        "not_": "İkinci satırdaki kısayol formül yalnızca eşit değerler (tie) yokken tam doğrudur. Birinci satır her durumda geçerlidir.",
        "ornek": (
            "Pearson'daki aynı veri: x = [1, 2, 3, 4, 5], y = [2, 1, 4, 3, 100].\n\n"
            "1. x'in sıraları: [1, 2, 3, 4, 5].\n"
            "2. y'nin sıraları: 1 en küçük, sonra 2, 3, 4 ve 100 en büyük; yani y = [2, 1, 4, 3, 100] için sıralar [2, 1, 4, 3, 5].\n"
            "3. Sıra farkları d = [1-2, 2-1, 3-4, 4-3, 5-5] = [-1, 1, -1, 1, 0]. Kareleri toplamı = 4.\n"
            "4. ρ_s = 1 - 6 × 4 / (5 × 24) = 1 - 24/120 = **0,80**.\n\n"
            "Pearson 0,72 çıkmıştı. 100 sayısı yalnızca 'en büyük' olduğu için etkisi sınırlı kaldı; "
            "ne kadar büyük olduğu hesaba girmedi."
        ),
        "panoda": [
            "**Panonun varsayılan yöntemi Spearman'dır** (kenar çubuğu, Korelasyon yöntemi). Pearson seçenek olarak durur.",
            "**3 Ağ ve Kümeler:** MST ve dendrogram Spearman korelasyonlarından kurulur.",
            "Kod: `analiz/korelasyon.py` içinde `korelasyon_matrisi` (`yontem='spearman'`) ve rolling için `_rolling_spearman` "
            "(her pencerede sıralar yeniden hesaplanır).",
            "Tasarım gerekçesi (`TASARIM.md`): uç değerlere dayanıklılık ve MST için uygunluk.",
        ],
        "iliski": [
            "**Neden varsayılan Spearman?** Günlük finansal getirilerde nadir ama çok büyük günler (kriz, şok) vardır. "
            "Pearson'da tek bir böyle gün korelasyonu epey oynatabilir; panonun ana işi 'varlıklar genelde birlikte mi oynuyor' "
            "sorusunu yanıtlamak olduğu için sıralara bakmak daha sağlam bir ana ölçüdür. Pearson yine de seçenek olarak durur "
            "ve ikisi arasındaki fark başlı başına bilgi verir.",
            "Spearman için p-değeri ve Fisher bandı panoda Pearson formülleriyle yaklaşık hesaplanır; Spearman için tam doğru değil, yaklaşıktır.",
        ],
        "canli": "pearson_spearman",
    },
    {
        "id": "normalize",
        "baslik": "Normalize",
        "kisa": "Farklı ölçekteki serileri ortak bir başlangıca çekip karşılaştırılabilir yapmak.",
        "ne": (
            "Normalize etmek, ölçekleri farklı serileri aynı skalaya getirmektir. Pano özelinde: iki varlığın fiyatı çok farklı "
            "büyüklükte olabilir (BTC on binlerce dolar, bir endeks bin birimler). Doğrudan çizersek biri düz çizgi görünür. "
            "İki seriyi de başlangıçta 100'e eşitleyince sonraki değişim doğrudan yüzde olarak okunur.\n\n"
            "Gündelik benzetme: iki arkadaşın biri 1.000 TL, diğeri 50.000 TL ile yatırıma başlamış olsun. "
            "Kimin daha çok kazandığını görmek için ikisini de 100 TL ile başlamış gibi çizersiniz."
        ),
        "neden": (
            "Seviye grafiklerinde 'hangisi daha iyi performans gösterdi' sorusunu yanıtlamanın standart yoludur. "
            "Başka normalizasyon türleri de vardır: z-skoru (ortalamayı çıkar, standart sapmaya böl) veya min-max (0-1 arasına sıkıştır). "
            "Hepsinin ortak fikri ölçek farkını ortadan kaldırmaktır.\n\n"
            "Dikkat: normalize görüntü içindir; hangi başlangıç gününü seçtiğiniz görüntüyü etkiler. Korelasyon zaten ölçekten bağımsızdır "
            "(formülde σ'lara bölünür) ve getiriler üzerinden hesaplandığı için bu normalizasyona ihtiyaç duymaz."
        ),
        "okuma": (
            "- Seri 100'ün üzerindeyse başlangıçtan beri kazandırmıştır; 140 = %40 artış, 70 = %30 düşüş.\n"
            "- İki seri arasındaki mesafe, o ana kadar birinin diğerine göre ne kadar öne geçtiğini gösterir.\n"
            "- Çizgilerin şekli (inişler, çıkışlar) önemlidir; sürekli birlikte hareket ediyorlarsa korelasyon yüksektir."
        ),
        "formuller": [
            r"N_t = 100 \times \frac{P_t}{P_0}",
            r"z_t = \frac{P_t - \mu}{\sigma} \quad \text{(z-skoru ile normalizasyon, bilgi için)}",
        ],
        "semboller": [
            ("N_t", "t gününde normalize değer."),
            ("P_t", "t gününde fiyat (seviye)."),
            ("P_0", "ilk ortak günün fiyatı; başlangıç noktası."),
            ("μ, σ", "serinin ortalaması ve standart sapması (z-skoru için)."),
        ],
        "not_": "Panoda yalnızca ilk formül (ilk ortak gün = 100) kullanılır; z-skoru karşılaştırma için verilmiştir.",
        "ornek": (
            "A varlığı 50'den 60'a, B varlığı 200'den 210'a çıktı.\n\n"
            "1. Ham değişim: A +10, B +10. Aynı görünür, yanıltıcıdır.\n"
            "2. Normalize: A = 100 × 60 / 50 = **120**; B = 100 × 210 / 200 = **105**.\n"
            "3. Yorum: A %20, B %5 arttı. A, B'den dört kat daha fazla kazandırmış."
        ),
        "panoda": [
            "**2 İkili İlişki**, alt grafik: 'Normalize seviye (ilk ortak gün = 100)'. İki varlığın seçili aralıktaki "
            "ilk ortak gözlemi 100 alınır (`100 * seviye / seviye.iloc[0]`); seçilen Baz (USD / Yerel) geçerlidir.",
            "Korelasyon hesabı normalize edilmiş seviyeler üzerinden değil, getiriler üzerinden yapılır.",
        ],
        "iliski": [
            "Normalize, **Korelasyon**'dan farklı bir iştir: seviye grafiğini okunur yapar, korelasyon ise getirilerin birlikteliğini ölçer.",
            "Korelasyon ve beta formüllerinde σ'ya bölme de bir normalizasyondur: korelasyon, kovaryansın ölçekten arındırılmış halidir.",
        ],
        "canli": "",
    },
    {
        "id": "fisher",
        "baslik": "Fisher z",
        "kisa": "Korelasyonun belirsizliğini (güven aralığı ve fark testi) hesaplamaya yarayan dönüşüm.",
        "ne": (
            "Bir korelasyonu örneklemden hesaplarız; gerçek (bilinmeyen) korelasyon ondan biraz farklı olabilir. "
            "Bu belirsizliği ölçmek için güven aralığı gerekir. Sorun şu: r -1 ile 1 arasında sınırlıdır ve 1'e yakınken "
            "dağılımı çarpıktır, yani doğrudan 'r ± bir şey' demek olmaz.\n\n"
            "Fisher z dönüşümü r'yi sınırsız bir ölçeğe taşır; orada dağılım yaklaşık normaldir ve standart hatası "
            "yalnızca örneklem büyüklüğüne bağlıdır. Aralığı orada hesaplayıp tekrar r ölçeğine çeviririz.\n\n"
            "Gündelik benzetme: harita üzerinde kutba yakın yerlerde mesafeler yanıltıcıdır. Harita projeksiyonu (z) mesafeleri "
            "düzeltir; ölçümü yaptıktan sonra gerçek harita (r) üzerine geri dönersiniz."
        ),
        "neden": (
            "İki işe yarar:\n\n"
            "1. **Güven aralığı:** 'BTC - NASDAQ korelasyonu 0,45' demek yetmez; 0,45 ± ne kadar? n küçükse aralık çok geniştir.\n"
            "2. **Fark testi:** 'Korelasyon şimdi 0,60, bir yıl önce 0,40; gerçekten değişti mi, yoksa gürültü mü?' "
            "sorusu iki örneklemli Fisher-z testiyle cevaplanır.\n\n"
            "Önemli sınır: formüller gözlemlerin bağımsız olduğunu varsayar. Rolling pencerelerde yan yana noktalar çakışan günler içerir, "
            "bu yüzden gerçek belirsizlik gösterilenden daha geniştir. Pano bunu ekranlarda ayrıca uyarır."
        ),
        "okuma": (
            "- **Dar aralık** (ör. 0,40 - 0,50): ölçüm güvenilir (n büyük).\n"
            "- **Geniş aralık** (ör. 0,05 - 0,70): neredeyse hiçbir şey söylemiyor (n küçük).\n"
            "- Aralık **0'ı içeriyorsa** ilişkinin yönü istatistiksel olarak kesin değildir.\n"
            "- İki korelasyonun farkı için p-değeri < 0,05 ise fark gürültüden ayırt edilebilir (çoklu test düzeltmesi ayrıca gerekir)."
        ),
        "formuller": [
            r"z = \operatorname{arctanh}(r) = \tfrac{1}{2}\ln\frac{1+r}{1-r}",
            r"\mathrm{SE}_z = \frac{1}{\sqrt{n-3}}",
            r"\text{95 yüzde aralığı: } \ \tanh\!\big(z \pm 1{,}96\cdot \mathrm{SE}_z\big)",
            r"\text{iki r farkı: } \ Z = \frac{z_1 - z_2}{\sqrt{\frac{1}{n_1-3}+\frac{1}{n_2-3}}}",
        ],
        "semboller": [
            ("r", "örneklem korelasyonu."),
            ("z", "Fisher dönüşümü sonrası değer (arctanh)."),
            ("SE_z", "z ölçeğindeki standart hata; sadece n'e bağlıdır."),
            ("n", "ortak gözlem sayısı."),
            ("1,96", "normal dağılımda %95 için kritik değer."),
            ("tanh", "z'den tekrar r ölçeğine döndürür (arctanh'ın tersi)."),
            ("Z", "iki korelasyon farkının test istatistiği; p-değeri normal dağılımdan alınır."),
        ],
        "ornek": (
            "r = 0,5 ve n = 103 olsun.\n\n"
            "1. z = arctanh(0,5) = 0,5493.\n"
            "2. SE = 1 / √(103 - 3) = 1 / 10 = 0,1.\n"
            "3. z ölçeğinde aralık: 0,5493 ± 1,96 × 0,1 → [0,3533 ; 0,7453].\n"
            "4. Geri r ölçeğine: tanh(0,3533) ≈ 0,34 ve tanh(0,7453) ≈ 0,63.\n"
            "5. Sonuç: r = 0,50, %95 aralık **[0,34 ; 0,63]**.\n\n"
            "n = 28 olsaydı SE = 1/5 = 0,2 olur ve aralık yaklaşık [0,16 ; 0,74]'e genişlerdi."
        ),
        "panoda": [
            "**2 İkili İlişki:** rolling korelasyonun etrafındaki açık renkli bant yaklaşık %95 Fisher z aralığıdır. "
            "Kod: `analiz/istatistik.py` içinde `fisher_bant(r, n)`.",
            "**6 Lead-Lag:** her gecikme için çapraz korelasyonun hata çubuğu yaklaşık %95 Fisher aralığıdır (`analiz/leadlag.py`).",
            "**1 Korelasyon Haritası:** 'şimdi' ile geçmiş korelasyon farkının p-değeri iki örneklemli Fisher-z testiyle "
            "hesaplanır (`analiz/korelasyon.py`, `iki_nokta_karsilastirma`); p < 0,05 olmayan farklar süzülebilir. "
            "Tek bir korelasyonun p-değeri (`korelasyon_p`) ise t = r√((n-2)/(1-r²)) yaklaşımıdır.",
            "Her yerde örtüşen pencereler bağımsız gözlem varsayımını bozar; bantlar iyimserdir.",
        ],
        "iliski": [
            "Dönüşüm aslında Pearson için türetilmiştir; Spearman için panoda yaklaşık olarak aynı formül kullanılır.",
            "n azaldıkça belirsizlik artar. Bu yüzden pano 60g için en az 40, 250g için en az 150 ortak gözlem arar.",
        ],
        "canli": "fisher",
    },
]
