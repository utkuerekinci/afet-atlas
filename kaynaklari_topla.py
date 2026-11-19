"""Kaynakları yerel bilgisayarda indirir ve doğrulanabilir ham dosyalar olarak saklar.

Komut: python kaynaklari_topla.py --hepsi
Ham bir XLSX dosyasını '81 il doğrulanmış tablo' olarak otomatik işaretlemez.
Sitedeki ziyaretçi veri yükleme düğmesi değildir.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

BASE=Path(__file__).resolve().parent
RAW=BASE/'indirilen_veriler'/'ham_kaynaklar'
MANIFEST=BASE/'indirilen_veriler'/'kaynak_durumu.json'
FORESTRY_PAGES={2024:'https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2053',
                2025:'https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2364'}
SOURCE_POP='https://raw.githubusercontent.com/topografya/veri/yayin/nufus/gostergeler.json'
SOURCE_SEGE='https://www.sanayi.gov.tr/assets/pdf/birimler/2022-ilce-sege.pdf'
SOURCE_DEMOGRAPHIC='https://raw.githubusercontent.com/topografya/veri/yayin/nufus/gostergeler.json'

class AnchorReader(HTMLParser):
    def __init__(self):
        super().__init__();self.anchors=[];self.href=None;self.buffer=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.href=dict(attrs).get('href');self.buffer=[]
    def handle_data(self,data):
        if self.href is not None:self.buffer.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.href:
            self.anchors.append((self.href,' '.join(''.join(self.buffer).split())))
            self.href=None;self.buffer=[]


def download(url: str, path: Path, file_kind: str) -> dict:
    response=requests.get(url,timeout=(15,90),headers={'User-Agent':'AfetAtlas-BBY261 academic data verification'})
    response.raise_for_status()
    contents=response.content
    if file_kind=='xlsx' and (not contents.startswith(b'PK\x03\x04') or len(contents)<2000):
        raise ValueError('XLSX ZIP imzası veya boyutu geçersiz; dosya saklanmadı.')
    if file_kind=='pdf' and (not contents.startswith(b'%PDF-') or len(contents)<10000):
        raise ValueError('PDF imzası veya boyutu geçersiz; dosya saklanmadı.')
    if file_kind=='json':
        obj=response.json()
        if not isinstance(obj,dict) or not obj:raise ValueError('JSON boş veya beklenmeyen yapıda.')
    if file_kind=='csv' and len(contents)<1000:raise ValueError('CSV boş veya çok kısa.')
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.partial')
    temp.write_bytes(contents)
    temp.replace(path)
    return {'url':response.url,'dosya':str(path.relative_to(BASE)),
            'byte':len(contents),'sha256':hashlib.sha256(contents).hexdigest(),
            'asama':'Ham kaynak indirildi; il bazında veri doğrulaması tamamlanmadı'}


def get_fire_url(year:int)->str:
    base=FORESTRY_PAGES[year]
    response=requests.get(base,timeout=(15,45));response.raise_for_status()
    parser=AnchorReader();parser.feed(response.text)
    matches=[]
    for href,title in parser.anchors:
        t=unicodedata.normalize('NFKD', title.translate(str.maketrans('İIı','iii'))).casefold()
        t=' '.join(''.join(ch for ch in t if not unicodedata.combining(ch)).split())
        if 'illere gore orman yanginlarinin dagilimi' in t and str(year) in t:
            url=urljoin(base,href)
            if urlparse(url).hostname not in {'cdniys.tarimorman.gov.tr','iysadmin.tarimorman.gov.tr'}:
                raise ValueError('Bilinmeyen XLSX sunucusu: '+urlparse(url).hostname)
            matches.append(url)
    if len(matches)!=1:raise ValueError(f'{year} için benzersiz OGM il bazlı yangın tablosu bulunamadı: {len(matches)} sonuç.')
    return matches[0]


def run(pop:bool,sege:bool,fire:bool,demographics:bool):
    log={}
    def attempt(key,fn):
        try:
            result=fn()
            if key == 'sege_2022' and 'donusum_hatasi' in result:
                log[key]={'durum':'eksik_donusum','sonuc':result}
                print('EKSİK',key, result['donusum_hatasi'][:180])
            else:
                log[key]={'durum':'indirildi','sonuc':result}
                print('OK ',key)
        except Exception as e:
            log[key]={'durum':'hata','hata':str(e)[:600]}
            print('HATA',key,str(e)[:180])
    if pop:
        def population():
            # V3.4'teki 973 ilçe ve resmi toplam kontrolleri geçmeyen dosya kaydedilmez.
            from ilce_veri import fetch_population,POP_LOCAL,POP_RAW
            frame=fetch_population(force_refresh=True)
            return {'ilce':len(frame),'il':frame.il.nunique(),'toplam_nufus':int(frame.nufus.sum()),
                    'dosya':str(POP_LOCAL.relative_to(BASE)),'ham_json':str(POP_RAW.relative_to(BASE)),'asama':'81 il ve 973 ilçe, her il için ilçe-il toplamları, Türkiye resmî toplamı kontrol edildi; bağımsız TÜİK satır kontrolü ayrıca gereklidir.'}
        attempt('ilce_nufus_2025',population)
    if sege:
        def sege_pdf():
            pdf_path = RAW / 'ilce_sege_2022_kaynak.pdf'
            if pdf_path.is_file():
                contents = pdf_path.read_bytes()
                if not contents.startswith(b'%PDF-') or len(contents) < 10000:
                    raise ValueError('Yerel SEGE PDF dosyası geçersiz; silin ve yeniden indirin.')
                entry = {'url': SOURCE_SEGE, 'dosya': str(pdf_path.relative_to(BASE)),
                         'byte': len(contents), 'sha256': hashlib.sha256(contents).hexdigest(),
                         'asama':'Önceden indirilen PDF yeniden kullanıldı; sayısal ayrıştırma deneniyor.'}
            else:
                entry=download(SOURCE_SEGE,pdf_path,'pdf')
            try:
                from hazirla_ilce_verileri import parse_sege_pdf
                from ilce_veri import fetch_population, read_sege_csv,combine,SEGE_LOCAL
                popframe=fetch_population()
                frame=parse_sege_pdf(pdf_path.read_bytes(),list(popframe.il.unique()))
                staging=SEGE_LOCAL.with_suffix('.partial.csv')
                frame.to_csv(staging,index=False,encoding='utf-8-sig')
                try:
                    combined,_=combine(popframe,read_sege_csv(staging))
                    if len(combined)!=973:raise ValueError('973 ilçe eşleşmedi')
                    staging.replace(SEGE_LOCAL)
                finally:
                    staging.unlink(missing_ok=True)
                entry['donusum']='973/973 doğrulanmış SEGE CSV üretildi'
                entry['csv']=str(SEGE_LOCAL.relative_to(BASE))
            except Exception as exc:
                entry['donusum_hatasi']=str(exc)[:500]
            return entry
        attempt('sege_2022',sege_pdf)
    def fire_excel(year):
        filepath=RAW/f'ogm_illere_gore_yangin_{year}.xlsx'
        result=download(get_fire_url(year),filepath,'xlsx')
        from xlsx_ham_csv import extract_all
        result['ham_csv_sayfalari']=[str(p.relative_to(BASE)) for p in extract_all(filepath, RAW/'csv')]
        result['donusum']='Çalışma sayfaları ham CSV olarak çıkarıldı; il ve olay sayısı kolonları henüz gözle doğrulanmadı.'
        return result
    if fire:
        for year in (2024,2025):
            attempt(f'ogm_yangin_il_{year}',lambda y=year:fire_excel(y))
    if demographics:
        def get_demography():
            from ilce_veri import POP_RAW, read_topografya_population_bytes
            if POP_RAW.is_file():
                raw=POP_RAW.read_bytes()
                frame=read_topografya_population_bytes(raw)
                return {'url':SOURCE_DEMOGRAPHIC, 'dosya':str(POP_RAW.relative_to(BASE)),
                        'byte':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                        'asama':f'81 il ve {len(frame)} ilçe toplamları doğrulandı; TÜİK satır karşılaştırması ayrıca yapılabilir.'}
            response=requests.get(SOURCE_DEMOGRAPHIC,timeout=(15,90))
            response.raise_for_status()
            raw=response.content
            frame=read_topografya_population_bytes(raw)
            POP_RAW.parent.mkdir(parents=True,exist_ok=True)
            staging=POP_RAW.with_suffix('.json.pending')
            staging.write_bytes(raw);staging.replace(POP_RAW)
            return {'url':response.url,'dosya':str(POP_RAW.relative_to(BASE)),
                    'byte':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                    'asama':f'81 il ve {len(frame)} ilçe toplamları doğrulandı.'}
        attempt('tuik_demografi_ikincil_aktarim',get_demography)
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\\nKaynak durumu:',MANIFEST)
    return log

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--hepsi',action='store_true')
    ap.add_argument('--nufus',action='store_true')
    ap.add_argument('--sege',action='store_true')
    ap.add_argument('--yangin',action='store_true')
    ap.add_argument('--demografi',action='store_true')
    args=ap.parse_args()
    if not any(vars(args).values()):ap.error('En az bir kaynak seçin veya --hepsi kullanın.')
    run(args.hepsi or args.nufus,args.hepsi or args.sege,args.hepsi or args.yangin,args.hepsi or args.demografi)
