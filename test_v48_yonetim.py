"""v4.8 temel veri doğrulama, GitHub API ve özel repo senkronizasyon testleri.

Gerçek GitHub tokenı / internet gerekmez. Çalıştır: python -m unittest test_v48_yonetim -v
"""
from __future__ import annotations

import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from atlas_yonetim_depo import (DATASETS, BUNDLED, DataRepositoryError,
    GitHubDataRepository, Settings, initialize_remote_data, runtime_version,
    validate_upload, _RUNTIME)


class VeriDogrulamaTestleri(unittest.TestCase):
    def test_paketli_veriler_gecerli(self):
        for name in DATASETS:
            path=BUNDLED/name
            if path.exists():
                with self.subTest(name=name):
                    result=validate_upload(name,path.read_bytes())
                    self.assertGreater(result['satir'],0)

    def test_uydurma_sutun_ve_rastgele_dosya_reddedilir(self):
        with self.assertRaises(ValueError):
            validate_upload('rasgele.csv',b'il,ilce\nAnkara,Cankaya')
        with self.assertRaises(ValueError):
            validate_upload('ilce_nufus_2025.csv',b'il,ilce\nAnkara,Cankaya')

    def test_uydurma_nufus_reddedilir(self):
        src=(BUNDLED/'ilce_nufus_2025.csv').read_bytes()
        altered=src.replace(b'782204',b'782205',1)
        self.assertNotEqual(src,altered)
        with self.assertRaises(ValueError):
            validate_upload('ilce_nufus_2025.csv',altered)

    def test_kira_sablonu_gecersiz_kalir(self):
        with self.assertRaises(ValueError):
            validate_upload('ticaret_kira_ilce.csv',b'il,ilce,kira_m2_tl\nAnkara,Cankaya,0')

    def test_reponun_acik_olmasi_reddedilir(self):
        settings=Settings('utkuerekinci/afet-atlas-veri','FAKE')
        client=GitHubDataRepository(settings)
        with patch.object(client,'_request',return_value={'full_name':settings.repo,'private':False}):
            with self.assertRaises(DataRepositoryError):
                client.check_access()

    def test_github_put_yalnizca_veri_klasorune(self):
        settings=Settings('utkuerekinci/afet-atlas-veri','FAKE')
        client=GitHubDataRepository(settings)
        src=(BUNDLED/'ilce_sege_2022.csv').read_bytes()
        captured=[]
        def fake_request(method,path,**kwargs):
            captured.append((method,path,kwargs))
            if method=='GET':
                # Yeni dosyada 404; yalnızca bu testte REST hata metnini simüle et.
                raise DataRepositoryError('Özel veri deposu / dosya bulunamadı. Depo adını ve izinlerini kontrol et.')
            return {'commit':{'sha':'abc123'}}
        with patch.object(client,'_request',side_effect=fake_request):
            sha=client.put('ilce_sege_2022.csv',src,'Test güncellemesi')
        self.assertEqual(sha,'abc123')
        self.assertEqual(captured[-1][0],'PUT')
        self.assertEqual(captured[-1][1],'/contents/indirilen_veriler/ilce_sege_2022.csv')
        self.assertEqual(base64.b64decode(captured[-1][2]['json']['content']),src)
        self.assertNotIn('afet-atlas/contents',captured[-1][1])

    def test_private_depo_snapshot_ozel_repo_okuma(self):
        name='ticaret_osm_ilce.csv'
        raw=(BUNDLED/name).read_bytes()
        sha='sha-test-'+sha256(raw).hexdigest()[:6]
        class Fake:
            def __init__(self,settings):pass
            def check_access(self):return True
            def index(self):return {name:sha}
            def disabled(self):return []
            def get(self,filename):
                if filename!=name:raise AssertionError(filename)
                return raw,sha
        old_env=os.environ.get('AFET_ATLAS_DATA_DIR')
        try:
            # Global version anahtarını resetleyip sadece fake repository ile çalıştır.
            with patch('atlas_yonetim_depo.GitHubDataRepository',Fake):
                settings=Settings('utkuerekinci/mock-test-repo','FAKE',branch='main')
                changed=initialize_remote_data(settings,force=True)
                self.assertTrue(changed)
                self.assertTrue(runtime_version())
                self.assertEqual((Path(os.environ['AFET_ATLAS_DATA_DIR'])/name).read_bytes(),raw)
                self.assertEqual((BUNDLED/name).read_bytes(),raw)
                # Aynı sürüm tekrar geldiğinde yeniden yükleme yapılmaz.
                self.assertFalse(initialize_remote_data(settings,force=True))
        finally:
            if old_env is None:os.environ.pop('AFET_ATLAS_DATA_DIR',None)
            else:os.environ['AFET_ATLAS_DATA_DIR']=old_env


if __name__=='__main__':
    unittest.main()
