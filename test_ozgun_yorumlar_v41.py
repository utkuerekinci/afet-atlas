"""Gerçek 81 il / 973 ilçe veri tabanında bağlamsal yorumların denetimi."""
from __future__ import annotations
import unittest
from ilce_veri import fetch_population, read_sege_csv, combine
from ticaret_veri import zenginlestir_ilceler
from atlas_analiz import sirala_ilceler, neden_birinci
from genel_bakis import prepare_provinces, city_summary, available_layers, OVERVIEW_TOPICS
from veri import il_sinirlarini_getir
from atlas_afet_veri import fire
from atlas_il_yorumlari import yangin_il_yorumu, yangin_lider_yorumu


class ContextualNarrativesV41(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        merged,_=combine(fetch_population(),read_sege_csv())
        cls.data,cls.status=zenginlestir_ilceler(merged)
        cls.districts,cls.provinces=prepare_provinces(cls.data,il_sinirlarini_getir())
        cls.cities=sorted(cls.districts.il.unique())

    def test_leaders_every_city_every_sector_and_preference(self):
        all_cases=0
        for mode,choices in (
            ('ticaret',['Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama']),
            ('yasam',['Dengeli','Daha sakin','Daha hareketli']),
        ):
            for choice in choices:
                outputs=[]
                for city in self.cities:
                    ranked,meta=sirala_ilceler(self.districts,mode,'İl içi',city,
                        sektor=choice if mode=='ticaret' else 'Yeme-içme',
                        tercih=choice if mode=='yasam' else 'Dengeli')
                    report=neden_birinci(ranked,meta)
                    body=report['yorum_paragrafi']
                    self.assertIn(str(ranked.iloc[0].ilce),body)
                    self.assertIn(str(ranked.iloc[1].ilce),body)
                    self.assertGreater(len(body),400)
                    self.assertEqual(body,neden_birinci(ranked,meta)['yorum_paragrafi'])
                    outputs.append(body)
                    all_cases+=1
                self.assertEqual(len(set(outputs)),81)
        self.assertEqual(all_cases,567)

    def test_81_cities_all_overview_layer_profiles(self):
        for topic in OVERVIEW_TOPICS:
            for label in available_layers(self.provinces,topic):
                outputs=[]
                for city in self.cities:
                    report=city_summary(self.districts,self.provinces,city,topic,label)
                    self.assertIn(city,report['text'])
                    self.assertTrue(report['key_value'])
                    outputs.append(report['text'])
                self.assertEqual(len(set(outputs)),81)

    def test_fire_top_is_metric_specific_and_temporal(self):
        a,b=fire(2024),fire(2025)
        for col in ['Yangın sayısı','Yanan alan (ha)']:
            top=b.dropna(subset=[col]).sort_values(col,ascending=False).reset_index(drop=True)
            body=yangin_lider_yorumu(top,2025,col,a)
            self.assertIn(str(top.iloc[0]['İl']),body)
            self.assertIn(str(top.iloc[1]['İl']),body)
        fire_cases=[yangin_il_yorumu(city,2025,'Yangın sayısı',b,a) for city in self.cities]
        self.assertEqual(len(set(fire_cases)),81)

    def test_score_and_order_unchanged_when_text_is_generated(self):
        for mode,choice in [('ticaret','Yeme-içme'),('yasam','Dengeli')]:
            rank,meta=sirala_ilceler(self.districts,mode,'İl içi','Ankara',
                sektor=choice if mode=='ticaret' else 'Yeme-içme',
                tercih=choice if mode=='yasam' else 'Dengeli')
            before=rank[meta['puan_sutunu']].copy()
            report=neden_birinci(rank,meta)
            self.assertEqual(report['birinci']['ilce'],rank.iloc[0].ilce)
            self.assertTrue(before.equals(rank[meta['puan_sutunu']]))

    def test_no_external_model_api_in_commentary_engine(self):
        from pathlib import Path
        root=Path(__file__).resolve().parent
        for name in ('atlas_yorum_motoru.py','atlas_il_yorumlari.py'):
            code=(root/name).read_text()
            for part in ('google.generativeai','google.genai','requests.post(','gemini.generate_content'):
                self.assertNotIn(part,code)

if __name__=='__main__':unittest.main()
