# -*- coding: utf-8 -*-
"""Makro Pano varlik bilgi kartlari (icerik). Yatirim tavsiyesi degildir.
Anahtar: seri kodu. Alanlar: ad, kisa, nedir, islem, nerede, turkiye, etkiler, panoda, notlar.
Saatler ve urun/ticker isimleri zamanla degisebilir; hepsi "yaklasik" kabul edilmelidir.
"""

ALANLAR = ["ad", "kisa", "nedir", "islem", "nerede", "turkiye", "etkiler", "panoda", "notlar"]

_DANIS = "Ürün adları ve koşullar kuruma göre değişir; ayrıntı için kendi kurumunuza danışın."
_KRIPTO_NEREDE = ("Kripto borsalarında (ör. Binance) 7/24, tatil yok. Tek bir resmi kapanış yoktur; "
                  "panoda gün sonu olarak 21:00 UTC (yaklaşık Türkiye saatiyle 00:00) fiyatı kullanılır.")
_KRIPTO_TR = ("Türk borsaları (ör. Binance TR, BtcTurk, Paribu; hangi coinin listelendiği borsaya göre değişir) "
              "ve global borsalar üzerinden alınıp satılabilir. Vergi ve mevzuat durumu değişebilir; "
              "kurumunuza ve güncel mevzuata bakın. ")
_KRIPTO_NOT = ("Gün sonu değeri 21:00 UTC (yaklaşık Türkiye saatiyle 00:00) fiyatıdır; borsalar 7/24 işlem gördüğü için "
               "başka bir saatte bakarsanız fiyat farklı olur. Fiyat USDT paritesindendir (USD'ye çok yakın bir stablecoin), "
               "birebir USD değildir.")
_FX_NEREDE = ("Merkezi borsası olmayan OTC piyasa; yaklaşık 24 saat, haftada 5 gün (Pazar akşamı - Cuma akşamı). "
              "Hafta sonu kapalı.")
_FX_NOT = ("Kaynak Yahoo FX; gün kapanışı yaklaşık Londra gece yarısıdır. Kaynakta 2010-08 sonrası tarih etiketi "
           "bir gün ileri olduğu için toplayıcı etiketi bir önceki iş gününe kaydırarak düzeltir (ABD kapanışıyla hizalamak için).")
_FX_TR = ("Bankalarda döviz hesabı, aracı kurumlarda forex/döviz işlemleri ve Borsa İstanbul VİOP'ta döviz vadeli kontratları "
          "(hangi paritelerin bulunduğu zamanla değişir) bu kurlara maruz kalmanın yollarıdır. " + _DANIS)
_VADELI_NOT = ("Seri sürekli (front-month) vadeli kontrattır; kontrat değişirken (roll) fiyatta yapay sıçrama olabilir, "
               "bu gerçek bir getiri değildir. Kaynak: Yahoo.")
_ENDEKS_ISLEM = ("Endeksin kendisi doğrudan alınıp satılamaz; yalnız ona bağlı ürünlerle (ETF/yatırım fonu, vadeli, opsiyon) "
                 "maruz kalınır. ")
_TAHVIL_ISLEM = ("Getiri oranının kendisi alınıp satılamaz; tahvilin fiyatından türetilir. Tahvil fiyatı ile getiri ters yönde "
                 "hareket eder. Tahvil, tahvil ETF'i veya faiz vadelisi üzerinden maruz kalınır. ")
_POLITIKA_ISLEM = ("İşlem görmez, sadece gösterge. Merkez bankası belirler; ilişkili ürünler: kısa vadeli devlet tahvili/bono, "
                   "para piyasası fonları, mevduat ve ülkenin para birimi. ")
_POLITIKA_NOT = ("Kaynak BIS aylık dönem sonu verisidir (ay başı tarihli, basamaklı). Karar günü değil ay bazında görünür; "
                 "günlük serilerle karşılaştırırken gecikme olabilir.")
_ALT_TR = _KRIPTO_TR + "Bu coin her borsada olmayabilir. "
_YD_TR = ("Yurt dışı hisse/ETF işlemi imkânı veren Türk aracı kurumlar üzerinden, TEFAS'ta yabancı endeks fonlarıyla (varsa) ya da "
          "yurt dışı aracı kurumlar üzerinden. " + _DANIS)
_BORSA_NOT = ("Kaynak Yahoo; gün sonu endeks seviyesi yerel para birimindedir. Yerel kapanış saati ile kripto 21:00 UTC "
              "referansı farklı olduğundan zamanlama kayması olabilir.")

BILGI = {}


def _e(kod, ad, kisa, nedir, islem, nerede, turkiye, etkiler, panoda, notlar):
    BILGI[kod] = dict(ad=ad, kisa=kisa, nedir=nedir, islem=islem, nerede=nerede,
                      turkiye=turkiye, etkiler=etkiler, panoda=panoda, notlar=notlar)


# ---------------------------------------------------------------- KRIPTO
_e("BTC", "Bitcoin (BTC)", "En büyük ve en eski kripto para.",
   "Bitcoin, merkezi bir kurumu olmayan, 2009'da başlayan kripto para ağıdır. Toplam arzı 21 milyon ile sınırlıdır; "
   "bu yüzden bazıları onu \"dijital altın\" olarak görür. Fiyat 1 BTC'nin USD (USDT) karşılığıdır.",
   "Doğrudan (spot) alınıp satılır. Ayrıca vadeli/opsiyon (ör. CME Bitcoin vadelisi) ve spot Bitcoin ETF'leri (ABD'de ör. IBIT) vardır.",
   _KRIPTO_NEREDE,
   _KRIPTO_TR + "Yurt dışındaki ETF'lere yurt dışı hisse imkânı veren aracı kurumlar üzerinden erişilebilir. " + _DANIS,
   ["Risk iştahının en görünür kripto göstergesidir; hisse senetleriyle zaman zaman birlikte hareket eder.",
    "Faiz beklentileri ve dolar likiditesinden etkilenir.", "Altcoinlerin çoğu BTC'yi takip eder; panoda kripto referansıdır."],
   "Binance, BTCUSDT, günlük (21:00 UTC).", _KRIPTO_NOT)
_e("ETH", "Ethereum (ETH)", "Akıllı kontrat ağı Ethereum'un yerel parası; ikinci büyük kripto.",
   "Ethereum, üzerinde uygulamaların (DeFi, NFT, stablecoin) çalıştığı bir blokzincirdir. ETH ağ işlem ücretinin ödendiği "
   "paradır. Fiyat 1 ETH'nin USD (USDT) karşılığıdır.",
   "Doğrudan (spot) alınıp satılır. Vadeli/opsiyon ve bazı ülkelerde spot ETH ETF'leri vardır.",
   _KRIPTO_NEREDE, _KRIPTO_TR + _DANIS,
   ["Kripto ekosisteminin (DeFi, stablecoin) sağlığını yansıtır.", "BTC ile yüksek oranda birlikte hareket eder, genelde daha oynaktır.",
    "Panoda büyük kripto ikilisinin ikinci ayağıdır."],
   "Binance, ETHUSDT, günlük (21:00 UTC).", _KRIPTO_NOT)
