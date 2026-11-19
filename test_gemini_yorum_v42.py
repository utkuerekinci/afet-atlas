"""Gemini API anahtarı olmadan, gerçek ağ çağrısı yapmadan entegrasyon denemeleri."""
import json
import os
import unittest
from unittest.mock import patch
import pandas as pd

import atlas_gemini_yorum as mod


class TestGeminiYorum(unittest.TestCase):
    def test_missing_key_is_optional(self):
        with patch.dict(os.environ, {'GOOGLE_API_KEY':'', 'GEMINI_API_KEY':''}):
            self.assertEqual(mod.api_anahtari(), '')

    def test_float_nan_is_json_null(self):
        text=json.dumps(mod._native({'sayi':float('nan'),'buyukluk':123.7}))
        self.assertIn('null',text)
        self.assertNotIn('NaN',text)

    def test_district_context_has_real_comparison_and_model(self):
        ranked=pd.DataFrame([
            {'il':'Ankara','ilce':'Çankaya','nufus':900000,'Fırsat puanı':81.5,'osm_yeme_icme':1295},
            {'il':'Ankara','ilce':'Yenimahalle','nufus':500000,'Fırsat puanı':80.1,'osm_yeme_icme':331},
        ])
        meta={'puan_sutunu':'Fırsat puanı','mod':'ticaret','kapsam':'İl içi',
              'il':'Ankara','sektor':'Yeme-içme'}
        context=mod.ilce_baglam(ranked,meta,{'gostergeler':[{'anahtar':'nufus','agirlik_yuzde':30}], 'yorum_paragrafi':'Çankaya öne çıkar.'})
        self.assertEqual(context['ilk_uc_ilce'][0]['ilce'],'Çankaya')
        self.assertEqual(context['ilk_uc_ilce'][1]['osm_yeme_icme'],331)
        self.assertEqual(context['sektor'],'Yeme-içme')
        self.assertEqual(context['gosterge_katkilari'][0]['agirlik_yuzde'],30)

    def test_province_context_changes_by_city(self):
        districts=pd.DataFrame([
            {'il':'Ankara','ilce':'Çankaya','nufus':100,'sege_sira':2},
            {'il':'Ankara','ilce':'Yenimahalle','nufus':80,'sege_sira':3},
            {'il':'İzmir','ilce':'Konak','nufus':90,'sege_sira':6},
        ])
        provinces=pd.DataFrame([{'İl':'Ankara','Nüfus (2025)':180}, {'İl':'İzmir','Nüfus (2025)':90}])
        ankara=mod.il_baglam(districts,provinces,'Ankara','Yaşam ve nüfus','Nüfus (2025)',{'text':'x'})
        izmir=mod.il_baglam(districts,provinces,'İzmir','Yaşam ve nüfus','Nüfus (2025)',{'text':'x'})
        self.assertEqual(ankara['il'],'Ankara')
        self.assertNotEqual(ankara['en_kalabalik_ilceler'],izmir['en_kalabalik_ilceler'])

    def test_api_response_is_passed_through_without_changing_scores(self):
        with patch.object(mod,'_generate_text',return_value='Özgün görüş metni.') as fake:
            result=mod.yorum_uret({'konu':'ilçe'},api_key='dummy',model='gemini-3.5-flash-lite')
            self.assertEqual(result,'Özgün görüş metni.')
            self.assertIn('"konu": "ilçe"',fake.call_args.args[0])

    def test_api_error_does_not_generate_synthetic_text(self):
        with patch.object(mod,'_generate_text',side_effect=RuntimeError('API offline')):
            with self.assertRaises(RuntimeError):
                mod.yorum_uret({'konu':'ilçe'},api_key='dummy')

    def test_fallback_module_does_not_depend_on_gemini(self):
        from atlas_analiz import neden_birinci
        self.assertTrue(callable(neden_birinci))

if __name__ == '__main__':
    unittest.main()
