"""OSM ve kira kalite testleri. Sentetik sayılar yalnızca bu TEST dosyasında kullanılır."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from shapely.geometry import box
from atlas_analiz import sirala_ilceler, neden_birinci
from bolge_puanlari import ticari_on_endeks
from ticaret_osm_hazirla import classify,aggregate_points
from ticaret_veri import OSM_SUTUNLAR,osm_oku,zenginlestir_ilceler,canonical_key

ROOT=Path(__file__).resolve().parent

class TicaretOSMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real=pd.read_csv(ROOT/'indirilen_veriler/ilce_nufus_2025_sege_2022_BIRLESIK.csv')

    def test_osm_category_and_geometry(self):
        self.assertIn('osm_yeme_icme',classify({'amenity':'restaurant'}))
        self.assertIn('osm_market_perakende',classify({'shop':'supermarket'}))
        self.assertIn('osm_ulasim',classify({'highway':'bus_stop'}))
        self.assertNotIn('osm_yeme_icme',classify({'disused:amenity':'restaurant','amenity':'restaurant'}))
        polys=[box(0,0,1,1),box(1,0,2,1)]
        got=aggregate_points([(0.5,0.5,{'amenity':'restaurant'},'n1'),
                             (0.5,1.5,{'highway':'bus_stop'},'n2'),
                             (0.5,0.5,{'amenity':'restaurant'},'n1')],polys,['A','B'])
        self.assertEqual(got['A']['osm_yeme_icme'],1)
        self.assertEqual(got['B']['osm_ulasim'],1)

    def test_manifest_missing_does_not_produce_fake_businesses(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('ticaret_veri.OSM_CSV',Path(d)/'notfound.csv'),patch('ticaret_veri.OSM_META',Path(d)/'notfound.json'),patch('ticaret_veri.KIRA_CSV',Path(d)/'notfoundrent.csv'):
                out,status=zenginlestir_ilceler(self.real)
                self.assertFalse(status['osm_aktif'])
                self.assertNotIn('osm_yeme_icme',out.columns)

    def test_full_973_rows_required_for_osm(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.real.head(972)[['il','ilce']].copy()
            for c in OSM_SUTUNLAR:data[c]=0
            path=Path(d)/'osm.csv'; meta=Path(d)/'manifest.json'
            data.to_csv(path,index=False)
            meta.write_text(json.dumps({'kaynak':'OpenStreetMap / Geofabrik','olcek':'Türkiye 973 ilçe','olusturma_tarihi':'2026-11-19'}))
            with patch('ticaret_veri.OSM_CSV',path),patch('ticaret_veri.OSM_META',meta):
                values,status=osm_oku(self.real)
                self.assertIsNone(values)
                self.assertIn('973',status)

    def test_real_dataset_973_matching_aliases(self):
        self.assertEqual(len({canonical_key(il,ilce) for il,ilce in zip(self.real.il,self.real.ilce_nufus_kaynagi)}),973)
        self.assertEqual(canonical_key('Amasya','Amasya'),canonical_key('Amasya','Amasya Merkez'))

    def test_osm_metrics_available_only_when_complete(self):
        sample=self.real[self.real.il=='Ankara'].copy()
        sample['osm_yeme_icme']=range(len(sample))
        sample['osm_ulasim']=range(3,3+len(sample))
        ranked,meta=sirala_ilceler(sample,'ticaret','İl içi','Ankara','Yeme-içme')
        self.assertTrue(meta['osm_aktif'])
        self.assertIn('isletme_kumesi',meta['agirliklar'])
        self.assertIn('rekabet_baskisi',meta['agirliklar'])
        self.assertIn('ulasim',meta['agirliklar'])
        self.assertIn('kafe',neden_birinci(ranked,meta)['yorum_paragrafi'])
        self.assertNotIn('kira',meta['agirliklar'])
        for _,row in ranked.iterrows():
            total=sum(row['Katkı: '+key] for key in meta['agirliklar'])
            self.assertAlmostEqual(total,row['Fırsat puanı'],delta=.16)

    def test_partial_rent_is_not_scored(self):
        sample=self.real[self.real.il=='Ankara'].copy()
        sample['kira_m2_tl']=500.0
        sample['kira_ulusal_tam']=False
        _,meta=ticari_on_endeks(sample,'Yeme-içme')
        self.assertNotIn('kira',meta['agirliklar'])
        sample['kira_ulusal_tam']=True
        _,meta=ticari_on_endeks(sample,'Yeme-içme')
        self.assertIn('kira',meta['agirliklar'])

if __name__=='__main__':unittest.main()
