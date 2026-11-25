"""Gerçek Streamlit sunucusu olmadan tek yönetici kimlik kontrolünün unit testi."""
from __future__ import annotations
import importlib
import sys
import types
import unittest
from unittest.mock import patch
from argon2 import PasswordHasher


class GirisTestleri(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password='FarkliGucluTestParolasi!2026'
        cls.digest=PasswordHasher(time_cost=2,memory_cost=19456,parallelism=1).hash(cls.password)

    def setUp(self):
        self.fake=types.ModuleType('streamlit')
        self.fake.session_state={}
        self.fake.secrets={'AFET_ATLAS_ADMIN_KULLANICI':'test-yonetici',
                           'AFET_ATLAS_ADMIN_SIFRE_OZETI':self.digest}
        self.patcher=patch.dict(sys.modules,{'streamlit':self.fake})
        self.patcher.start()
        sys.modules.pop('atlas_yonetim_ui',None)
        self.mod=importlib.import_module('atlas_yonetim_ui')

    def tearDown(self):
        self.patcher.stop()
        sys.modules.pop('atlas_yonetim_ui',None)

    def test_dogru_kullanici_ve_parola_giris_yapar(self):
        self.assertTrue(self.mod._login_attempt('test-yonetici',self.password))
        self.assertTrue(self.mod.logged_in())
        self.assertGreater(self.fake.session_state['_atlas_admin_until'],0)

    def test_yanlis_kullanici_veya_sifre_giremez(self):
        self.assertFalse(self.mod._login_attempt('baskasi',self.password))
        self.assertFalse(self.mod._login_attempt('test-yonetici','YanlisSifre'))
        self.assertFalse(self.mod.logged_in())

    def test_bes_yanlis_denemede_oturum_gecici_kilitlenir(self):
        for _ in range(5):
            self.assertFalse(self.mod._login_attempt('test-yonetici','Hatalı!'))
        self.assertFalse(self.mod._login_attempt('test-yonetici',self.password))
        self.assertFalse(self.mod.logged_in())

    def test_suresi_dolmus_oturum_gecersiz(self):
        self.mod._login_attempt('test-yonetici',self.password)
        self.fake.session_state['_atlas_admin_until']=1
        self.assertFalse(self.mod.logged_in())


if __name__=='__main__':unittest.main()
