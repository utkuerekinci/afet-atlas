"""Gerçek 2025 nüfus ve SEGE-2022 kayıtlarından gerekçe üretimi denetimleri."""
import unittest
from pathlib import Path
import pandas as pd
from atlas_analiz import neden_birinci, sirala_ilceler

ROOT=Path(__file__).resolve().parent

class NarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=pd.read_csv(ROOT/'indirilen_veriler/ilce_nufus_2025_sege_2022_BIRLESIK.csv')

    def test_all_sectors_have_explanations(self):
        for sector in ('Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama'):
            with self.subTest(sector=sector):
                ranked,meta=sirala_ilceler(self.df,'ticaret','İl içi','Ankara',sektor=sector)
                why=neden_birinci(ranked,meta)
                p=why['yorum_paragrafi']
                self.assertIn(why['birinci']['ilce'],p)
                self.assertIn(why['ikinci']['ilce'],p)
                self.assertGreaterEqual(len(p.split('. ')),4)
                self.assertNotIn('nihai yatırım kararı',p)
                self.assertGreaterEqual(p.count('. '),3)
                if sector=='Lojistik / depolama':
                    self.assertIn('depolama',p)

    def test_all_preferences_have_contextual_explanations(self):
        for pref in ('Dengeli','Daha sakin','Daha hareketli'):
            with self.subTest(pref=pref):
                ranked,meta=sirala_ilceler(self.df,'yasam','İl içi','Ankara',tercih=pref)
                why=neden_birinci(ranked,meta)
                p=why['yorum_paragrafi']
                self.assertIn(why['birinci']['ilce'],p)
                self.assertIn('yaşam',p)
                self.assertIn('öneri',p.lower())
                self.assertNotIn('Bu sonuç gerçek yaşam memnuniyetini',p)

    def test_same_score_does_not_claim_winner_is_clearly_superior(self):
        ranked,meta=sirala_ilceler(self.df,'yasam','İl içi','Ankara',tercih='Dengeli')
        why=neden_birinci(ranked,meta)
        if why['fark']==0:
            self.assertIn('yakın bir profil',why['yorum_paragrafi'])

    def test_national_rank_has_province_context(self):
        ranked,meta=sirala_ilceler(self.df,'ticaret','Türkiye geneli','Ankara',sektor='Hizmetler')
        p=neden_birinci(ranked,meta)['yorum_paragrafi']
        self.assertIn('Türkiye genelindeki',p)
        self.assertGreaterEqual(len(p.split('. ')),4)

    def test_one_record_never_invents_runner(self):
        one=self.df.head(1)
        ranked,meta=sirala_ilceler(one,'ticaret','Türkiye geneli','Ankara',sektor='Yeme-içme')
        why=neden_birinci(ranked,meta)
        self.assertIsNone(why['ikinci'])
        self.assertIn(one.iloc[0].ilce,why['yorum_paragrafi'])

if __name__=='__main__':unittest.main()
