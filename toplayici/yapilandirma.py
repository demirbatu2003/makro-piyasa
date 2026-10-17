"""Yapilandirma ve seri katalogu. Ticker / kodlar arastirma/veri_fizibilite.md'den gelir."""
import os
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
VERI_DIZINI = KOK / "veri"
DB_YOLU = VERI_DIZINI / "makro.sqlite"
LOG_YOLU = VERI_DIZINI / "log.txt"

BASLANGIC = "2010-01-01"        # gecmis baslangici (onayli karar)
GERI_BINDIRME_GUN = 3           # revizyonlar icin geri bindirme
DENEME = 3                      # her kaynak cagrisi icin deneme sayisi
ZAMAN_ASIMI = 40                # saniye
KRIPTO_REFERANS_SAAT_UTC = 21   # kripto gunluk referansi: 21:00 UTC (1h kline, mumun acilis fiyati)
NABIZ_1M_GUN = 30               # 1m nabiz saklama suresi
NABIZ_1H_GUN = 90               # 1h nabiz saklama suresi
BAYAT_GUN = {"gunluk": 5, "aylik": 62}   # gecikmis esigi (takvim gunu)
SUPHE_GETIRI = 0.5              # tek gunde +-%50 ustu = suphe isareti

# EVDS key'i ortam degiskeninden okunur; yoksa EVDS yolu atlanir. Depoya yazilmaz.
EVDS_KEY = os.environ.get("MAKRO_EVDS_KEY", "")

BINANCE_TABANLAR = ["https://api.binance.com", "https://data-api.binance.vision"]

# Altcoin sepeti: sabit 10 coin, esit agirlik. Secim: 2026-10-16'da Binance 24s USDT hacmi
# siralamasi ilk 40'indan, BTC/ETH/SOL/stablecoin/tokenlestirilmis hisse-altin haric,
# yerlesik buyuk coinler (piyasa degeri + hacim). Hayatta kalma yanliligi vardir.
ALTCOINLER = ["XRP", "BNB", "DOGE", "ADA", "TRX", "AVAX", "LINK", "UNI", "NEAR", "SUI"]
ALTSEPET_MIN_COIN = 3           # sepet, getirisi olan en az 3 coin oldugu gunden baslar

# kod, ad, kategori, birim, kaynak, kaynak_kodu, frekans, kapanis_notu,
# para_birimi, usd_kur_kodu, usd_kur_ters, v1
# usd_kur_ters: 0 = kur USD-basina-yerel (USD deger = yerel / kur, orn. USDJPY);
#               1 = kur yerel-basina-USD (USD deger = yerel * kur, orn. EURUSD, GBPUSD).
_K = []
def _ekle(kod, ad, kat, birim, kaynak, kkod, frek, not_, pb=None, kur=None, ters=0, v1=1):
    _K.append(dict(kod=kod, ad=ad, kategori=kat, birim=birim, kaynak=kaynak, kaynak_kodu=kkod,
                   frekans=frek, kapanis_notu=not_, para_birimi=pb, usd_kur_kodu=kur,
                   usd_kur_ters=int(ters), v1=int(v1)))

_KR = "Binance 1h kline, 21:00 UTC fiyati (7/24)"
_ekle("BTC", "Bitcoin", "kripto", "fiyat", "binance", "BTCUSDT", "gunluk", _KR, "USD")
_ekle("ETH", "Ethereum", "kripto", "fiyat", "binance", "ETHUSDT", "gunluk", _KR, "USD")
_ekle("SOL", "Solana", "kripto", "fiyat", "binance", "SOLUSDT", "gunluk", _KR, "USD")
_ekle("ALTSEPET", "Altcoin sepeti (10 coin, esit agirlik, taban 100)", "kripto", "fiyat",
      "turetilmis", "ALT_*", "gunluk", _KR + "; esit agirlikli gunluk getiri bilesimi", "USD")
for _c in ALTCOINLER:
    _ekle("ALT_" + _c, "Sepet bileseni " + _c, "kripto", "fiyat", "binance", _c + "USDT",
          "gunluk", _KR, "USD", v1=0)

_FX = "Yahoo FX, ~24/5, Londra gece yarisi kapanisi"
for kod, ad, t in [("USDTRY", "USD/TRY", "TRY=X"), ("EURUSD", "EUR/USD", "EURUSD=X"),
                   ("DXY", "ABD Dolar Endeksi", "DX-Y.NYB"), ("USDJPY", "USD/JPY", "JPY=X"),
                   ("USDCNY", "USD/CNY", "CNY=X"), ("USDBRL", "USD/BRL", "BRL=X"),
                   ("USDINR", "USD/INR", "INR=X"), ("USDZAR", "USD/ZAR", "ZAR=X"),
                   ("GBPUSD", "GBP/USD", "GBPUSD=X"), ("USDHKD", "USD/HKD", "HKD=X")]:
    _ekle(kod, ad, "fx", "fiyat", "yahoo", t, "gunluk", _FX if kod != "DXY" else "Yahoo, ICE DXY, ABD seansi")

_VD = "Yahoo vadeli (front-month, roll sicramasi icerir), COMEX/NYMEX seans kapanisi"
_ekle("XAUUSD", "Altin (GC=F vadeli)", "emtia", "fiyat", "yahoo", "GC=F", "gunluk", _VD, "USD")
_ekle("GRAMALTIN", "Gram altin TL (GC=F x TRY=X / 31.1035)", "emtia", "fiyat", "turetilmis",
      "GC=F*TRY=X/31.1035", "gunluk", "Turetilmis; iki bilesenin ortak tarihinde", "TRY", "USDTRY", 0)
