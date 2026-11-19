"""Resmî XLSX dosyasındaki bütün hücreleri ham CSV'ye çıkarır (standart kütüphane).

Ham sayfa CSV'leri onaylanmış il/afet kayıtları değildir; yıl, il, birim ve
alt toplam ayrıştırması ayrıca yapılmalıdır. Formül varsa kaydedilmiş hücre
sonuçları okunur. Boş hücreler korunur. İsimli sayfalar dosya adıyla kaydedilir.
"""
from __future__ import annotations
import csv
import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p':'http://schemas.openxmlformats.org/package/2006/relationships'}

def index_col(cell_ref:str)->int:
    letters=re.match(r'([A-Z]+)',cell_ref)
    if not letters:raise ValueError(f'Hücre koordinatı hatalı: {cell_ref}')
    n=0
    for ch in letters.group(1):n=n*26+ord(ch)-ord('A')+1
    return n-1

def extract_all(path:Path, destination:Path)->list[Path]:
    destination.mkdir(parents=True,exist_ok=True)
    output=[]
    with ZipFile(path) as z:
        if not {'xl/workbook.xml','xl/_rels/workbook.xml.rels'}.issubset(z.namelist()):
            raise ValueError('XLSX temel sayfa bilgisi yok.')
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared=[''.join(n.text or '' for n in si.findall('.//m:t',NS))
                    for si in strings.findall('m:si',NS)]
        book=ET.fromstring(z.read('xl/workbook.xml'))
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={r.attrib['Id']:r.attrib.get('Target','') for r in rels}
        sheets=book.findall('m:sheets/m:sheet',NS)
        if not sheets:raise ValueError('Çalışma sayfası yok.')
        for idx,sheet in enumerate(sheets,1):
            rid=sheet.attrib.get('{'+NS['r']+'}id')
            target=targets.get(rid,'')
            if target.startswith('/'):member=target.lstrip('/')
            else:member='xl/'+target.replace('\\','/')
            while '/./' in member:member=member.replace('/./','/')
            if member not in z.namelist():raise ValueError(f'Sayfa XML bulunamadı: {member}')
            root=ET.fromstring(z.read(member))
            table=[]
            last_row=0
            for row in root.findall('.//m:sheetData/m:row',NS):
                row_no=int(row.attrib.get('r',last_row+1))
                if row_no<=last_row or row_no>100000:
                    raise ValueError('XLSX satır numarası sıralı değil veya çok büyük.')
                table.extend([[] for _ in range(row_no-last_row-1)])
                last_row=row_no
                contents={}
                for c in row.findall('m:c',NS):
                    col=index_col(c.attrib.get('r','A1'))
                    typ=c.attrib.get('t','')
                    v=c.find('m:v',NS)
                    if typ=='inlineStr':
                        value=''.join(t.text or '' for t in c.findall('.//m:is/m:t',NS))
                    elif v is None:value=''
                    elif typ=='s':
                        k=int(v.text or '-1')
                        value=shared[k] if 0<=k<len(shared) else ''
                    elif typ=='b':value='TRUE' if v.text=='1' else 'FALSE'
                    else:value=v.text or ''
                    contents[col]=value
                if contents:
                    line=['']*(max(contents)+1)
                    for col,val in contents.items():line[col]=val
                else:line=[]
                table.append(line)
            safe_name=re.sub(r'[^a-zA-Z0-9_-]+','_',sheet.attrib.get('name','sheet'))[:35]
            out=destination/f'{path.stem}_sayfa_{idx:02d}_{safe_name}.csv'
            with out.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.writer(f)
                writer.writerows(table)
            output.append(out)
    return output

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('xlsx',type=Path)
    parser.add_argument('--output',type=Path,default=Path('indirilen_veriler/ham_kaynaklar/csv'))
    args=parser.parse_args()
    for p in extract_all(args.xlsx,args.output):print(p)