_e("SOL", "Solana (SOL)", "Hızlı ve ucuz işlem hedefleyen akıllı kontrat ağının parası.",
   "Solana, Ethereum'a rakip olarak tasarlanmış bir blokzincirdir; yüksek işlem hızı ve düşük ücret hedefler. SOL ağın yerel parasıdır. "
   "Fiyat 1 SOL'ün USD (USDT) karşılığıdır.",
   "Doğrudan (spot) alınıp satılır. Türev ürünler büyük kripto borsalarında bulunur; ETF durumu ülkeye göre değişir.",
   _KRIPTO_NEREDE, _KRIPTO_TR + "Listeleme borsaya göre değişir. " + _DANIS,
   ["Daha yüksek riskli altcoin tarafının temsilcisidir.", "Risk iştahı artınca BTC'den hızlı yükselip düşme eğilimindedir.",
    "Panoda BTC/ETH dışındaki tekil büyük coin örneğidir."],
   "Binance, SOLUSDT, günlük (21:00 UTC).", _KRIPTO_NOT)
_e("ALTSEPET", "Altcoin Sepeti (10 coin)", "Pano için kurulmuş, 10 büyük altcoinden oluşan eşit ağırlıklı endeks.",
   "Bu bir piyasa endeksi değil, bu panoda hesaplanan kendi endeksimizdir. Bileşenler: XRP, BNB, DOGE, ADA, TRX, AVAX, LINK, UNI, NEAR, SUI. "
   "Her coine eşit ağırlık verilir. Hesap: her gün 10 coinin günlük getirisinin düz ortalaması alınır ve bu ortalama getiriler "
   "zincirlenerek (bileşik) endeks oluşturulur; başlangıç değeri 100'dür. Yani endeks, her gün yeniden eşit ağırlığa getirilen bir sepetin değeri gibi davranır. "
   "Bir coinin verisi henüz yoksa o gün sepete dahil edilmez; sepet, getirisi olan en az 3 coinin bulunduğu günden başlar.\n\n"
   "Coin listesi 2026-10-16'da Binance 24 saatlik USDT hacim sıralamasındaki ilk 40 içinden; BTC, ETH, SOL, stablecoin ve "
   "tokenleştirilmiş hisse/altın hariç, yerleşik büyük coinler olarak seçilmiştir.",
   "Doğrudan alınamaz, çünkü sepet bir hesaplamadır. Benzer bir dağılım için 10 coinin tek tek alınması gerekir; "
   "bazı kripto sepet/endeks ürünleri farklı bileşen ve ağırlıkla bulunabilir ama bu sepetle aynı değildir.",
   "Bileşenler Binance'ta 7/24 işlem görür. Endeksin kendisi işlem görmez.",
   "Bileşen coinler Türk ve global kripto borsalarında alınabilir (her coin her borsada olmayabilir). " + _DANIS,
   ["BTC/ETH dışındaki altcoin tarafının genel risk iştahını ölçer.", "BTC'ye göre güçlenmesi/zayıflaması spekülatif iştahın göstergesi olabilir.",
    "Tek coin riskini azaltmak için kurulmuştur."],
   "Türetilmiş (Binance bileşenlerinden), ALT_* kodları, günlük, taban 100. Bileşenler: ALT_XRP, ALT_BNB, ALT_DOGE, ALT_ADA, ALT_TRX, ALT_AVAX, ALT_LINK, ALT_UNI, ALT_NEAR, ALT_SUI.",
   "Hayatta kalma yanlılığı vardır: bugünün büyük coinleri seçildiği için geçmişte kaybolan coinler dahil değildir, bu da geçmiş performansı olduğundan iyi gösterebilir. "
   "Günlük yeniden dengeleme varsayılır, gerçek işlem maliyeti hesaba katılmaz. " + _KRIPTO_NOT)

_ALT = [("XRP", "XRP (Ripple ağı)", "Hızlı sınır ötesi ödeme amaçlı ağın parası; Ripple şirketiyle ilişkilidir."),
        ("BNB", "BNB (Binance Coin)", "Binance borsasının ve BNB Chain ağının yerel parası."),
        ("DOGE", "Dogecoin (DOGE)", "Başlangıçta şaka olarak çıkan, meme coin olarak bilinen kripto para."),
        ("ADA", "Cardano (ADA)", "Akademik araştırma yaklaşımıyla geliştirilen akıllı kontrat ağının parası."),
        ("TRX", "TRON (TRX)", "TRON ağının parası; ağ üzerinde çok miktarda USDT transferi yapılır."),
        ("AVAX", "Avalanche (AVAX)", "Hızlı sonuçlanan akıllı kontrat ağı Avalanche'ın parası."),
        ("LINK", "Chainlink (LINK)", "Blokzincirlere dış dünya verisi (fiyat vb.) taşıyan oracle ağının parası."),
        ("UNI", "Uniswap (UNI)", "Merkeziyetsiz borsa Uniswap'ın yönetişim tokenı."),
        ("NEAR", "NEAR Protocol (NEAR)", "Akıllı kontrat ağı NEAR'ın yerel parası."),
        ("SUI", "Sui (SUI)", "Yeni nesil, hızlı akıllı kontrat ağı Sui'nin yerel parası.")]
for _k, _ad, _ks in _ALT:
    _e("ALT_" + _k, _ad, _ks,
       _ks + " Fiyat 1 " + _k + "'nin USD (USDT) karşılığıdır. Panoda tek başına bir gösterge olarak değil, ALTSEPET endeksinin 10 bileşeninden biri olarak (eşit ağırlık, %10) bulunur.",
       "Doğrudan (spot) alınıp satılır; türev ürünler büyük kripto borsalarında bulunabilir. Ülkeye göre ETF/ETP ürünleri olabilir, her coin için yoktur.",
       _KRIPTO_NEREDE, _ALT_TR + _DANIS,
       ["ALTSEPET'in bir parçasıdır; sepetin hareketine katkısı yaklaşık %10'dur.", "Genelde BTC'ye göre daha oynaktır.",
        "Tek coine özgü haberler (ağ sorunu, listeleme, hukuki gelişme) fiyatı sepetten ayrıştırabilir."],
       "Binance, " + _k + "USDT, günlük (21:00 UTC). Sepet bileşeni (v1 ekranında ayrı gösterilmez).",
       "Sepet seçimi hayatta kalma yanlılığı taşır. " + _KRIPTO_NOT)