_ekle("XAGUSD", "Gumus (SI=F vadeli)", "emtia", "fiyat", "yahoo", "SI=F", "gunluk", _VD, "USD")
_ekle("BRENT", "Brent (BZ=F vadeli)", "emtia", "fiyat", "yahoo", "BZ=F", "gunluk", _VD, "USD")
_ekle("BAKIR", "Bakir (HG=F vadeli)", "emtia", "fiyat", "yahoo", "HG=F", "gunluk", _VD, "USD")

_B = [("BIST100", "BIST 100", "XU100.IS", "Istanbul seansi kapanisi (~15:00 UTC)", "TRY", "USDTRY", 0),
      ("BIST30", "BIST 30", "XU030.IS", "Istanbul seansi kapanisi (~15:00 UTC)", "TRY", "USDTRY", 0),
      ("SPX", "S&P 500", "^GSPC", "ABD seansi kapanisi (~21:00 UTC)", "USD", None, 0),
      ("NASDAQ", "Nasdaq Composite", "^IXIC", "ABD seansi kapanisi (~21:00 UTC)", "USD", None, 0),
      ("DAX", "DAX", "^GDAXI", "Frankfurt seansi kapanisi (~16:30 UTC)", "EUR", "EURUSD", 1),
      ("FTSE", "FTSE 100", "^FTSE", "Londra seansi kapanisi (~16:30 UTC)", "GBP", "GBPUSD", 1),
      ("NIKKEI", "Nikkei 225", "^N225", "Tokyo seansi kapanisi (~06:00 UTC)", "JPY", "USDJPY", 0),
      ("SHANGHAI", "Shanghai Composite", "000001.SS", "Shanghai seansi kapanisi (~07:00 UTC); kalite supheli", "CNY", "USDCNY", 0),
      ("HANGSENG", "Hang Seng", "^HSI", "Hong Kong seansi kapanisi (~08:00 UTC)", "HKD", "USDHKD", 0),
      ("BOVESPA", "Bovespa", "^BVSP", "Sao Paulo seansi kapanisi (~20:00 UTC)", "BRL", "USDBRL", 0),
      ("NIFTY", "Nifty 50", "^NSEI", "Mumbai seansi kapanisi (~10:00 UTC)", "INR", "USDINR", 0),
      ("JSE", "JSE All Share (proxy)", "^J203.JO", "Johannesburg seansi kapanisi (~15:00 UTC); proxy, kalite supheli", "ZAR", "USDZAR", 0)]
for kod, ad, t, n, pb, kur, ters in _B:
    _ekle(kod, ad, "borsa", "fiyat", "yahoo", t, "gunluk", n, pb, kur, ters)

_ekle("VIX", "VIX (CBOE)", "vix", "fiyat", "fred", "VIXCLS", "gunluk", "FRED, ABD seansi kapanisi, ~1 gun gecikmeli")
_ekle("US2Y", "ABD 2y getiri", "faiz", "faiz_yuzde", "fred", "DGS2", "gunluk", "FRED, ~1 gun gecikmeli")
_ekle("US10Y", "ABD 10y getiri", "faiz", "faiz_yuzde", "fred", "DGS10", "gunluk", "FRED, ~1 gun gecikmeli")
for kod, ad, s in [("DE10Y", "Almanya 10y getiri (aylik)", "IRLTLT01DEM156N"),
                   ("JP10Y", "Japonya 10y getiri (aylik)", "IRLTLT01JPM156N"),
                   ("ZA10Y", "G. Afrika 10y getiri (aylik)", "IRLTLT01ZAM156N")]:
    _ekle(kod, ad, "faiz", "faiz_yuzde", "fred", s, "aylik", "FRED/OECD aylik ortalama, ay baslangic tarihli")
_ekle("FED", "Fed hedef ust sinir", "politika", "faiz_yuzde", "fred", "DFEDTARU", "gunluk", "FRED gunluk, basamakli")
_ekle("ECB", "ECB mevduat faizi", "politika", "faiz_yuzde", "fred", "ECBDFR", "gunluk", "FRED gunluk, basamakli")
for kod, ad, ulke in [("BOE", "BoE politika faizi", "GB"), ("BOJ", "BoJ politika faizi", "JP"),
                      ("PBOC", "PBoC LPR 1y", "CN"), ("TCMB", "TCMB 1 haftalik repo", "TR"),
                      ("SELIC", "Brezilya Selic", "BR"), ("INDIA_REPO", "Hindistan repo", "IN"),
                      ("ZA_REPO", "G. Afrika repo", "ZA")]:
    _ekle(kod, ad, "politika", "faiz_yuzde", "bis", "WS_CBPOL/M." + ulke, "aylik",
          "BIS aylik donem sonu, ay baslangic tarihli, basamakli")
_ekle("USDTRY_TCMB", "USD/TRY resmi (TCMB, EVDS)", "fx", "fiyat", "evds", "TP.DK.USD.A.YTL",
      "gunluk", "EVDS sonrasi (key gerekir)", None, None, 0, v1=0)

KATALOG = _K
