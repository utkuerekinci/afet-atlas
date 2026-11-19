import io
import unittest
import pandas as pd
from ilce_veri import read_population_bytes, combine, normalize_name
from hazirla_ilce_verileri import RANK_LIMITS

class IlceTests(unittest.TestCase):
    def test_name_norm(self):
        self.assertEqual(normalize_name('İZMİR'), normalize_name('Izmir'))
        self.assertEqual(normalize_name('Şişli'), normalize_name('Sisli'))
    def test_reject_unsupported_population(self):
        # Unit test only: synthetic 2-row fixture must not appear as real nationwide data.
        dummy=b'il,ilce,nufus\nAnkara,Cankaya,10\nIzmir,Konak,20\n'
        with self.assertRaisesRegex(ValueError,'973'):
            read_population_bytes(dummy)
    def test_no_fabricated_sege(self):
        pop=pd.DataFrame([{'il':'Ankara','ilce':'Çankaya','anahtar':'ankara:cankaya','nufus':10,'nufus_yogunlugu_km2':1.0}])
        df,status=combine(pop)
        self.assertNotIn('sege_sira',df.columns)
        self.assertIn('Henüz',status['sege'])
    def test_grade_totals(self):
        arr=[RANK_LIMITS[0]]+[RANK_LIMITS[i]-RANK_LIMITS[i-1] for i in range(1,6)]
        self.assertEqual(arr,[67,173,175,215,222,121])

if __name__=='__main__': unittest.main()
