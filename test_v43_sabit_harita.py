"""v4.3 harita testi: gerçek il geometrileri, kilitli Leaflet ve il seçimi."""
import unittest
import pandas as pd
from atlas_sabit_harita import _hafif_il_geometrileri, hazirla_harita, il_olayi


class SabitHaritaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feats = _hafif_il_geometrileri()
        cls.cities = [f['properties']['il'] for f in cls.feats]
        cls.df = pd.DataFrame({'İl':cls.cities,'Nüfus':range(len(cls.cities))})

    def test_all_81_full_polygons_and_selection_by_tooltip(self):
        self.assertEqual(len(self.feats),81)
        self.assertEqual(len(set(self.cities)),81)
        self.assertEqual(il_olayi({'last_object_clicked_tooltip':'Ankara'}),'Ankara')
        self.assertEqual(il_olayi({'last_object_clicked_tooltip':'Uydurma İl'}),None)

    def test_latlon_selection_fallback(self):
        self.assertEqual(il_olayi({'last_object_clicked':{'lat':39.93,'lng':32.86}}),'Ankara')
        self.assertIsNone(il_olayi(None))

    def test_fixed_map_and_clickable_geojson(self):
        m=hazirla_harita(self.df,'Nüfus','Nüfus','Ankara')
        html=m.get_root().render()
        self.assertIn('"dragging": false',html)
        self.assertIn('"scrollWheelZoom": false',html)
        self.assertIn('"doubleClickZoom": false',html)
        self.assertIn('"touchZoom": false',html)
        self.assertIn('cursor:pointer!important',html)
        self.assertIn('"il": "Ankara"',html)
        self.assertIn('"secili": true',html)

    def test_absent_values_are_not_imputed(self):
        other=self.df.copy(); other['Nüfus']=pd.NA
        m=hazirla_harita(other,'Nüfus','Nüfus','Ankara')
        html=m.get_root().render()
        self.assertIn('"dolgu": "#263243"',html)
        self.assertIn('"deger": "\\u2014"',html)

    def test_unmatched_city_table_rejected(self):
        with self.assertRaises(ValueError):
            hazirla_harita(self.df.iloc[:-1],'Nüfus','Nüfus','Ankara')


if __name__=='__main__':
    unittest.main()
