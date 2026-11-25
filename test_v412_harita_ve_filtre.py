"""v4.12: admin veri bağlantısı eksikliğinde güvenli Türkiye haritası, tek ticaret puanı ve filtre düzeni."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import os
import tempfile
import unittest

import pandas as pd
from genel_bakis import prepare_provinces, available_layers, layer_frame, city_summary, provincial_safety_scores
from atlas_sabit_harita import hazirla_harita
from ilce_veri import fetch_population, read_sege_csv, combine
from ticaret_veri import zenginlestir_ilceler
from veri import il_sinirlarini_getir
import veri

BASE=Path(__file__).resolve().parent

class MapUX412(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pop=fetch_population()
        merged,_=combine(pop,read_sege_csv())
        cls.districts, cls.status=zenginlestir_ilceler(merged)
        cls.geo=il_sinirlarini_getir()
        cls.districts, cls.prov=prepare_provinces(cls.districts,cls.geo)

    def test_home_trade_average_four_sectors_only(self):
        self.assertEqual(available_layers(self.prov,'Ticari hareketlilik'), ['Ortalama ticari puan'])
        cols=['Fırsat puanı · Yeme-içme','Fırsat puanı · Perakende',
              'Fırsat puanı · Hizmetler','Fırsat puanı · Lojistik']
        pd.testing.assert_series_equal(self.prov['Ortalama ticari puan'],
                                       self.prov[cols].mean(axis=1).round(1),check_names=False)
        data,col,label=layer_frame(self.prov,'Ticari hareketlilik','Ortalama ticari puan')
        self.assertEqual(len(data),81)
        info=city_summary(self.districts,self.prov,'Ankara','Ticari hareketlilik','Ortalama ticari puan')
        self.assertEqual(info['key_label'],'Ortalama ticari puan')
        self.assertIn('ortalama',info['text'])
        for _ in range(1):
            html=hazirla_harita(data,col,label,'Ankara').get_root().render()
            self.assertEqual(html.count('"atlas-score-label"'),81)
            self.assertIn('atlas-score-chip',html)
            self.assertIn('"dragging": false',html)

    def test_home_disaster_seven_inputs_and_fallback(self):
        data=provincial_safety_scores()
        self.assertEqual(len(data),81)
        with patch('genel_bakis.afet_guvenlik_bilesenleri',side_effect=OSError('data unavailable')):
            restored=provincial_safety_scores()
        pd.testing.assert_frame_equal(data.sort_values('İl').reset_index(drop=True),
                                      restored.sort_values('İl').reset_index(drop=True))
        for _ in range(1):
            html=hazirla_harita(data,'Güvenlik skoru (%)','Güvenlik skoru (%)','Ankara').get_root().render()
            self.assertEqual(html.count('"atlas-score-label"'),81)

    def test_missing_private_geojson_does_not_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(veri,'VERI_KLASORU',Path(tmp)):
                with patch.object(veri,'_indir',side_effect=AssertionError('network attempted')):
                    geo=veri.il_sinirlarini_getir()
        self.assertEqual(len(geo['features']),81)

    def test_ui_order_and_removed_messages(self):
        ui=(BASE/'atlas_ui.py').read_text(encoding='utf-8')
        app=(BASE/'app.py').read_text(encoding='utf-8')
        light=(BASE/'atlas_tema.py').read_text(encoding='utf-8')
        self.assertNotIn('İşletme katmanı hazırlanıyor',ui)
        self.assertLess(ui.find("st.selectbox('Harita göstergesi',options"),
                        ui.find("st.selectbox('Analiz edilecek sektör'"))
        self.assertLess(ui.find("st.selectbox('Analiz edilecek sektör'"),
                        ui.find("city=il_secimi(sorted(province.İl.tolist())"))
        self.assertEqual(ui.count("st.selectbox('Analiz edilecek sektör'"),1)
        self.assertIn('#f04e66',app)
        self.assertIn('#f04e66',light)
        self.assertIn("if topic in ('Doğal afetler', 'Ticari hareketlilik')",app)

if __name__=='__main__':unittest.main()