# ---------------------------------------------------------------- FX
_e("USDTRY", "USD/TRY (Dolar/Türk Lirası)", "1 ABD dolarının Türk Lirası karşılığı.",
   "1 USD için kaç TL ödendiğini gösterir. Yükselmesi TL'nin dolar karşısında değer kaybettiği anlamına gelir. Birim: TL. "
   "Piyasa kurudur; TCMB'nin açıkladığı resmi göstergeden ve banka alış/satış kurlarından küçük farklar olabilir.",
   "Doğrudan alınıp satılır (döviz). Ayrıca vadeli (VİOP döviz vadelileri) ve bankalarda döviz hesabı.",
   _FX_NEREDE + " Yerel bankalarda kur işlemleri Türkiye'de iş saatlerinde yoğundur.", _FX_TR,
   ["TL varlıkların (BIST100, GRAMALTIN) dolar bazında değerini doğrudan etkiler.", "Türkiye'de enflasyon ve faiz beklentileriyle yakından bağlantılıdır.",
    "Panoda TL tabanlı serilerin USD'ye çevrilmesinde kullanılır."],
   "Yahoo, TRY=X, günlük.", _FX_NOT)
_e("EURUSD", "EUR/USD (Euro/Dolar)", "1 euronun ABD doları karşılığı; dünyanın en çok işlem gören paritesi.",
   "1 EUR için kaç USD ödendiğini gösterir. Yükselmesi euronun dolar karşısında güçlendiği anlamına gelir. Birim: USD.",
   "Doğrudan alınıp satılır. Vadeli, opsiyon ve bazı ETF'lerle de erişilir.", _FX_NEREDE, _FX_TR,
   ["Dolar endeksi (DXY) içinde en büyük paya sahip parite.", "ECB ve Fed faiz farklarından etkilenir.", "Küresel dolar gücünün temel göstergesidir."],
   "Yahoo, EURUSD=X, günlük.", _FX_NOT)
_e("DXY", "ABD Dolar Endeksi (DXY)", "Doları bir grup büyük para birimine karşı ölçen endeks.",
   "ICE tarafından yayınlanan endekstir; doların EUR (en büyük pay), JPY, GBP, CAD, SEK ve CHF karşısındaki değerini ölçer. "
   "Birim: endeks puanı. Yükselmesi doların güçlendiği anlamına gelir.",
   "Endeksin kendisi alınıp satılamaz. İlişkili enstrümanlar: ICE DXY vadeli kontratları, dolar endeksi ETF'leri (ör. UUP) ve altta yatan döviz çiftleri.",
   "ICE vadelileri yaklaşık neredeyse 24 saat, haftada 5 gün işlem görür. Panoda ABD seansı kapanışı kullanılır.",
   "Bu endekse özel doğrudan ürün sınırlıdır; dolar gücüne maruz kalmak için döviz hesabı, döviz çiftleri veya yurt dışı ETF'ler vardır. " + _DANIS,
   ["Güçlü dolar genelde emtia, altın ve gelişmekte olan ülke varlıkları üzerinde baskı yaratabilir.", "Küresel likidite koşullarının göstergesidir.",
    "Panoda doların genel yönü için tek bir özet olarak bulunur."],
   "Yahoo, DX-Y.NYB, günlük (ABD seansı).",
   "Ağırlığın büyük kısmı euro olduğu için EUR/USD'nin tersi gibi davranır. TL, BRL, ZAR gibi gelişen ülke paraları içinde yoktur. "
   "Diğer FX serilerinden farklı olarak ABD seansı kapanışı kullanılır.")
for _k, _ad, _ks, _nd, _et, _tk in [
    ("USDJPY", "USD/JPY (Dolar/Japon Yeni)", "1 doların Japon Yeni karşılığı.",
     "1 USD için kaç JPY ödendiğini gösterir. Yükselmesi yenin zayıfladığı anlamına gelir. Japonya'nın uzun süre çok düşük faizi nedeniyle yen, carry trade'lerde fonlama para birimi olarak sık kullanılır.",
     ["BoJ ve Fed faiz farkları ile ABD tahvil getirilerinden etkilenir.", "Yen güçlenince carry trade çözülmeleri risk varlıklarında düşüşe yol açabilir.", "Nikkei ile ters yönde hareket etme eğilimi vardır."], "Yahoo, JPY=X, günlük."),
    ("USDCNY", "USD/CNY (Dolar/Çin Yuanı)", "1 doların Çin Yuanı karşılığı (onshore).",
     "1 USD için kaç CNY ödendiğini gösterir. Çin yuanı sıkı yönetilen bir kurdur; PBoC günlük orta kur belirler ve kur belirli bir bant içinde dalgalanır.",
     ["Çin ekonomisi ve ticaret gerilimlerinin göstergesidir.", "Yuan zayıflaması gelişen piyasa paralarına baskı yapabilir.", "Emtia talebiyle (bakır, petrol) ilişkilidir."], "Yahoo, CNY=X, günlük."),
    ("USDBRL", "USD/BRL (Dolar/Brezilya Reali)", "1 doların Brezilya Reali karşılığı.",
     "1 USD için kaç BRL ödendiğini gösterir. Real, emtia fiyatları ve Brezilya'nın yüksek faiz ortamıyla yakından ilişkili bir gelişen piyasa kurudur.",
     ["Emtia (soya, demir cevheri, petrol) ve risk iştahından etkilenir.", "Brezilya Selic faizi ile ilişkilidir.", "Gelişen piyasa riskinin bir göstergesidir."], "Yahoo, BRL=X, günlük."),
    ("USDINR", "USD/INR (Dolar/Hindistan Rupisi)", "1 doların Hindistan Rupisi karşılığı.",
     "1 USD için kaç INR ödendiğini gösterir. Rupi yönetilen dalgalanan bir kurdur; Hindistan Merkez Bankası (RBI) ani oynaklığa müdahale edebilir.",
     ["Petrol fiyatı Hindistan için ithalat maliyeti olduğundan rupiyi etkiler.", "Yabancı portföy girişleri (Nifty) ile ilişkilidir.", "Gelişen piyasa riskinin göstergesidir."], "Yahoo, INR=X, günlük."),
    ("USDZAR", "USD/ZAR (Dolar/Güney Afrika Randı)", "1 doların Güney Afrika Randı karşılığı.",
     "1 USD için kaç ZAR ödendiğini gösterir. Rand, emtia (altın, platin) ihracatı ve risk iştahı ile hareket eden, likit bir gelişen piyasa kurudur.",
     ["Altın ve platin gibi metallerle ilişkilidir.", "Küresel risk iştahının hızlı tepki veren göstergesidir.", "JSE ve ZA10Y serileriyle birlikte okunur."], "Yahoo, ZAR=X, günlük."),
    ("GBPUSD", "GBP/USD (Sterlin/Dolar)", "1 İngiliz sterlininin ABD doları karşılığı.",
     "1 GBP için kaç USD ödendiğini gösterir. Yükselmesi sterlinin güçlendiği anlamına gelir. \"Cable\" olarak da anılır. Birim: USD.",
     ["BoE ve Fed faiz farkları ile İngiltere verilerinden etkilenir.", "Dolar endeksi içinde küçük bir paya sahiptir.", "FTSE 100 ile ters ilişki gösterebilir (sterlin zayıflayınca yurt dışı gelirli şirketler kazanır)."], "Yahoo, GBPUSD=X, günlük."),
    ("USDHKD", "USD/HKD (Dolar/Hong Kong Doları)", "1 doların Hong Kong Doları karşılığı; kur dolara sabitlidir.",
     "HKD, yaklaşık 7,75 civarında dar bir bant içinde USD'ye sabitlenmiştir (currency peg, yaklaşık). Bu yüzden normalde çok az oynar. Banttan kopma Hong Kong finansal stresi hakkında bilgi verebilir.",
     ["Bant uçlarına yaklaşması Hong Kong'da likidite stresini gösterebilir.", "Hang Seng'in USD'ye çevrilmesi için kullanılır.", "Normalde dalgalanmadığı için çoğu zaman az bilgi taşır."], "Yahoo, HKD=X, günlük."),
]:
    _unit = "" if _k == "GBPUSD" else " Birim: yerel para birimi / 1 USD."
    _e(_k, _ad, _ks, _nd + _unit,
       "Doğrudan alınıp satılır (döviz); bu para birimi çiftlerine bazı aracı kurumlarda, vadeli ve opsiyon ürünlerinde erişilebilir. Bankalarda bu para her zaman doğrudan hesap olarak sunulmayabilir.",
       _FX_NEREDE, _FX_TR, _et, _tk, _FX_NOT)

