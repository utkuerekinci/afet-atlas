"""v3.5: gerçek paketli USGS + sadece test içi sentetik 973 ilçe kapsamı."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

import pandas as pd
from hesaplama import puanlari_hesapla
from afet_atlas_adk.veri_araclari import araclari_olustur
from afet_atlas_adk.bolge_araclari import bolge_araclari_olustur
from afet_atlas_adk.kapsam_araclari import kapsam_araclari_olustur

BASE=Path(__file__).resolve().parent

class YeniDepremAraclari(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=BASE/'indirilen_veriler'
        cls.events=pd.read_csv(d/'usgs_2025_m4_5.csv')
        geo=json.loads((d/'turkiye_81_il.geojson').read_text('utf-8'))
        iller, matches=puanlari_hesapla(cls.events,geo,0)
        cls.tools={f.__name__:f for f in araclari_olustur(iller,cls.events,matches,2025,2025,4.5,0)}
    def test_13_tools(self):
        self.assertEqual(len(self.tools),13)
    def test_country_magnitude(self):
        result=self.tools['deprem_buyukluk_dagilimi']()
        self.assertEqual(result['toplam_kayit'],159)
        self.assertEqual(sum(result['gruplar'].values()),159)
    def test_province_magnitude(self):
        result=self.tools['deprem_buyukluk_dagilimi']('Balıkesir')
        self.assertEqual(result['toplam_kayit'],18)
        self.assertEqual(sum(result['gruplar'].values()),18)
    def test_monthly_and_yearly(self):
        monthly=self.tools['deprem_aylik_dagilim']()
        yearly=self.tools['deprem_yillik_dagilim']()
        self.assertEqual(monthly['toplam'],159)
        self.assertEqual(yearly['yillik_kayitlar'],{'2025':159})
    def test_top_provinces(self):
        result=self.tools['deprem_illerini_sirala']('Deprem sayısı',10,'En yüksek')
        self.assertEqual(result['sonuclar'][0]['il'],'Balıkesir')
        self.assertEqual(len(result['sonuclar']),10)
        self.assertIn('hata',self.tools['deprem_illerini_sirala'](adet=81))
    def test_score_explanation(self):
        result=self.tools['deprem_puani_neden_yuksek']('Balıkesir')
        self.assertEqual(result['toplam_puan'],30)
        self.assertEqual(sum(x['puan_katkisi'] for x in result['kalemler']),30)
    def test_top_events_and_filters(self):
        self.assertEqual(len(self.tools['buyuklugune_gore_en_onemli_depremler'](8)['olaylar']),8)
        self.assertIn('hata',self.tools['deprem_olay_kayitlari']('Ankara',3.0))

class BolgeselAraclar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Gerçek ilçe verisi değil: model ve araç kontratını sınama fixture'ı.
        rows=[{'il':f'Test İl {i%81:02d}','ilce':f'Test İlçe {i:03d}',
               'nufus':1000+i*10,'nufus_yogunlugu_km2':float(100+i%40)} for i in range(973)]
        cls.tools={f.__name__:f for f in bolge_araclari_olustur(pd.DataFrame(rows))}
    def test_thirteen_regional_tools(self):
        self.assertEqual(len(self.tools),13)
    def test_province_population_ranking(self):
        out=self.tools['illeri_nufusa_gore_sirala'](adet=5)
        self.assertEqual(len(out['ilk_iller']),5)
        self.assertGreaterEqual(out['ilk_iller'][0]['nufus'],out['ilk_iller'][1]['nufus'])
    def test_national_district_ranking(self):
        out=self.tools['ilceleri_nufusa_gore_sirala'](adet=10)
        self.assertEqual(out['sonuclar'][0]['ilce'],'Test İlçe 972')
    def test_comparison(self):
        a=self.tools['iki_ili_nufusa_gore_karsilastir']('Test İl 00','Test İl 01')
        self.assertIn('nufus_farki_birinci_eksi_ikinci',a)
        b=self.tools['iki_ilceyi_karsilastir']('Test İl 00','Test İlçe 000','Test İl 01','Test İlçe 001')
        self.assertIn('puan_farki',b)
    def test_explanation(self):
        out=self.tools['yasamda_neden_bu_ilce_birinci'](kapsam='İl içi',il_adi='Test İl 00')
        self.assertIn('gostergeler',out)
        self.assertGreaterEqual(out['fark'],0)
    def test_sector_leaders(self):
        out=self.tools['sektorlerin_birincilerini_karsilastir']()
        self.assertEqual(len(out['liderler']),4)
    def test_missing_sege(self):
        self.assertIn('hata',self.tools['sege_en_gelismis_ilceler']())
        self.assertFalse(self.tools['bolgesel_veri_durumu']()['sege_tam_eslesme'])

class GenelKaynakAraclari(unittest.TestCase):
    def test_data_gaps(self):
        funcs={f.__name__:f for f in kapsam_araclari_olustur(False)}
        self.assertEqual(len(funcs['afet_veri_durumu']()['henuz_sayisal_entegre_edilmeyen_afetler']),2)
        self.assertEqual(len(funcs['afet_veri_durumu']()['rapor_kayitli_afetler']),4)
        self.assertFalse(funcs['asistan_yetenekleri']()['bolgesel_araclar_aktif'])
        self.assertIn('tasarlanan_agirliklar',funcs['sektor_modeli_ve_gostergeler']())

if __name__=='__main__':unittest.main()
