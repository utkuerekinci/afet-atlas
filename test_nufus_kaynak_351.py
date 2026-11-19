"""Yalnızca YAPAY test fixture'ları, üretim verisi değildir."""
import json
import unittest
from ilce_veri import read_topografya_population_bytes, OFFICIAL_TR_POP_2025


def fake_payload():
    provinces=[]
    for i in range(81):
        count = 13 if i == 0 else 12
        rows=[]
        for j in range(count):
            rows.append({'ad':f'İlçe {j+1}', 'n':[1,1], 'alan_km2':10})
        provinces.append({'ad':f'İl {i+1}', 'ilceler':rows, 'nufus':[count,count]})
    # Unit test only: synthetic total has a single balancing row; never actual population.
    additional=OFFICIAL_TR_POP_2025-973
    provinces[0]['ilceler'][0]['n']=[1, 1+additional]
    provinces[0]['nufus']=[13,13+additional]
    return {'kaynak': {'kurum':'Türkiye İstatistik Kurumu (TÜİK)'},
            'yillar':[2024,2025], 'ilce_yillari':[2024,2025],
            'tr':{'nufus':[100,OFFICIAL_TR_POP_2025]}, 'iller':provinces}

class TopoPopulationTest(unittest.TestCase):
    def test_success(self):
        data=fake_payload()
        frame=read_topografya_population_bytes(json.dumps(data,ensure_ascii=False).encode())
        self.assertEqual(len(frame),973)
        self.assertEqual(frame.il.nunique(),81)
        self.assertEqual(int(frame.nufus.sum()),OFFICIAL_TR_POP_2025)
        self.assertEqual(len(set(frame.anahtar)),973)

    def test_bad_province_subtotal_rejected(self):
        data=fake_payload()
        data['iller'][9]['ilceler'][0]['n'][1] += 10
        with self.assertRaisesRegex(ValueError,'ilçeler toplamı'):
            read_topografya_population_bytes(json.dumps(data,ensure_ascii=False).encode())

    def test_bad_national_total_rejected(self):
        data=fake_payload()
        data['tr']['nufus'][-1] -= 11
        with self.assertRaisesRegex(ValueError,'resmî toplamla uyuşmuyor'):
            read_topografya_population_bytes(json.dumps(data,ensure_ascii=False).encode())

    def test_wrong_district_year_rejected(self):
        data=fake_payload()
        data['ilce_yillari']=[2023,2024]
        with self.assertRaisesRegex(ValueError,'2024 ve 2025 değil'):
            read_topografya_population_bytes(json.dumps(data,ensure_ascii=False).encode())

    def test_no_fake_names(self):
        data=fake_payload()
        data['iller'][5]['ilceler'][3]['ad']=data['iller'][5]['ilceler'][2]['ad']
        with self.assertRaisesRegex(ValueError,'tekrar'):
            read_topografya_population_bytes(json.dumps(data,ensure_ascii=False).encode())

if __name__ == '__main__':unittest.main()