# ---------------------------------------------------------------- EMTIA
_e("XAUUSD", "Altın (ons, USD)", "Altının ons başına USD fiyatı (COMEX vadelisi).",
   "Altın, küresel güvenli liman ve enflasyon/dolar karşıtı varlık olarak görülür. Pano, COMEX'teki sürekli front-month GC=F vadeli kontratını kullanır. "
   "Birim: 1 troy ons (yaklaşık 31,1035 gram) başına USD.",
   "Vadeli/fon üzerinden: COMEX GC vadelisi, altın ETF'leri (ör. GLD, IAU) ve fiziki altın. Spot altın (XAU/USD) OTC piyasada işlem görür.",
   "COMEX vadelisi yaklaşık neredeyse 24 saat, haftada 5 gün işlem görür (kısa günlük bakım arası). Panoda COMEX seans kapanışı kullanılır.",
   "Bankalar ve kuyumcular gram altın/külçe sunar; Borsa İstanbul'da altın ürünleri ve fonlar (zaman içinde değişebilir) vardır. " + _DANIS,
   ["Reel faizler ve dolar güçlenince genelde baskı altında kalır.", "Jeopolitik ve finansal stres dönemlerinde talep artabilir.",
    "Merkez bankası alımları fiyatı destekleyebilir.", "GRAMALTIN'in ham maddesidir."],
   "Yahoo, GC=F, günlük.", _VADELI_NOT)
_e("GRAMALTIN", "Gram Altın (TL)", "1 gram altının Türk Lirası karşılığı; panoda hesaplanır.",
   "Türetilmiş seridir: gram altın = ons altın (GC=F) x USDTRY (TRY=X) / 31,1035. 31,1035 bir troy onsun gram karşılığıdır. "
   "İki bileşenin de verisi olan ortak günlerde hesaplanır. Birim: TL/gram. Yerel piyasadaki fiyatlar, banka makası, vergi ve işçilik nedeniyle bundan farklı olabilir.",
   "Panodaki seri hesaplamadır, işlem görmez. Gram altına yakın ürünler: banka gram altın hesapları, fiziki altın, Borsa İstanbul altın ürünleri ve altın fonları.",
   "Dünya altını ve USD/TRY ile birlikte hareket eder. Yerel fiziki piyasa Türkiye iş saatlerinde yoğundur.",
   "Bankalar ve kuyumcular (fiziki/gram altın hesabı), Borsa İstanbul'daki altın ürünleri ve altın fonları. Ayrıntı ve maliyetler için kurumunuza danışın.",
   ["Hem küresel altına hem TL değer kaybına duyarlıdır; TL'de çoğu zaman enflasyona karşı korunma aracı olarak izlenir.", "Ons düşse bile USDTRY yükselirse TL fiyatı artabilir.",
    "Panoda yerel yatırımcı için ons fiyatını TL'ye çevirir."],
   "Türetilmiş: GC=F x TRY=X / 31,1035, günlük.", "Bileşenlerin kapanış saatleri farklı olabilir. " + _VADELI_NOT)
_e("XAGUSD", "Gümüş (ons, USD)", "Gümüşün ons başına USD fiyatı (COMEX vadelisi).",
   "Gümüş hem değerli metal hem sanayi metalidir (güneş paneli, elektronik). Pano, COMEX'teki sürekli SI=F vadelisini kullanır. Birim: troy ons başına USD.",
   "Vadeli/fon üzerinden: COMEX SI vadelisi, gümüş ETF'leri (ör. SLV) ve fiziki gümüş.",
   "COMEX yaklaşık neredeyse 24 saat, haftada 5 gün. Panoda seans kapanışı kullanılır.",
   "Bankalarda gümüş hesapları ve fiziki gümüş; Borsa İstanbul'da bazı gümüş ürünleri olabilir. " + _DANIS,
   ["Altınla birlikte hareket eder ama daha oynaktır.", "Sanayi talebi ve küresel büyüme beklentilerinden etkilenir.", "Altın/gümüş oranı risk iştahı için izlenir."],
   "Yahoo, SI=F, günlük.", _VADELI_NOT)
_e("BRENT", "Brent Petrol", "Brent ham petrolün varil başına USD fiyatı (vadeli).",
   "Brent, Kuzey Denizi kaynaklı ham petrol referansıdır ve dünya petrol fiyatlamasının büyük bölümünün referansıdır. Pano, BZ=F sürekli vadelisini kullanır. Birim: varil başına USD.",
   "Vadeli/fon üzerinden: ICE Brent vadelisi, petrol ETF/ETP'leri (kontrat roll maliyeti içerir). Fiziki petrol bireysel olarak alınmaz.",
   "Vadeli kontratlar yaklaşık neredeyse 24 saat, haftada 5 gün işlem görür.",
   "Türk bireysel yatırımcı için erişim sınırlıdır: yurt dışı ürünlere imkân veren aracı kurumlar veya yurt dışı petrol ETF'leri. " + _DANIS,
   ["Enflasyon beklentilerini ve ithalatçı ülkelerin (Türkiye, Hindistan) dış dengesini etkiler.", "Jeopolitik ve OPEC kararlarından etkilenir.", "Petrol ihraç eden ülkelerin para birimlerini destekleyebilir."],
   "Yahoo, BZ=F, günlük.", _VADELI_NOT)
_e("BAKIR", "Bakır", "Bakırın libre (pound) başına USD fiyatı (COMEX vadelisi).",
   "Bakır, inşaat, enerji ve elektronikte yaygın kullanıldığı için küresel sanayi ve Çin büyümesi hakkında ipucu verir (\"Dr. Copper\"). Pano, HG=F sürekli vadelisini kullanır. Birim: pound başına USD (1 pound yaklaşık 0,4536 kg).",
   "Vadeli/fon üzerinden: COMEX HG vadelisi, bakır ETF/ETP'leri. Fiziken bireysel olarak pratik değildir.",
   "COMEX yaklaşık neredeyse 24 saat, haftada 5 gün.",
   "Doğrudan ürün sınırlıdır; yurt dışı ETF'lere imkân veren aracı kurumlar. " + _DANIS,
   ["Küresel ve Çin sanayi talebinin göstergesidir.", "Gelişen piyasa ve emtia ihraç eden para birimleriyle ilişkilidir.", "Zayıflayan bakır büyüme endişesine işaret edebilir."],
   "Yahoo, HG=F, günlük.", _VADELI_NOT)

