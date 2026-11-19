"""Offline quality controls for packaged six non-earthquake layer data."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import pandas as pd
from atlas_afet_veri import AFETLER, fire, get, region_map, report_provinces, MGM_IL, key
from atlas_harita import katman_haritasi
from afet_atlas_adk.diger_afet_araclari import diger_afet_araclari_olustur

GEO=json.loads((Path(__file__).parent/'indirilen_veriler'/'turkiye_81_il.geojson').read_text(encoding='utf-8'))

class GercekKaynakTestleri(unittest.TestCase):
    def test_six_layers_supported(self):
        self.assertEqual(len(AFETLER),6)
        for a in AFETLER:
            d=get(a)
            self.assertEqual(len(d['tablo']),81,a)
            self.assertEqual(d['tablo']['İl'].nunique(),81,a)
            self.assertTrue(set(d['tablo']['İl'])=={x['properties']['shapeName'] for x in GEO['features']})

    def test_fire_two_years_and_national_counts(self):
        expected={2024:(3797,77),2025:(3224,81)}
        for year,(count,complete) in expected.items():
            d=fire(year)
            self.assertEqual(int(d['Yangın sayısı'].sum()),count)
            self.assertEqual(d['Yangın sayısı'].notna().sum(),complete)
            self.assertTrue(d['İl'].is_unique)
        self.assertEqual(int(fire(2024)['Yanan alan (ha)'].isna().sum()),7)
        self.assertAlmostEqual(float(fire(2025)['Yanan alan (ha)'].sum()),81472.6,delta=.1)

    def test_fire_missing_values_stay_missing(self):
        d=fire(2024)
        self.assertGreater(int(d['Yangın sayısı'].isna().sum()),0)
        self.assertFalse(d['Yangın sayısı'].dropna().lt(0).any())

    def test_drought_regional_not_province_spi(self):
        d=get('Kuraklık')['tablo']
        self.assertEqual(len(region_map()),81)
        self.assertEqual(d['Bölge'].nunique(),7)
        self.assertAlmostEqual(float(d.query('İl=="İzmir"')['Bölge yağış sapması (%)'].iloc[0]),-22.4)
        self.assertEqual(d.loc[d['Bölge']=='Karadeniz','Bölge yağış sapması (%)'].nunique(),1)

    def test_mgm_only_evidenced_provinces_non_null(self):
        for a,n in [('Sel / taşkın',8),('Heyelan',10),('Çığ',9),('Fırtına',5)]:
            d=report_provinces(a)
            self.assertEqual(int(d['Rapor vurgusu'].notna().sum()),n)
            self.assertTrue(d.loc[d['Rapor vurgusu'].isna(),'Olay aralığı'].eq('Bilinmiyor').all())
            self.assertTrue(d.loc[d['Rapor vurgusu'].notna(),'Rapor vurgusu'].isin([1,2]).all())
        self.assertEqual(get('Sel / taşkın')['ulusal_toplam'],434)
        self.assertEqual(get('Heyelan')['ulusal_toplam'],42)
        self.assertEqual(get('Çığ')['ulusal_toplam'],17)
        self.assertEqual(get('Fırtına')['ulusal_toplam'],257)

    def test_geographic_map_all_layers(self):
        for a in AFETLER:
            d=get(a,2025 if a=='Orman yangını' else 2024)
            f=katman_haritasi(GEO,d['tablo'][['İl',d['harita_kolonu']]],d['harita_kolonu'],d['birim'],'Ankara')
            self.assertEqual(len(f.data),83,a)
            self.assertEqual(len(f.data[-2].customdata),81,a)

    def test_invalid_year_or_data_rejected(self):
        with self.assertRaises(ValueError):get('Sel / taşkın',2025)
        with self.assertRaises(ValueError):get('Orman yangını',2015)
        with self.assertRaises(ValueError):get('Erozyon')
        self.assertEqual(key('Hakkari'),key('Hakkâri'))

    def test_adk_does_not_invent_province_counts(self):
        t={f.__name__:f for f in diger_afet_araclari_olustur()}
        self.assertEqual(len(t),4)
        self.assertEqual(t['afet_il_detayi']('Orman yangını','Antalya',2025)['degerler']['Yangın sayısı'],200)
        van=t['afet_il_detayi']('Çığ','Van',2024)
        self.assertIn('6–8',van['degerler']['Olay aralığı'])
        unknown=t['afet_il_detayi']('Sel / taşkın','İstanbul',2024)
        self.assertIsNone(unknown['degerler']['Rapor vurgusu'])
        self.assertIsNone(t['afet_ulusal_ozet']('Kuraklık')['ulusal_olay_sayisi'])
        self.assertFalse(t['afet_illeri_sirala']('Sel / taşkın')['kesin_il_siralamasi_mumkun_mu'])
        self.assertIn('hata',t['afet_ulusal_ozet']('Deprem'))
        self.assertIn('hata',t['afet_ulusal_ozet']('Heyelan',2025))

if __name__=='__main__':unittest.main()
