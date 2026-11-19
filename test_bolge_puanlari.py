import unittest
import pandas as pd
from bolge_puanlari import ticari_on_endeks,yasam_tercih_endeksi

class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({'ilce':['A','B','C'],'nufus':[100,200,400],
            'nufus_yogunlugu_km2':[800,400,100], 'sege_sira':[90,40,20]})
    def test_all_sectors(self):
        for sector in ['Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama']:
            got,meta=ticari_on_endeks(self.df,sector)
            self.assertEqual(len(got),3)
            self.assertTrue(got['Fırsat puanı'].between(0,100).all())
            self.assertAlmostEqual(sum(meta['agirliklar'].values()),1.0)
    def test_missing_is_not_zero(self):
        simple=self.df[['ilce','nufus']]
        result,meta=ticari_on_endeks(simple,'Yeme-içme')
        self.assertEqual(meta['agirliklar'], {'nufus':1.0})
        self.assertEqual(result.iloc[0].ilce,'C')
    def test_preference(self):
        active=yasam_tercih_endeksi(self.df,'Daha hareketli')
        calm=yasam_tercih_endeksi(self.df,'Daha sakin')
        self.assertEqual(len(active),len(calm))
        self.assertTrue(active['Tercih uyumu'].between(0,100).all())
        self.assertTrue(calm['Tercih uyumu'].between(0,100).all())

if __name__=='__main__':unittest.main()
