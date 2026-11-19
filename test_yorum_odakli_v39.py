"""v3.9 yorum ağırlıklı arayüz ve SEGE entegrasyonu denetimleri."""
import unittest
from pathlib import Path
from ilce_veri import POP_LOCAL,SEGE_LOCAL,read_population_bytes,read_sege_csv,combine
from ticaret_veri import zenginlestir_ilceler
from atlas_analiz import sirala_ilceler,neden_birinci

ROOT=Path(__file__).resolve().parent
BANNED=(
    'nihai yatırım kararı değildir',
    'bu sonuç gerçek yaşam memnuniyetini',
    'osm kayıtlarının eksik olabileceğini unutma',
    'bu sayılar osm\'deki etiketli kayıtları temsil ediyor',
    'gerçek müşteri sayısı, yaya geçişi',
)

class FocusedNarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pop=read_population_bytes(POP_LOCAL.read_bytes())
        base,_=combine(pop,read_sege_csv())
        cls.data,cls.status=zenginlestir_ilceler(base)

    def test_life_has_sege_and_access_in_weights(self):
        ranked,meta=sirala_ilceler(self.data,'yasam','İl içi','Ankara',tercih='Dengeli')
        self.assertEqual(set(meta['agirliklar']),{'yasam_ritmi','sege','ulasim'})
        self.assertAlmostEqual(sum(meta['agirliklar'].values()),1.)
        self.assertTrue(ranked['Tercih uyumu'].between(0,100).all())

    def test_narrative_not_a_warning_block(self):
        for mode,choices in [('ticaret',['Yeme-içme','Hizmetler','Lojistik / depolama']),
                             ('yasam',['Dengeli','Daha hareketli','Daha sakin'])]:
            for choice in choices:
                with self.subTest(mode=mode,choice=choice):
                    ranked,meta=sirala_ilceler(self.data,mode,'İl içi','İzmir',
                                  sektor=choice if mode=='ticaret' else 'Yeme-içme',
                                  tercih=choice if mode=='yasam' else 'Dengeli')
                    narrative=neden_birinci(ranked,meta)['yorum_paragrafi']
                    self.assertGreater(len(narrative),350)
                    self.assertTrue(any(word in narrative.lower() for word in ('öner','değerlendir','öncelik','ön plana','alırdım')))
                    for phrase in BANNED:
                        self.assertNotIn(phrase,narrative.lower())

    def test_sectors_have_distinct_recommendations(self):
        endings=[]
        for sector in ('Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama'):
            ranked,meta=sirala_ilceler(self.data,'ticaret','İl içi','Ankara',sektor=sector)
            endings.append(neden_birinci(ranked,meta)['yorum_paragrafi'].split('.')[-2])
        self.assertEqual(len(set(endings)),4)

    def test_ui_does_not_repeat_rejected_phrases(self):
        ui=(ROOT/'atlas_ui.py').read_text().lower()
        analyses=(ROOT/'atlas_analiz.py').read_text().lower()
        for phrase in BANNED:
            self.assertNotIn(phrase,ui)
            self.assertNotIn(phrase,analyses)

    def test_same_data_is_used_for_reason_and_score(self):
        ranked,meta=sirala_ilceler(self.data,'yasam','Türkiye geneli','Ankara',tercih='Daha hareketli')
        result=neden_birinci(ranked,meta)
        self.assertEqual(result['birinci']['ilce'],str(ranked.iloc[0].ilce))
        self.assertEqual(len(result['gostergeler']),len(meta['agirliklar']))
        self.assertIn(result['ikinci']['ilce'],result['yorum_paragrafi'])

if __name__=='__main__':unittest.main()