# ---------------------------------------------------------------- BORSA
_e("BIST100", "BIST 100", "Borsa İstanbul'daki en büyük 100 şirketin endeksi.",
   "Borsa İstanbul tarafından hesaplanan, piyasa değeri ve işlem hacmine göre seçilen 100 hisseden oluşan endekstir. Birim: endeks puanı (TL bazlı).",
   _ENDEKS_ISLEM + "Örnekler: BIST30 endeks vadeli kontratları (VİOP), BIST endeksini izleyen borsa yatırım fonları (ETF) ve endeks fonları; ürün listesi değişebilir.",
   "Borsa İstanbul, hafta içi; sürekli işlem yaklaşık 10:00-18:00 (Türkiye saati, değişebilir). Panoda yaklaşık 15:00 UTC kapanış kullanılır.",
   "Hisseler doğrudan aracı kurumlarla; BIST30 vadeli kontratları VİOP'ta; endeks fonları/ETF'ler TEFAS veya borsada. " + _DANIS,
   ["Türkiye'nin risk algısı, TL ve faiz beklentileriyle yakından bağlıdır.", "TL değer kaybında nominal TL endeks yükselirken USD bazlı getiri farklı olabilir.", "Bankalar endekste ağırlıklıdır; faiz kararlarına duyarlıdır."],
   "Yahoo, XU100.IS, günlük (TL).", "Endeks TL cinsindendir; USD bazı için USDTRY ile çevrilir. " + _BORSA_NOT)
_e("SPX", "S&P 500", "ABD'nin en büyük 500 şirketinin piyasa değeri ağırlıklı endeksi.",
   "S&P Dow Jones Indices tarafından hesaplanır; ABD hisse piyasasının büyük bölümünü temsil eder. Birim: endeks puanı, USD.",
   _ENDEKS_ISLEM + "Örnekler: SPY, VOO, IVV (ETF'ler); CME ES ve MES vadelileri; opsiyonlar.",
   "NYSE/Nasdaq normal seans: 09:30-16:00 New York saati; Türkiye saatiyle yaklaşık 16:30-23:00 (ABD/Türkiye yaz saati farkına göre değişebilir). Panoda yaklaşık 21:00 UTC kapanış kullanılır. Vadeliler neredeyse 24 saat.",
   _YD_TR, ["Küresel hisse piyasasının ve risk iştahının ana referansıdır.", "Fed faizi, kurumsal karlar ve büyüme verilerinden etkilenir.", "Birçok varlıkla (BTC, gelişen piyasa hisseleri) korelasyonu izlenir."],
   "Yahoo, ^GSPC, günlük (USD).", "Fiyat endeksidir (temettüler dahil değil). " + _BORSA_NOT)
_e("NASDAQ", "Nasdaq Composite", "Nasdaq borsasındaki binlerce hissenin endeksi; teknoloji ağırlıklı.",
   "Nasdaq'ta işlem gören hisselerin büyük çoğunluğunu içerir; büyük teknoloji şirketlerinin ağırlığı yüksektir. Birim: endeks puanı, USD. Not: Nasdaq-100 farklı bir endekstir.",
   _ENDEKS_ISLEM + "Örnekler: Nasdaq-100'ü izleyen QQQ ETF'i ve NQ vadelisi (Nasdaq-100; Composite'e yakın ama aynı değildir); Composite için doğrudan ürün sınırlıdır.",
   "ABD seansı yaklaşık 16:30-23:00 Türkiye saati (yaz saati nedeniyle değişebilir). Panoda yaklaşık 21:00 UTC kapanış.",
   _YD_TR, ["Teknoloji ve büyüme hisselerine duyarlıdır; faiz artışlarında daha çok etkilenir.", "Kripto ve risk iştahıyla yakın ilişki gösterebilir.", "S&P 500'ün daha oynak kuzeni gibidir."],
   "Yahoo, ^IXIC, günlük (USD).", "Fiyat endeksidir. " + _BORSA_NOT)
