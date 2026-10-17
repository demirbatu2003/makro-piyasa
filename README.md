# Makro Pano

Kendi PC'nde calisan, ucretsiz kaynaklarla beslenen makro varlik iliskileri panosu. Bu klasorde su an yalnizca **v1 veri hatti** hazir.

## Klasor yapisi

- `toplayici\` : veri toplama kodu (Python paketi). `oku.py` diger parcalarin kullandigi okuma arayuzudur.
- `veri\makro.sqlite` : tum veri (tek dosya; yedeklemek icin kopyalamak yeterli). `veri\log.txt` : hata/cekim gunlugu.
- `analiz\`, `pano\` : analiz kutuphanesi ve arayuz (ayri calisma).
- `TASARIM.md`, `FIKIR.md`, `arastirma\` : tasarim ve arastirma belgeleri.

## Komutlar (makro-pano klasorunden)

```
C:\Python314\python.exe -m toplayici gunluk   # eksikleri doldur + gunluk guncelle (3 gun geri bindirme)
C:\Python314\python.exe -m toplayici nabiz    # Binance BTC/ETH/SOL 1h (90 gun) ve 1m (30 gun) nabiz
C:\Python314\python.exe -m toplayici durum    # seri basina ilk/son tarih, satir sayisi, durum, son hata
```

Okuma (Python): `from toplayici.oku import katalog, gunluk_panel, nabiz, saglik`. Kur donusumu: `katalog()` icinde `usd_kur_kodu` ve `usd_kur_ters`
(False = kur USD-basina-yerel, USD deger = yerel / kur; True = kur yerel-basina-USD, USD deger = yerel * kur).

## Notlar

- Gecmis 2010-01-01'den baslar. Kripto gunluk referansi: Binance 1h mumunun 21:00 UTC acilis fiyati.
- Altcoin sepeti: XRP, BNB, DOGE, ADA, TRX, AVAX, LINK, UNI, NEAR, SUI (esit agirlik, taban 100; en az 3 coin verisi olan gunden baslar). Liste `toplayici\yapilandirma.py` icinde. Bugunun buyuk coinlerinden secildigi icin hayatta kalma yanliligi vardir.
- Aylik seriler (DE/JP/ZA 10y, BIS politika faizleri) ay baslangic tarihiyle saklanir.
- Gram altin ve altcoin sepeti turetilmis seridir; her `gunluk` calismasinda yeniden hesaplanir.

## Zamanlanmis gorevler

- `makro_pano_gunluk` : her gun 08:00, kacirilirsa en kisa surede calisir (`gunluk`).
- `makro_pano_nabiz` : saatte bir (`nabiz`).

Durdurmak / silmek:

```
schtasks /Delete /TN makro_pano_gunluk /F
schtasks /Delete /TN makro_pano_nabiz /F
```

## EVDS (TCMB) anahtari

v1'de EVDS yoktur; anahtar yoksa o yol atlanir. Anahtari almak icin evds2.tcmb.gov.tr'den ucretsiz profil ac, API anahtarini al ve ortam degiskeni olarak ekle:

```
setx MAKRO_EVDS_KEY "anahtarin"
```

(Yeni bir terminal/oturumdan sonra gecerli olur; zamanlanmis gorevler icin oturumu kapatip acmak gerekebilir.) Anahtar dosyalara yazilmaz. EVDS kodu henuz dogrulanmamistir (TP.DK.USD.A.YTL).

## Panoyu acmak

Masaustundeki **Makro Pano** kisayoluna (Makro Pano.vbs) cift tikla: sunucu GIZLI (konsol penceresiz) arka planda baslar, tarayici http://localhost:8502 adresinde acilir (statarb panosu 8501'de). Zaten aciksa ikinci sunucu baslatmaz, yalniz tarayiciyi acar. Tarayici sekmesini kapatmak sunucuyu kapatmaz.
**Durdurmak icin**: masaustundeki **Makro Pano Durdur** kisayolu (yalniz 8502'yi kapatir) ya da kenar cubugundaki 'Panoyu kapat' dugmesi. Sunucu beklenmedik kapanirsa 3 sn sonra kendini yeniden baslatir. Tum sunucu ciktisi: `veri\pano_log.txt` (2 MB'ta doner). Hata gorursen once tarayiciyi yenile (F5); duzelmezse 'Makro Pano' kisayoluna tekrar cift tikla.
Elle: `cd C:\Users\batuh\makro-pano` ardindan `C:\Python314\python.exe pano_baslat.py 8502 --tarayici`. Durdurma: `python pano_durdur.py 8502`.
Ekran 0'daki "Verileri guncelle" dugmesi `python -m toplayici gunluk` komutunu calistirir. Arayuz kodu `pano\` icindedir (`app.py`, `ortak.py`, `sayfalar\`); veri tabanina yalnizca okur (guncelle dugmesi disinda).
