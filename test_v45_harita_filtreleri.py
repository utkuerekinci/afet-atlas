"""v4.5: il kayıtları, ülke karşılaştırması ve kullanıcı arayüzü regresyon denetimi."""
from pathlib import Path
import unittest
import pandas as pd
from atlas_deprem_kayitlari import secilen_il_kayitlari, hareketliligi_yuksek_bes_il

ROOT = Path(__file__).parent

class DepremEkraniTests(unittest.TestCase):
    def test_secilen_ile_ait_kayitlar_ve_yeniden_esleme(self):
        rows=pd.DataFrame([
            {'İl':'Ankara','Tarih':'2025-01-01','Büyüklük':4.5,'Yer':'a','İl sınırına uzaklık (km)':0,'Puan':1},
            {'İl':'Kars','Tarih':'2025-04-10','Büyüklük':4.8,'Yer':'x','İl sınırına uzaklık (km)':0,'Puan':1},
            {'İl':'Ankara','Tarih':'2025-05-03','Büyüklük':5.1,'Yer':'b','İl sınırına uzaklık (km)':10,'Puan':3},
        ])
        chosen=secilen_il_kayitlari(rows,'Ankara')
        self.assertEqual(chosen['Yer'].tolist(),['b','a'])
        self.assertEqual(len(secilen_il_kayitlari(rows,'Kars')),1)
        self.assertTrue(secilen_il_kayitlari(rows,'Van').empty)

    def test_ulke_karsilastirmasi_ayri_sekmede(self):
        df=pd.DataFrame({'İl':['A','B','C','D','E','F'],'Toplam puan':[3,7,0,5,2,9],
             'Deprem sayısı':[2,3,0,2,1,4], 'Karşılaştırma endeksi':[20,10,None,40,60,0]})
        leaders=hareketliligi_yuksek_bes_il(df)
        self.assertEqual(leaders['İl'].tolist(),['F','B','D','A','E'])

    def test_app_has_filter_strip_and_native_sidebar_toggle(self):
        source=(ROOT/'app.py').read_text(encoding='utf-8')
        self.assertIn('def deprem_filtreleri()',source)
        self.assertIn("elif module=='Afet Analizi':",source)
        self.assertIn("['İl sıralaması','Hareketliliği en yüksek 5 il']",source)
        self.assertIn('st.markdown(\'#### \'+selected+\' · Deprem kayıtları\')',source)
        self.assertIn('stSidebarCollapsedControl',source)
        self.assertIn('content:"☰"',source)
        self.assertNotIn('🔻 ANALİZLER · Alt bölümleri aç / kapat',source)
        self.assertIn("with st.expander('▾  Analizler'",source)
        self.assertNotIn('chosen_disaster',source)
        self.assertNotIn("'Deprem filtreleri',expanded=module=='Afet Analizi'",source)

if __name__=='__main__': unittest.main()
