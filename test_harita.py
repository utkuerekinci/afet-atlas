"""Haritanın 81 ili çizip çizmediğini gerçek veriyle test eder; internet gerekmez."""
from pathlib import Path
import json
import unittest
import pandas as pd
from hesaplama import puanlari_hesapla
from harita_cizimi import turkiye_haritasi

KOK = Path(__file__).resolve().parent / "indirilen_veriler"

class HaritaTesti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo = json.loads((KOK / "turkiye_81_il.geojson").read_text(encoding="utf-8"))
        cls.depremler = pd.read_csv(KOK / "usgs_2025_m4_5.csv")

    def test_81_il_ciziliyor(self):
        sonuc, _ = puanlari_hesapla(self.depremler, self.geo, 0)
        fig = turkiye_haritasi(self.geo, sonuc)
        self.assertEqual(len(fig.data), 82)  # 81 il ve renk ölçeği
        self.assertEqual({t.name for t in fig.data[:-1]}, set(sonuc["İl"]))
        self.assertTrue(all(t.fill == 'toself' for t in fig.data[:-1]))
        self.assertTrue(all(len(t.x) > 5 for t in fig.data[:-1]))
        self.assertFalse(any(t.type == 'choropleth' for t in fig.data))

    def test_her_mesafe_icin_harita(self):
        for mesafe in (0, 50, 75, 100, 150):
            with self.subTest(mesafe=mesafe):
                sonuc, eslesen = puanlari_hesapla(self.depremler, self.geo, mesafe)
                fig = turkiye_haritasi(self.geo, sonuc)
                self.assertEqual(len(fig.data), 82)
                self.assertEqual(len(sonuc), 81)

if __name__ == "__main__":
    unittest.main()
