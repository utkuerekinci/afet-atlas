"""Yüklü gerçek OSM özetinin gerileme ve puanlama doğrulaması."""
import unittest
import pandas as pd
from ilce_veri import POP_LOCAL,SEGE_LOCAL,read_population_bytes,read_sege_csv,combine
from ticaret_veri import osm_oku,zenginlestir_ilceler,OSM_SUTUNLAR
from atlas_analiz import sirala_ilceler,neden_birinci

class IntegratedOSMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population=read_population_bytes(POP_LOCAL.read_bytes())
        cls.base,_=combine(cls.population,read_sege_csv())
        cls.rows,cls.status=zenginlestir_ilceler(cls.base)

    def test_full_coverage_and_record_integrity(self):
        self.assertEqual(len(self.rows),973)
        self.assertEqual(self.rows.il.nunique(),81)
        self.assertTrue(self.status['osm_aktif'],self.status['osm'])
        self.assertTrue(self.rows[OSM_SUTUNLAR].notna().all().all())
        self.assertTrue((self.rows[OSM_SUTUNLAR]>=0).all().all())
        self.assertEqual(int(self.rows[OSM_SUTUNLAR].sum().sum()),236011)

    def test_ui_and_agent_rankings_real_data(self):
        for sector in ['Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama']:
            for scope in ['Türkiye geneli','İl içi']:
                ranked,meta=sirala_ilceler(self.rows,'ticaret',scope,'Ankara',sector)
                self.assertEqual(len(ranked),973 if scope=='Türkiye geneli' else 25)
                self.assertTrue(ranked['Fırsat puanı'].between(0,100).all())
                self.assertGreaterEqual(len(neden_birinci(ranked,meta)['yorum_paragrafi'].split('. ')),4)

    def test_sparse_logistics_does_not_turn_missing_tags_into_low_competition(self):
        ranked,meta=sirala_ilceler(self.rows,'ticaret','Türkiye geneli','Ankara','Lojistik / depolama')
        self.assertFalse(meta['osm_aktif'])
        self.assertNotIn('rekabet_baskisi',meta['agirliklar'])
        self.assertIn('osm_lojistik',ranked.columns)
        self.assertIn('depo',neden_birinci(ranked,meta)['yorum_paragrafi'].lower())

if __name__=='__main__':unittest.main()
