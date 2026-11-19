"""Gerçek 973 ilçe ve hatalı-eşleşme engeli regresyon testleri."""
import unittest
from pathlib import Path
import pandas as pd
from ilce_veri import POP_LOCAL, SEGE_LOCAL, read_population_bytes, read_sege_csv, combine, eslesme_anahtarlari

class GercekEslesmeTesti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pop = read_population_bytes(POP_LOCAL.read_bytes())
        cls.sege = read_sege_csv(SEGE_LOCAL)
    def test_all_973_match_without_guessing(self):
        combined, status = combine(self.pop, self.sege)
        self.assertEqual(len(combined),973)
        self.assertEqual(combined.sege_sira.nunique(),973)
        self.assertEqual(set(combined.sege_sira.astype(int)),set(range(1,974)))
        self.assertEqual(int(combined.nufus.sum()),86092168)
        self.assertEqual(combined.il.nunique(),81)
        self.assertEqual(combined.eslesme_yontemi.value_counts().to_dict(),{'doğrudan':872,'il öneki çıkarıldı':100,'belgelenmiş eş anlam':1})
        self.assertTrue(all(combined.sege_anahtar.str.split(':').str[0] == combined.il.map(lambda x: __import__('ilce_veri').normalize_name(x))))
    def test_specific_mappings(self):
        joined,_ = combine(self.pop,self.sege)
        for province, raw, target in [('Ankara','Ankara Gölbaşı','Gölbaşı'), ('Adıyaman','Adıyaman Merkez','Merkez'), ('Artvin','Artvin Kemalpaşa','Kemalpaşa'), ('Samsun','19 Mayıs','Ondokuzmayıs')]:
            row=joined[(joined.il==province)&(joined.ilce_nufus_kaynagi==raw)]
            self.assertEqual(len(row),1)
            self.assertEqual(row.iloc[0].ilce,target)
    def test_invalid_alias_does_not_silently_pass(self):
        changed=self.pop.copy()
        idx=changed.index[changed.ilce=='19 Mayıs'][0]
        changed.loc[idx,'ilce']='Tanimsiz ilce'
        with self.assertRaisesRegex(ValueError,'kesin SEGE eşleşmesi'):
            eslesme_anahtarlari(changed,self.sege)
    def test_no_cross_province_mapping(self):
        wrong=self.pop.copy()
        idx=wrong.index[(wrong.il=='Ankara')&(wrong.ilce=='Ankara Gölbaşı')][0]
        wrong.loc[idx,'ilce']='Adıyaman Gölbaşı'
        with self.assertRaisesRegex(ValueError,'kesin SEGE eşleşmesi'):
            eslesme_anahtarlari(wrong,self.sege)

if __name__=='__main__': unittest.main()
