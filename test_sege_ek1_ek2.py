"""SEGE Ek-1 / Ek-2 testleri. Projenin kökünde çalıştır: python -m unittest test_sege_ek1_ek2 -v"""
import hashlib
from pathlib import Path
from unittest import TestCase, skipUnless
from unittest.mock import patch
import unittest
import pandas as pd
from hazirla_ilce_verileri import parse_sege_pdf, RANK_LIMITS, GRADE_COUNTS
from ilce_veri import read_sege_csv, DATA_DIR

CSV = DATA_DIR / "ilce_sege_2022.csv"
PDF = DATA_DIR / "ham_kaynaklar" / "ilce_sege_2022_kaynak.pdf"
PDF_HASH = "5c99314d7a10558f9f607f1fe4c4135148b887a232e79984b4540a213d9ede8f"

class SEGEGercekPdfTest(TestCase):
    def test_package_csv_973_and_81(self):
        data = pd.read_csv(CSV, encoding="utf-8-sig")
        self.assertEqual(len(data), 973)
        self.assertEqual(data.il.nunique(), 81)
        self.assertEqual(data.sege_sira.tolist(), list(range(1,974)))
        self.assertEqual(read_sege_csv(CSV).anahtar.nunique(), 973)
        self.assertEqual(data.sege_kademe.value_counts().sort_index().tolist(), list(GRADE_COUNTS))

    def test_kadikoy_gudul_distinct(self):
        data = pd.read_csv(CSV, encoding="utf-8-sig").set_index('sege_sira')
        self.assertEqual(data.loc[4, 'ilce'], 'Kadıköy')
        self.assertEqual(data.loc[630, 'ilce'], 'Güdül')
        self.assertEqual(data.loc[630, 'il'], 'Ankara')
        self.assertEqual(data.loc[5, 'ilce'], 'Yenimahalle')

    def test_artvin_and_hakkari(self):
        data = pd.read_csv(CSV, encoding='utf-8-sig')
        self.assertEqual(int((data.il=='Artvin').sum()),9)
        self.assertEqual(int(data.il.str.lower().str.startswith('hakk').sum()),5)

    @skipUnless(PDF.exists(), 'Ham resmî PDF mevcutsa çapraz kontrol çalışır')
    def test_official_pdf_duplicate_tables_agree(self):
        raw=PDF.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PDF_HASH)
        data=pd.read_csv(CSV,encoding='utf-8-sig')
        parsed,audit=parse_sege_pdf(raw,data.il.unique().tolist(),return_audit=True)
        pd.testing.assert_frame_equal(data,parsed,check_dtype=False)
        self.assertEqual(len(audit),973)
        self.assertTrue((audit.pdf_ek1_sayfa>=42).all())
        self.assertTrue((audit.pdf_ek2_sayfa>=49).all())

    @skipUnless(PDF.exists(), 'Ham resmî PDF mevcutsa çelişki koruması çalışır')
    def test_detect_conflict_between_tables(self):
        from hazirla_ilce_verileri import _read_ek2
        real_ek2=_read_ek2
        def broken(doc, start, provinces):
            rows=real_ek2(doc,start,provinces)
            v=list(rows[4]);v[2]=1.000;rows[4]=tuple(v)
            return rows
        data=pd.read_csv(CSV,encoding='utf-8-sig')
        with patch('hazirla_ilce_verileri._read_ek2', side_effect=broken):
            with self.assertRaisesRegex(ValueError,'çelişkili sıra 4'):
                parse_sege_pdf(PDF.read_bytes(),data.il.unique().tolist())

if __name__=='__main__':unittest.main()
