"""v4.11 çevrimdışı regresyon: yedi afet, 81 yüzde etiket, yangın yedeği."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest
import pandas as pd
import atlas_afet_veri as src
from genel_bakis import (AFET_GUVENLIK_AGIRLIKLARI, provincial_safety_scores,
                          afet_guvenlik_bilesenleri, available_layers, layer_frame)
from atlas_sabit_harita import hazirla_harita

ROOT=Path(__file__).resolve().parent

class GuvenlikSkoruTestleri(unittest.TestCase):
    def test_seven_disaster_groups_and_weights(self):
        self.assertEqual(set(AFET_GUVENLIK_AGIRLIKLARI),
            {'deprem','orman_yangini','sel','heyelan','cig','firtina','kuraklik'})
        self.assertAlmostEqual(sum(AFET_GUVENLIK_AGIRLIKLARI.values()),1.0)
        risk=afet_guvenlik_bilesenleri()
        self.assertEqual(risk.shape,(81,8))
        self.assertFalse(risk.isna().any().any())
        score=provincial_safety_scores()
        self.assertEqual(score.shape,(81,2))
        self.assertTrue(score['Güvenlik skoru (%)'].between(0,100).all())
        self.assertEqual(score['İl'].nunique(),81)

    def test_single_home_layer_and_81_visible_labels_both_themes(self):
        self.assertEqual(available_layers(pd.DataFrame(),'Doğal afetler'), ['Güvenlik skoru (%)'])
        data,col,label=layer_frame(pd.DataFrame(),'Doğal afetler','Güvenlik skoru (%)')
        self.assertEqual(len(data),81)
        self.assertEqual(col,label)
        for _ in range(1):
            html=hazirla_harita(data,col,label,'Ankara').get_root().render()
            self.assertEqual(html.count('"atlas-score-label"'),81)
            self.assertIn('cursor:pointer!important',html)
            self.assertIn('"dragging": false',html)
            self.assertIn('"scrollWheelZoom": false',html)
            self.assertIn('atlas-score-chip',html)

    def test_mgm_unknown_is_neutral_not_zero(self):
        from genel_bakis import _rapor_riski
        series=_rapor_riski(['Ankara','İstanbul','Van'], 'Sel / taşkın')
        self.assertEqual(series['İstanbul'],0.5)
        self.assertGreater(series['Van'],series['Ankara'])

    def test_other_disaster_alters_composite_score(self):
        baseline=provincial_safety_scores().set_index('İl').loc['Ankara','Güvenlik skoru (%)']
        with patch.dict(src.MGM_IL['Sel / taşkın'],{'Ankara':('En yüksek sel kaydı',None)}):
            now=provincial_safety_scores().set_index('İl').loc['Ankara','Güvenlik skoru (%)']
        self.assertLess(now,baseline)

    def test_fire_screen_uses_fallback_when_remote_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(src,'DATA',Path(tmp)):
                for year in (2024,2025):
                    record=src.get('Orman yangını',year)
                    self.assertEqual(len(record['tablo']),81)
                    self.assertEqual(int(record['tablo']['Yangın sayısı'].sum()),
                                     {2024:3797,2025:3224}[year])
                self.assertEqual(len(provincial_safety_scores()),81)

    def test_public_messages_and_admin_login_notice_removed(self):
        app=(ROOT/'app.py').read_text(encoding='utf-8')
        admin=(ROOT/'atlas_yonetim_ui.py').read_text(encoding='utf-8')
        self.assertNotIn('OSM kayıtları şu anda kullanılamıyor. Haritada',app)
        self.assertNotIn('OSM dosyalarını Yönetici Paneli’nden',app)
        self.assertNotIn('Bu alanda yalnızca senin tanımladığın kullanıcı adı',admin)
        self.assertIn("if topic in ('Doğal afetler', 'Ticari hareketlilik')",app)

if __name__=='__main__':
    unittest.main()