for _k, _ad, _ks, _nd, _isl, _ner, _et, _kod, _nt in [
    ("DAX", "DAX (Almanya)", "Frankfurt'taki en büyük 40 Alman şirketinin endeksi.",
     "Deutsche Börse tarafından hesaplanır. Birim: endeks puanı, EUR. DAX performans endeksidir, yani temettüler yeniden yatırılmış kabul edilir (S&P 500 gibi fiyat endeksi değildir).",
     "Örnekler: DAX vadelisi (Eurex FDAX), DAX izleyen ETF'ler.",
     "Xetra yaklaşık 09:00-17:30 Orta Avrupa saati; Türkiye saatiyle yaklaşık 11:00-19:30 (yaz saati farkına göre değişebilir). Panoda yaklaşık 16:30 UTC kapanış.",
     ["Avrupa sanayisi ve ihracatının, Çin talebinin göstergesidir.", "EUR/USD ve ECB politikasıyla ilişkilidir.", "Türkiye'nin büyük ticaret ortağı Almanya'nın ekonomisini yansıtır."], "Yahoo, ^GDAXI, günlük (EUR).",
     "EUR cinsindendir; USD bazı için EURUSD ile çevrilir."),
    ("FTSE", "FTSE 100 (Birleşik Krallık)", "Londra'da işlem gören en büyük 100 şirketin endeksi.",
     "FTSE Russell tarafından hesaplanır. Birim: endeks puanı, GBP. Şirketlerin büyük kısmı gelirlerini yurt dışından elde eder (enerji, banka, madencilik ağırlıklı).",
     "Örnekler: FTSE 100 vadelisi, FTSE 100 izleyen ETF'ler.",
     "Londra Menkul Kıymetler Borsası yaklaşık 08:00-16:30 Londra saati; Türkiye saatiyle yaklaşık 10:00-18:30 (yaz saati farkına göre değişebilir). Panoda yaklaşık 16:30 UTC kapanış.",
     ["Sterlin zayıflayınca (yurt dışı gelirler değerlenince) endeks genelde desteklenir.", "Emtia ve enerji şirketlerinin ağırlığı yüksektir.", "BoE politikasıyla ilişkilidir."], "Yahoo, ^FTSE, günlük (GBP).",
     "GBP cinsindendir; USD bazı için GBPUSD ile çevrilir."),
    ("NIKKEI", "Nikkei 225 (Japonya)", "Tokyo Borsası'ndaki 225 büyük Japon şirketin fiyat ağırlıklı endeksi.",
     "Nikkei Inc. tarafından hesaplanır. Fiyat ağırlıklıdır (hisse fiyatı yüksek olan şirket daha çok etkiler). Birim: endeks puanı, JPY.",
     "Örnekler: Nikkei 225 vadelileri (OSE, CME), Nikkei izleyen ETF'ler.",
     "Tokyo Borsası yaklaşık 09:00-15:30 Tokyo saati; Türkiye saatiyle yaklaşık 03:00-09:30. Panoda yaklaşık 06:00 UTC kapanış.",
     ["Yen zayıflayınca ihracatçı şirketler kazandığı için endeks genelde yükselir.", "BoJ politikasından etkilenir.", "Asya seansının ilk büyük göstergelerindendir."], "Yahoo, ^N225, günlük (JPY).",
     "JPY cinsindendir; USD bazı için USDJPY ile çevrilir."),
    ("SHANGHAI", "Shanghai Composite (Çin)", "Şanghay Borsası'nda işlem gören tüm hisselerin endeksi.",
     "Şanghay Menkul Kıymetler Borsası'nın ana endeksidir. Birim: endeks puanı, CNY. Piyasaya devlet etkisi büyüktür ve yabancı yatırımcı erişimi sınırlıdır.",
     "Endeksi izleyen ürünler sınırlıdır; yurt dışı ETF'ler (A-share) ve Stock Connect gibi yollar vardır.",
     "Şanghay yaklaşık 09:30-15:00 Çin saati; Türkiye saatiyle yaklaşık 04:30-10:00. Panoda yaklaşık 07:00 UTC kapanış.",
     ["Çin ekonomisi ve politika teşviklerinin göstergesidir.", "Bakır ve emtia talebi ile ilişkilidir.", "Yabancı erişimi sınırlı olduğundan yerel yatırımcı duyarlılığını yansıtır."], "Yahoo, 000001.SS, günlük (CNY).",
     "Veri kalitesi şüpheli: Yahoo'da eksik/hatalı günler olabilir. CNY cinsindendir; USD için USDCNY ile çevrilir."),
    ("HANGSENG", "Hang Seng (Hong Kong)", "Hong Kong Borsası'ndaki büyük şirketlerin endeksi.",
     "Hang Seng Indexes tarafından hesaplanır. Çin'e ve teknoloji/finans şirketlerine maruz kalmayı yansıtır. Birim: endeks puanı, HKD.",
     "Örnekler: Hang Seng vadelileri (HKEX), Hang Seng ETF'leri (Hong Kong'da).",
     "Hong Kong yaklaşık 09:30-16:00 Hong Kong saati (öğle arası var); Türkiye saatiyle yaklaşık 04:30-11:00. Panoda yaklaşık 08:00 UTC kapanış.",
     ["Çin ve küresel yatırımcıların Çin'e bakışını yansıtır.", "HKD USD'ye sabit olduğu için ABD faizlerinden etkilenir.", "Çin teşvik haberlerine hızlı tepki verir."], "Yahoo, ^HSI, günlük (HKD).",
     "HKD cinsindendir; USD için USDHKD ile çevrilir."),
    ("BOVESPA", "Bovespa (Brezilya)", "São Paulo Borsası'nın ana endeksi (Ibovespa).",
     "B3 tarafından hesaplanır. Madencilik, petrol ve bankalar ağırlıklıdır. Birim: endeks puanı, BRL.",
     "Örnekler: Brezilya endeks vadelileri (B3), Brezilya ETF'leri (ör. EWZ, ABD'de).",
     "B3 yaklaşık 10:00-17:00 São Paulo saati; Türkiye saatiyle yaklaşık 16:00-23:00 (yaz saati farkı olabilir). Panoda yaklaşık 20:00 UTC kapanış.",
     ["Emtia döngüsünün ve gelişen piyasa iştahının göstergesidir.", "Selic faiz kararlarına duyarlıdır.", "BRL ile birlikte okunur."], "Yahoo, ^BVSP, günlük (BRL).",
     "BRL cinsindendir; USD için USDBRL ile çevrilir."),
    ("NIFTY", "Nifty 50 (Hindistan)", "Hindistan Ulusal Borsası'ndaki 50 büyük şirketin endeksi.",
     "NSE tarafından hesaplanır. Birim: endeks puanı, INR.",
     "Örnekler: Nifty vadelileri (NSE, GIFT Nifty), Hindistan ETF'leri (ör. INDA, ABD'de).",
     "NSE yaklaşık 09:15-15:30 Hindistan saati; Türkiye saatiyle yaklaşık 06:45-13:00. Panoda yaklaşık 10:00 UTC kapanış.",
     ["Hindistan'ın büyüme hikâyesi ve yabancı portföy akışlarının göstergesidir.", "Petrol fiyatı ithalat maliyeti nedeniyle önemlidir.", "RBI faiz politikasından etkilenir."], "Yahoo, ^NSEI, günlük (INR).",
     "INR cinsindendir; USD için USDINR ile çevrilir."),
    ("JSE", "JSE All Share (Güney Afrika, proxy)", "Johannesburg Borsası geniş endeksi; panoda bir proxy olarak kullanılır.",
     "Pano, Yahoo'daki ^J203.JO (FTSE/JSE All Share) kodunu kullanır. Bu seri tam resmi seri değil, bir vekil (proxy) olarak kabul edilir ve veri kalitesi şüphelidir. Birim: endeks puanı, ZAR.",
     "Örnekler: JSE Top 40 vadelileri, Güney Afrika ETF'leri (ör. EZA, ABD'de).",
     "JSE yaklaşık 09:00-17:00 Güney Afrika saati; Türkiye saatiyle yaklaşık 10:00-18:00. Panoda yaklaşık 15:00 UTC kapanış.",
     ["Altın, platin ve madencilik emtialarına duyarlıdır.", "Gelişen piyasa risk iştahını yansıtır.", "ZAR ile birlikte okunur."], "Yahoo, ^J203.JO, günlük (ZAR).",
     "Proxy ve şüpheli kalite: eksik/sıçrama olabilir. ZAR cinsindendir; USD için USDZAR ile çevrilir."),
]:
    _e(_k, _ad, _ks, _nd, _ENDEKS_ISLEM + _isl, _ner, _YD_TR, _et, _kod, _nt + " " + _BORSA_NOT)

