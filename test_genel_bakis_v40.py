"""Tests of v4.0 home page on the shipped, real district+OSM+disaster datasets."""
from pathlib import Path
import unittest

from ilce_veri import fetch_population, read_sege_csv, combine
from veri import il_sinirlarini_getir
from ticaret_veri import zenginlestir_ilceler
from genel_bakis import (
    OVERVIEW_TOPICS, available_layers, city_summary, layer_frame, prepare_provinces,
)

BASE=Path(__file__).resolve().parent


class GeneralOverviewV40Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pop=fetch_population()
        merged,_=combine(pop,read_sege_csv())
        all_districts, status=zenginlestir_ilceler(merged)
        assert status['osm_aktif']
        cls.geo=il_sinirlarini_getir()
        cls.districts,cls.provinces=prepare_provinces(all_districts,cls.geo)

    def test_full_coverage_and_loaded_osm(self):
        self.assertEqual(len(self.districts),973)
        self.assertEqual(len(self.provinces),81)
        self.assertIn('OSM yeme-içme kaydı',self.provinces.columns)
        self.assertEqual(int(self.provinces['İlçe sayısı'].sum()),973)

    def test_all_visible_layers_match_real_province_boundaries(self):
        names={f['properties']['shapeName'] for f in self.geo['features']}
        for topic in OVERVIEW_TOPICS:
            options=available_layers(self.provinces,topic)
            self.assertGreater(len(options),0)
            for name in options:
                with self.subTest(topic=topic,layer=name):
                    tab,col,_=layer_frame(self.provinces,topic,name)
                    self.assertEqual(len(tab),81)
                    self.assertEqual(set(tab['İl']),names)
                    self.assertTrue(tab[col].notna().any())

    def test_city_profile_for_each_topic_layer_and_multiple_cities(self):
        cities=['Ankara','İstanbul','İzmir','Artvin','Bayburt']
        for city in cities:
            for topic in OVERVIEW_TOPICS:
                for name in available_layers(self.provinces,topic):
                    with self.subTest(city=city,topic=topic,layer=name):
                        details=city_summary(self.districts,self.provinces,city,topic,name)
                        self.assertEqual(details['il'],city)
                        self.assertGreater(details['nufus'],0)
                        self.assertGreater(details['ilce'],0)
                        self.assertTrue(details['text'])
                        self.assertTrue(details['key_value'])

    def test_no_usgs_fetch_on_home(self):
        code=(BASE/'app.py').read_text(encoding='utf-8')
        overview=code.split("if module=='Genel Bakış':",1)[1].split("elif module=='Yaşam Kalitesi':",1)[0]
        self.assertNotIn('deprem_bul(',overview)
        self.assertNotIn('dis_dashboard(',overview)
        self.assertIn("st.markdown('### Analiz alanları')",overview)
        self.assertIn('katman',overview.lower())

    def test_map_plotter_with_new_home_layers(self):
        from atlas_harita import katman_haritasi
        for topic in OVERVIEW_TOPICS:
            selected=available_layers(self.provinces,topic)[0]
            data,col,label=layer_frame(self.provinces,topic,selected)
            fig=katman_haritasi(self.geo,data,col,label,'Ankara')
            self.assertEqual(len(fig.data),83)

if __name__=='__main__':
    unittest.main()
