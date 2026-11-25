"""Afet Atlas koyu tema ve Yardım regresyon testleri."""
import unittest
from pathlib import Path
import tomllib
import pandas as pd
from atlas_sabit_harita import _hafif_il_geometrileri, hazirla_harita
from atlas_tema import ortak_kontrol_css

ROOT=Path(__file__).resolve().parent

class KoyuTemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.iller=[f['properties']['il'] for f in _hafif_il_geometrileri()]
        cls.tablo=pd.DataFrame({'İl':cls.iller,'Nüfus':list(range(81))})

    def test_koyu_tema_tek_secenek(self):
        config=tomllib.loads((ROOT/'.streamlit/config.toml').read_text(encoding='utf-8'))
        self.assertEqual(config['theme']['base'],'dark')
        app=(ROOT/'app.py').read_text(encoding='utf-8')
        self.assertNotIn('atlas_gunduz_modu',app)
        self.assertNotIn('gunduz_tema_css',app)
        self.assertNotIn('Gündüz modu',app)
        self.assertIn('Yönetici paneli herkese açık mı?',app)

    def test_kirmizi_secimler(self):
        css=ortak_kontrol_css()
        for widget in ('stSelectbox','stMultiSelect','stPopover','gemini_btn_'):
            self.assertIn(widget,css)
        self.assertIn('background-color:#f04e66!important',css)

    def test_sabit_koyu_harita(self):
        html=hazirla_harita(self.tablo,'Nüfus','Nüfus','Ankara').get_root().render()
        self.assertIn('"dragging": false',html)
        self.assertIn('"scrollWheelZoom": false',html)
        self.assertIn('cursor:pointer!important',html)
        self.assertIn('#0c1a2e',html)

if __name__=='__main__':unittest.main()
