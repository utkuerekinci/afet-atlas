"""Gerçek il geometri/deprem fixture + sentetik ve yalnızca test içi ilçe verisi."""
import json
import unittest
from pathlib import Path

import pandas as pd
from atlas_harita import katman_haritasi, secilen_nokta
from atlas_analiz import sirala_ilceler, neden_birinci

from hesaplama import puanlari_hesapla

DIR=Path(__file__).resolve().parent

class AtlasArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo=json.loads((DIR/'indirilen_veriler/turkiye_81_il.geojson').read_text())
        cls.events=pd.read_csv(DIR/'indirilen_veriler/usgs_2025_m4_5.csv')
        cls.provinces,cls.matches=puanlari_hesapla(cls.events,cls.geo,0)
        cls.fixture=pd.DataFrame({'il':['Ankara','Ankara','İstanbul','İstanbul'],
            'ilce':['Çankaya','Yenimahalle','Kadıköy','Şişli'],
            'nufus':[1000000,400000,600000,300000],
            'nufus_yogunlugu_km2':[1100,600,1500,3000]})

    def test_real_2025_map(self):
        fig=katman_haritasi(self.geo,self.provinces[['İl','Toplam puan']],
                           'Toplam puan','Olay puanı','Ankara')
        self.assertEqual(len(fig.data),83)
        self.assertEqual(len(fig.data[-2].customdata),81)
        self.assertEqual(len(self.matches),33)
        self.assertEqual(int(self.provinces['Toplam puan'].max()),30)

    def test_shared_map_checks_all_81_names(self):
        altered=self.provinces[['İl','Toplam puan']].iloc[:-1]
        with self.assertRaises(ValueError):
            katman_haritasi(self.geo,altered,'Toplam puan','puan')

    def test_selection_decode(self):
        class E:
            selection=type('S',(),{'points':[{'customdata':['Ankara']}]})()
        self.assertEqual(secilen_nokta(E()),'Ankara')
        self.assertIsNone(secilen_nokta(None))

    def test_district_rank_province_and_national(self):
        national,meta=sirala_ilceler(self.fixture,'ticaret','Türkiye geneli','Ankara','Yeme-içme')
        local,_=sirala_ilceler(self.fixture,'ticaret','İl içi','Ankara','Yeme-içme')
        self.assertEqual(len(national),4)
        self.assertEqual(len(local),2)
        self.assertEqual(set(local.il),{'Ankara'})
        why=neden_birinci(national,meta)
        self.assertEqual(len(why['gostergeler']),2)
        for _,r in national.iterrows():
            contribution=sum(r['Katkı: '+x['gosterge']] for x in why['gostergeler'])
            self.assertAlmostEqual(contribution,float(r['Fırsat puanı']),delta=.11)
        self.assertIsNotNone(why['ikinci'])

    def test_live_rank_uses_only_known_measurements(self):
        missing=self.fixture.drop(columns=['nufus_yogunlugu_km2'])
        # Existing data loader always supplies column, so fill explicit NaN in fixture.
        missing['nufus_yogunlugu_km2']=float('nan')
        ranked,meta=sirala_ilceler(missing,'ticaret','Türkiye geneli','Ankara','Hizmetler')
        self.assertEqual(set(meta['agirliklar']),{'nufus'})
        self.assertNotIn('Katkı: Yaklaşık nüfus yoğunluğu',ranked)

    def test_top_rank_has_reason(self):
        ranked,meta=sirala_ilceler(self.fixture,'yasam','İl içi','Ankara',tercih='Dengeli')
        why=neden_birinci(ranked,meta)
        self.assertTrue(why['birinci']['ilce'])
        self.assertIsNotNone(why['ikinci'])
        self.assertGreaterEqual(why['fark'],0)

if __name__=='__main__':unittest.main()
