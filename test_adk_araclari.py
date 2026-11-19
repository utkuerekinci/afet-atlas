"""Gerçek 2025 verisinde ADK'nin Python araçlarını API anahtarsız test et."""
from pathlib import Path
import json
import importlib.util
import unittest
import pandas as pd
from hesaplama import puanlari_hesapla

DOSYA = Path(__file__).resolve().parent / "afet_atlas_adk" / "veri_araclari.py"
spec = importlib.util.spec_from_file_location("afet_atlas_veri_araclari", DOSYA)
modul = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modul)


class ADKAracTesti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        klasor = Path(__file__).resolve().parent / "indirilen_veriler"
        cls.deprem = pd.read_csv(klasor / "usgs_2025_m4_5.csv")
        sinir = json.loads((klasor / "turkiye_81_il.geojson").read_text(encoding="utf-8"))
        cls.il, cls.eslesen = puanlari_hesapla(cls.deprem, sinir, 0)
        cls.arac = {a.__name__: a for a in modul.araclari_olustur(
            cls.il, cls.deprem, cls.eslesen, 2025, 2025, 4.5, 0)}

    def test_veri_kapsami(self):
        k = self.arac["veri_kapsami"]()
        self.assertEqual(k["usgs_olay_sayisi"], 159)
        self.assertEqual(k["il_olay_eslesme_sayisi"], 33)
        self.assertEqual(k["il_sayisi"], 81)

    def test_il_puani(self):
        b = self.arac["il_ozeti"]("Balıkesir")
        self.assertEqual((b["deprem_eslesmesi_sayisi"], b["toplam_olay_puani"]), (18, 30))
        i = self.arac["il_ozeti"]("İSTANBUL")
        self.assertEqual(i["deprem_eslesmesi_sayisi"], 0)
        self.assertIsNone(i["goreli_endeks_100_uzerinden"])
        self.assertIn("hata", self.arac["il_ozeti"]("Atlantis"))

    def test_karsilastirma(self):
        k = self.arac["il_karsilastir"]("Ankara", "İstanbul")
        self.assertEqual(k["birinci"]["toplam_olay_puani"], 4)
        self.assertEqual(k["ikinci"]["toplam_olay_puani"], 0)

    def test_olay_listeleme(self):
        k = self.arac["ilin_en_buyuk_depremleri"]("Balıkesir", 3)
        self.assertEqual(len(k["olaylar"]), 3)
        self.assertGreaterEqual(k["olaylar"][0]["buyukluk"], k["olaylar"][1]["buyukluk"])
        self.assertIn("hata", self.arac["ilin_en_buyuk_depremleri"]("Balıkesir", 100))

    def test_siralama(self):
        en = self.arac["hareketliligi_en_yuksek_iller"]()
        self.assertEqual(en["iller"][0]["il"], "Balıkesir")
        dus = self.arac["hareketliligi_en_dusuk_kayitli_iller"]()
        self.assertEqual(dus["sifir_eslesmeli_il_sayisi"], 72)


if __name__ == "__main__":
    unittest.main()