# ---------------------------------------------------------------- VIX
_e("VIX", "VIX (CBOE Volatilite Endeksi)", "ABD hisse piyasasında beklenen oynaklığı gösteren \"korku endeksi\".",
   "CBOE tarafından S&P 500 opsiyon fiyatlarından hesaplanır; önümüzdeki 30 günde beklenen yıllıklaştırılmış oynaklığı yüzde puan olarak ifade eder. "
   "Yüksek VIX, piyasada panik/belirsizlik ve opsiyonların pahalı olduğu anlamına gelir. Birim: endeks puanı (% oynaklık).",
   "Endeksin kendisi alınıp satılamaz. İlişkili enstrümanlar: VIX vadeli kontratları (CBOE), VIX opsiyonları ve VIX ETP'leri (ör. VXX, UVXY). "
   "Bu ürünler spot VIX'i birebir takip etmez; vadeli eğrisi ve roll maliyeti nedeniyle uzun vadede büyük değer kaybedebilir, riskli ürünlerdir.",
   "VIX ABD hisse seansında hesaplanır; vadeli kontratlar yaklaşık neredeyse 24 saat, haftada 5 gün işlem görür.",
   "VIX ürünleri çoğunlukla yurt dışı aracı kurumlarda bulunur; Türk aracı kurumlarda erişim ürüne göre değişir. " + _DANIS,
   ["S&P 500 düşerken genelde yükselir (ters ilişki).", "Risk iştahı ve piyasa stresinin kısa vadeli ölçüsüdür.", "Çok yüksek VIX dönemleri sıklıkla kriz ve dipler civarında görülür, ancak zamanlama garanti değildir."],
   "FRED, VIXCLS, günlük (yaklaşık 1 gün gecikmeli).",
   "VIX bir fiyat değil, beklenti ölçüsüdür; alınıp satılamaz. FRED'den yaklaşık 1 gün gecikmeyle geldiği için panoda en son gün eksik olabilir.")

# ---------------------------------------------------------------- TAHVIL GETIRILERI
_e("US2Y", "ABD 2 Yıllık Hazine Tahvili Getirisi", "ABD hükümetinin 2 yıl vadeli borçlanma faizi (%).",
   "ABD Hazinesi'nin 2 yıl vadeli tahvilinin getirisidir; piyasanın Fed politika faizinin önümüzdeki 2 yıldaki yolu hakkındaki beklentisine çok duyarlıdır. Birim: yıllık yüzde (%).",
   _TAHVIL_ISLEM + "Örnekler: ABD kısa vadeli Hazine ETF'leri (ör. SHY), 2 yıllık Treasury vadelisi (CME ZT).",
   "Tahvil piyasası OTC, yaklaşık neredeyse 24 saat (haftada 5 gün). Panoda FRED günlük verisi kullanılır.",
   _YD_TR, ["Fed beklentilerinin en duyarlı göstergesidir.", "Yüksek faiz doları destekler, hisse ve kripto üzerinde baskı yaratabilir.", "US10Y ile farkı (eğri) resesyon sinyali olarak izlenir."],
   "FRED, DGS2, günlük (yaklaşık 1 gün gecikmeli).", "Birim yüzde (%) olduğundan değişim baz puan (bp) ile ifade edilir. Oran olduğu için fiyat gibi yüzde getiri hesaplanmaz; fark kullanılır.")
_e("US10Y", "ABD 10 Yıllık Hazine Tahvili Getirisi", "ABD hükümetinin 10 yıl vadeli borçlanma faizi (%); küresel faiz referansı.",
   "ABD 10 yıllık Hazine tahvilinin getirisidir. Dünyadaki birçok kredi ve değerleme için \"risksiz oran\" referansıdır. Birim: yıllık yüzde (%).",
   _TAHVIL_ISLEM + "Örnekler: ABD uzun vadeli Hazine ETF'leri (ör. IEF, TLT), 10 yıllık Treasury vadelisi (CME ZN).",
   "OTC, yaklaşık neredeyse 24 saat (haftada 5 gün). Panoda FRED günlük verisi.",
   _YD_TR, ["Yüksek getiri, büyüme hisselerinin değerlemesine ve altın gibi getirisiz varlıklara baskı yapabilir.", "Küresel borçlanma maliyetini ve gelişen piyasa akışlarını etkiler.", "Enflasyon ve büyüme beklentilerini yansıtır."],
   "FRED, DGS10, günlük (yaklaşık 1 gün gecikmeli).", "Birim yüzde (%); fark kullanılır. Yaklaşık 1 gün gecikme.")
for _k, _ad, _ks, _ulke, _kod, _dolar in [
    ("DE10Y", "Almanya 10 Yıllık Tahvil Getirisi (aylık)", "Almanya hükümetinin 10 yıl vadeli borçlanma faizi; euro bölgesi referansı.", "Almanya", "IRLTLT01DEM156N", "Bund"),
    ("JP10Y", "Japonya 10 Yıllık Tahvil Getirisi (aylık)", "Japonya hükümetinin 10 yıl vadeli borçlanma faizi.", "Japonya", "IRLTLT01JPM156N", "JGB"),
    ("ZA10Y", "Güney Afrika 10 Yıllık Tahvil Getirisi (aylık)", "Güney Afrika hükümetinin 10 yıl vadeli borçlanma faizi.", "Güney Afrika", "IRLTLT01ZAM156N", "yerel devlet tahvili")]:
    _e(_k, _ad, _ks,
       _ulke + " 10 yıllık devlet tahvilinin getirisidir (" + _dolar + "). Birim: yıllık yüzde (%). OECD verisi FRED üzerinden aylık ortalama olarak gelir.",
       _TAHVIL_ISLEM + "Örnek ürünler ülkeye göre değişir (yerel tahvil, tahvil ETF'leri, vadeliler).",
       "Tahvil piyasası OTC; panoda günlük değil aylık ortalama değer kullanılır.",
       _YD_TR, ["Bölgesel faiz ve enflasyon beklentilerini gösterir.", "ABD getirisiyle farkı küresel sermaye akışlarını etkiler.", "Para birimiyle birlikte okunur."],
       "FRED/OECD, " + _kod + ", aylık.",
       "Aylık ortalamadır ve ay başı tarihli gösterilir; yani o tarihte henüz gerçekleşmemiş günlerin ortalamasını içerir. Gün gün analizde dikkatli kullanılmalı, anlık seviye değildir.")

# ---------------------------------------------------------------- POLITIKA FAIZLERI
_e("FED", "Fed Politika Faizi (hedef üst sınır)", "ABD Merkez Bankası'nın federal fon faizi hedef aralığının üst sınırı.",
   "Federal Reserve (Fed), kısa vadeli faiz için bir hedef aralık belirler; pano aralığın üst sınırını (DFEDTARU) gösterir. Dünyadaki en etkili politika faizidir. Birim: yıllık yüzde (%). Toplantı kararlarıyla basamaklı değişir.",
   _POLITIKA_ISLEM + "Beklentiyi gösteren araçlar: Fed Funds vadelisi, 2 yıllık Hazine getirisi.", "İşlem görmez; kararlar yaklaşık yılda 8 FOMC toplantısında açıklanır.",
   "Doğrudan alınamaz. Dolar mevduatı/dolar para piyasası fonları ve kısa vadeli tahvillerle dolaylı ilişki kurulur. " + _DANIS,
   ["Küresel likidite ve dolar gücünün ana belirleyicisi.", "Faiz arttıkça riskli varlıklar (hisse, kripto) genelde baskı altında kalır.", "Gelişen piyasa para birimlerini etkiler."],
   "FRED, DFEDTARU, günlük, basamaklı.", "Basamaklıdır; günlük görünse de sadece karar günlerinde değişir.")
