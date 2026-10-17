import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "pano"))

from toplayici import oku
import varlik_bilgi as vb


def test_hepsi_var_ve_dolu():
    kat = oku.katalog()
    kodlar = set(kat[(kat["v1"] == True) | (kat["kod"].str.startswith("ALT_"))]["kod"])
    assert len(kodlar) == 56, len(kodlar)
    eksik = kodlar - set(vb.BILGI)
    assert not eksik, eksik
    for k in kodlar:
        for a in vb.ALANLAR:
            v = vb.BILGI[k].get(a)
            assert v and (isinstance(v, str) or all(v)), (k, a)
        assert 2 <= len(vb.BILGI[k]["etkiler"]) <= 4, k
        assert vb.bilgi_karti(k).startswith("## ")


def test_bilinmeyen():
    assert "XYZ" in vb.bilgi_karti("XYZ")


if __name__ == "__main__":
    test_hepsi_var_ve_dolu()
    test_bilinmeyen()
    print("OK", len(vb.BILGI))
