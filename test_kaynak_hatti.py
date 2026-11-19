"""Dış kaynaklar olmadan dosya-kaynak hattının doğrulama testleri."""
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
import zipfile
import xml.etree.ElementTree as ET

from kaynaklari_topla import get_fire_url, download
from xlsx_ham_csv import extract_all, index_col

class KaynakTest(unittest.TestCase):
    def test_ogm_html_ref(self):
        class Resp:
            text='<a href="https://cdniys.tarimorman.gov.tr/static/y2025.xlsx">14 İllere göre orman yangınlarının dağılımı, 2025.xlsx</a>'
            def raise_for_status(self):pass
        with patch('kaynaklari_topla.requests.get',return_value=Resp()):
            self.assertEqual(get_fire_url(2025),'https://cdniys.tarimorman.gov.tr/static/y2025.xlsx')
    def test_reject_unknown_host(self):
        class Resp:
            text='<a href="https://bad.invalid/wildfire.xlsx">14 İllere göre orman yangınlarının dağılımı,2024.xlsx</a>'
            def raise_for_status(self):pass
        with patch('kaynaklari_topla.requests.get',return_value=Resp()):
            with self.assertRaises(ValueError):get_fire_url(2024)
    def test_reject_html_as_xlsx(self):
        class Resp:
            content=b'<html><title>Blocked</title></html>'
            url='https://example.org/file.xlsx'
            def raise_for_status(self):pass
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.xlsx'
            with patch('kaynaklari_topla.requests.get',return_value=Resp()):
                with self.assertRaises(ValueError):download('https://example.org/file.xlsx',path,'xlsx')
            self.assertFalse(path.exists())
    def test_xlsx_raw_cells(self):
        ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            xlsx=base/'test.xlsx'
            book=f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets><sheet name="Veri" sheetId="1" r:id="rId1"/></sheets></workbook>'
            rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" /></Relationships>'
            sheet=f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>İl</t></is></c><c r="C1"><v>9</v></c></row><row r="3"><c r="B3" t="inlineStr"><is><t>Ankara</t></is></c></row></sheetData></worksheet>'
            with zipfile.ZipFile(xlsx,'w') as z:
                z.writestr('xl/workbook.xml',book)
                z.writestr('xl/_rels/workbook.xml.rels',rels)
                z.writestr('xl/worksheets/sheet1.xml',sheet)
            files=extract_all(xlsx,base/'csv')
            self.assertEqual(len(files),1)
            lines=files[0].read_text(encoding='utf-8-sig').splitlines()
            self.assertEqual(lines[0],'İl,,9')
            self.assertEqual(lines[1],'')
            self.assertEqual(lines[2],',Ankara')
            self.assertEqual(index_col('AA8'),26)

if __name__=='__main__':unittest.main()