_e("ECB", "ECB Mevduat Faizi", "Avrupa Merkez Bankası'nın bankaların fazla likiditesini yatırdığı faiz oranı.",
   "ECB'nin ana politika araçlarından biri olan mevduat kolaylığı faizidir; politika duruşunu belirleyen oran olarak izlenir. Birim: yıllık yüzde (%).",
   _POLITIKA_ISLEM + "Beklentiyi gösteren araçlar: euro bölgesi kısa vadeli tahvil getirileri.", "İşlem görmez; toplantı kararlarıyla basamaklı değişir.",
   "Doğrudan alınamaz; euro mevduatı/fonları dolaylı ilişkilidir. " + _DANIS,
   ["Euro ve euro bölgesi hisseleri/tahvillerini etkiler.", "Fed ile farkı EUR/USD'yi etkiler.", "Küresel faiz iklimini gösterir."],
   "FRED, ECBDFR, günlük, basamaklı.", "Basamaklıdır; geçmişte negatif değerler alabilmiştir.")
for _k, _ad, _ks, _nd, _bis, _et in [
    ("BOE", "Bank of England Politika Faizi", "Birleşik Krallık Merkez Bankası'nın Bank Rate politika faizi.", "BoE'nin belirlediği Bank Rate'tir. Birim: yıllık yüzde (%).", "M.GB", ["Sterlini (GBPUSD) ve İngiliz tahvillerini etkiler.", "Fed ve ECB ile farkı karşılaştırmada kullanılır.", "FTSE'yi dolaylı etkiler."]),
    ("BOJ", "Bank of Japan Politika Faizi", "Japonya Merkez Bankası'nın politika faizi.", "BoJ'un politika faizidir; uzun süre sıfır/negatife yakın kalmıştır. Birim: yıllık yüzde (%).", "M.JP", ["Yen carry trade'ini belirler; faiz artışı yeni güçlendirebilir.", "USDJPY ve Nikkei üzerinde etkili.", "Küresel düşük faiz fonlamasının temel kaynaklarından biridir."]),
    ("PBOC", "PBoC LPR 1 Yıllık", "Çin'de bankaların kredi faizi referansı (1 yıllık Loan Prime Rate).", "Çin Merkez Bankası (PBoC) yönlendirmesiyle bankaların belirlediği 1 yıllık kredi referans faizidir (LPR). Birim: yıllık yüzde (%).", "M.CN", ["Çin kredi koşullarını ve teşvik yönünü gösterir.", "Yuan, Shanghai ve emtia talebini etkiler.", "Çin'in gevşeme/sıkılaşma sinyali olarak izlenir."]),
    ("TCMB", "TCMB 1 Haftalık Repo Faizi", "Türkiye Cumhuriyet Merkez Bankası'nın ana politika faizi.", "TCMB'nin bir haftalık repo ihale faizidir, ana politika faizidir. Birim: yıllık yüzde (%). Kararlar PPK toplantılarında açıklanır.", "M.TR", ["TL, TL mevduat/tahvil faizi ve BIST100 üzerinde belirleyicidir.", "USDTRY'yi ve enflasyon beklentilerini etkiler.", "Panoda Türkiye'ye yerel bağlam sağlar."]),
    ("SELIC", "Brezilya Selic Faizi", "Brezilya Merkez Bankası'nın politika faizi (Selic).", "Brezilya Merkez Bankası'nın hedef Selic oranıdır. Birim: yıllık yüzde (%).", "M.BR", ["BRL ve Bovespa üzerinde etkili.", "Yüksek faiz BRL carry trade'ini çekebilir.", "Gelişen piyasa para politikasının referanslarından biridir."]),
    ("INDIA_REPO", "Hindistan Repo Faizi", "Hindistan Merkez Bankası (RBI) repo faizi.", "RBI'nin bankalara kısa vadeli borç verdiği repo oranıdır; ana politika faizidir. Birim: yıllık yüzde (%).", "M.IN", ["INR ve Nifty'yi etkiler.", "Enflasyon ve büyüme dengesini yansıtır.", "Gelişen piyasa faiz seviyeleri için referanstır."]),
    ("ZA_REPO", "Güney Afrika Repo Faizi", "Güney Afrika Merkez Bankası (SARB) repo faizi.", "SARB'ın ana politika faizi olan repo oranıdır. Birim: yıllık yüzde (%).", "M.ZA", ["ZAR ve JSE'yi etkiler.", "ZA10Y tahvil getirisi ile birlikte okunur.", "Gelişen piyasa faiz seviyeleri için referanstır."]),
]:
    _e(_k, _ad, _ks, _nd, _POLITIKA_ISLEM + "Beklenti için ilgili ülkenin kısa vadeli tahvil getirisi izlenir.",
       "İşlem görmez; kararlar merkez bankasının takvimli toplantılarında açıklanır.",
       "Doğrudan alınamaz; ilgili ülkenin para birimi, mevduatı veya devlet tahvilleri dolaylı ilişkilidir. " + _DANIS,
       _et, "BIS, WS_CBPOL/" + _bis + ", aylık.", _POLITIKA_NOT)

# ---------------------------------------------------------------- v1 disi
_e("USDTRY_TCMB", "USD/TRY Resmi Kur (TCMB, EVDS)", "TCMB'nin açıkladığı resmi USD/TRY kuru (v1'de kapalı).",
   "Merkez Bankası'nın EVDS sisteminde yayınladığı gösterge döviz kuru. Piyasa kurundan küçük farklar gösterebilir. Birim: 1 USD için TL.",
   "Gösterge kurdur, doğrudan işlem görmez; piyasa kuru üzerinden işlem yapılır.", "Türkiye iş günlerinde yayımlanır.",
   "Bankalarda döviz işlemleri. " + _DANIS, ["USDTRY ile karşılaştırma için.", "Resmi kaynak doğrulaması.", "v1'de varsayılan olarak kapalıdır."],
   "EVDS, TP.DK.USD.A.YTL (erişim anahtarı gerekir), günlük.", "v1'de kullanılmaz; anahtar yoksa atlanır.")


def bilgi_karti(kod):
    """Bir varligin bilgi kartini tek bir Markdown string'i olarak dondurur."""
    b = BILGI.get(kod)
    if b is None:
        return ("### " + str(kod) + "\n\nBu seri için henüz bir bilgi kartı yazılmadı. "
                "Kaynak ve birim bilgisi için panoda ilgili serinin sayfasına bakın.")

    etk = "\n".join("- " + s for s in b["etkiler"])
    return "\n".join([
        "## " + b["ad"] + " (`" + kod + "`)",
        "*" + b["kisa"] + "*",
        "",
        "### Nedir?", b["nedir"], "",
        "### Alınıp satılabilir mi?", b["islem"], "",
        "### Nerede ve ne zaman işlem görür?", b["nerede"], "",
        "### Türkiye'den erişim", b["turkiye"], "",
        "### Neyi etkiler / neden panoda?", etk, "",
        "### Panoda", b["panoda"], "",
        "### Notlar", b["notlar"], "",
        "---",
        "*Genel bilgilendirme amaçlıdır, yatırım tavsiyesi değildir. Saatler ve ürün isimleri yaklaşıktır ve değişebilir.*",
    ])
