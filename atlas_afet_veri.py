"""Afet Atlas: kaynaklı 2024 MGM rapor özeti ve 2024/25 OGM ikincil il tabloları.

IMPORTANT: MGM raporlarındaki açıkça adı geçen iller kayıt örnekleridir;
listede olmayan il = sıfır olay DEĞİLDİR. Yangın CSV'leri ikincil aktarım,
resmî XLSX satır doğrulaması yapılmadığından 'ön inceleme' niteliğindedir.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import unicodedata
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'indirilen_veriler'
MGM_URL='https://www.mgm.gov.tr/FILES/genel/raporlar/2024%20MetAfet%20Degerlendirme%20Raporu_V1.pdf'
OGM_URL={2024:'https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2053',2025:'https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2364'}
AFETLER=['Orman yangını','Sel / taşkın','Heyelan','Çığ','Fırtına','Kuraklık']
MGM_ULUSAL={
    'Sel / taşkın':{'adet':434,'birim':'şiddetli yağış / sel afeti','kaynak_sayfa':'67–68'},
    'Heyelan':{'adet':42,'birim':'MGM heyelan afeti','kaynak_sayfa':'115–117'},
    'Çığ':{'adet':17,'birim':'MGM çığ afeti','kaynak_sayfa':'99–101'},
    'Fırtına':{'adet':257,'birim':'MGM fırtına afeti','kaynak_sayfa':'79–82'},
}
# Metinde isimleri açıkça geçen iller. Tam kapsamlı il listesi DEĞİL.
# (durum, kanıt ve sayıya dönüştürülmeyen aralık, varsa)
MGM_IL={
 'Sel / taşkın':{
   'Van':('Yılın en çok sel/şiddetli yağış afeti bildirilen ili','20 ve üzeri; harita sınıfı'),
   'Elazığ':('Raporda öne çıkan illerden','12–15; harita sınıfı'),
   **{name:('Raporda sel/şiddetli yağış görüldüğü açıkça belirtiliyor',None) for name in ('Ankara','Konya','Muğla','Antalya','İzmir','Balıkesir')},
 },
 'Heyelan':{
   **{name:('Yılın en çok heyelan raporlanan illerinden', 'Artvin: 6–8; harita sınıfı' if name=='Artvin' else None) for name in ('Artvin','Siirt','Rize')},
   **{name:('İlkbahar heyelanı görüldüğü raporlanmış',None) for name in ('Bitlis','Elazığ','Yozgat','Ankara','Şırnak','Hakkâri','Bursa')},
 },
 'Çığ':{
   'Van':('En yüksek kayıt sınıfında; 2024 çığ haritası','6–8; harita sınıfı'),
   **{name:('2024 çığ haritasında kayıtlı','1–2; harita sınıfı') for name in ('Rize','Artvin','Kars','Erzurum','Bingöl','Batman','Siirt','Şırnak')},
 },
 'Fırtına':{
    'Kayseri':('2024 yılında en çok fırtına afeti görülen illerden','15 ve üzeri; harita sınıfı'),
    **{name:('2024 yılında en çok fırtına afeti görülen illerden',None) for name in ('Antalya','Muğla')},
    **{name:('Fırtına afetinin sık yaşandığı belirtilmiş',None) for name in ('Çorum','Burdur')},
 }
}
# MGM 2024 raporu, Şekil 84'te 7 coğrafi BÖLGE için yıllık yağış anomalisi.
# Bu il ölçümü, SPI ya da gözlenmiş kuraklık afeti sayısı DEĞİLDİR.
YAGIS_SAPMASI_2024={'Marmara':-19.7,'Ege':-22.4,'Akdeniz':-9.0,'İç Anadolu':-11.9,
                    'Karadeniz':2.2,'Doğu Anadolu':7.5,'Güneydoğu Anadolu':-6.9}
REGIONS={
 'Marmara':'Balıkesir Bilecik Bursa Çanakkale Edirne İstanbul Kırklareli Kocaeli Sakarya Tekirdağ Yalova'.split(),
 'Ege':'Afyonkarahisar Aydın Denizli İzmir Kütahya Manisa Muğla Uşak'.split(),
 'Akdeniz':'Adana Antalya Burdur Hatay Isparta Kahramanmaraş Mersin Osmaniye'.split(),
 'İç Anadolu':'Aksaray Ankara Çankırı Eskişehir Karaman Kayseri Kırıkkale Kırşehir Konya Nevşehir Niğde Sivas Yozgat'.split(),
 'Karadeniz':'Amasya Artvin Bartın Bayburt Bolu Çorum Düzce Giresun Gümüşhane Karabük Kastamonu Ordu Rize Samsun Sinop Tokat Trabzon Zonguldak'.split(),
 'Doğu Anadolu':'Ağrı Ardahan Bingöl Bitlis Elazığ Erzincan Erzurum Hakkâri Iğdır Kars Malatya Muş Tunceli Van'.split(),
 'Güneydoğu Anadolu':'Adıyaman Batman Diyarbakır Gaziantep Kilis Mardin Siirt Şanlıurfa Şırnak'.split(),
}

def key(s:str)->str:
    s=str(s).replace('İ','I').replace('ı','i').replace('â','a')
    return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c) and c.isalpha())

def provinces()->list[str]:
    data=json.loads((DATA/'turkiye_81_il.geojson').read_text(encoding='utf-8'))
    names=sorted(f['properties']['shapeName'] for f in data['features'])
    if len(names)!=81 or len(set(names))!=81:raise ValueError('81 il geometrisi bekleniyor')
    return names

def region_map()->dict[str,str]:
    d={}
    for r,names in REGIONS.items():
        for name in names:
            if name in d:raise ValueError('Tekrarlı bölge adı: '+name)
            d[name]=r
    expected=set(provinces())
    if set(d)!=expected:raise ValueError(f'Bölge/il eşleşmesi: eksik={expected-set(d)} fazla={set(d)-expected}')
    return d

def fire(year:int)->pd.DataFrame:
    if year not in (2024,2025):raise ValueError('Orman yangını yalnızca 2024 ve 2025 ön inceleme dosyalarına sahip')
    path=DATA/f'orman_yangini_{year}_IKINCIL_KAYNAK.csv'
    d=pd.read_csv(path)
    if len(d)!=81 or d['yil'].nunique()!=1 or int(d['yil'].iloc[0])!=year:raise ValueError('Yangın dosyası yıl/kapsam hatası')
    names={key(n):n for n in provinces()}
    d['İl']=d['il'].apply(lambda n:names.get(key(n)))
    if d['İl'].isna().any() or d['İl'].nunique()!=81:raise ValueError('Yangın dosyası 81 il eşleşmesi başarısız')
    d['Yangın sayısı']=pd.to_numeric(d['yangin_sayisi'],errors='coerce')
    d['Yanan alan (ha)']=pd.to_numeric(d['yanan_alan_ha'],errors='coerce')
    if (d['Yangın sayısı'].dropna()<0).any() or (d['Yanan alan (ha)'].dropna()<0).any():raise ValueError('Negatif değer')
    expected={2024:3797,2025:3224}[year]
    if int(d['Yangın sayısı'].sum())!=expected:raise ValueError(f'Yangın sayısı ulusal toplamla eşleşmiyor: {year}')
    area=float(d['Yanan alan (ha)'].sum())
    if abs(area-{2024:27485,2025:81473}[year])>0.51:raise ValueError('Yanan alan toplamı yayımlanan ulusal sonuçla uyuşmuyor')
    return d[['İl','Yangın sayısı','Yanan alan (ha)']].sort_values('İl').reset_index(drop=True)

def report_provinces(afet:str)->pd.DataFrame:
    if afet not in MGM_IL:raise ValueError('Bilinmeyen MGM afet türü')
    known=MGM_IL[afet]
    rows=[]
    for name in provinces():
        if name in known:
            desc,interval=known[name]
            rows.append({'İl':name,'Rapor vurgusu':2 if ('en çok' in desc or 'En yüksek' in desc) else 1,
                         'Açıklama':desc,'Olay aralığı':interval or 'Raporda kesin il sayısı verilmemiş',
                         'Kapsam':'Raporda açıkça belirtilmiş'})
        else:
            rows.append({'İl':name,'Rapor vurgusu':float('nan'),
                         'Açıklama':'Metinde açıkça adı geçmiyor; 0 olay anlamına gelmez.',
                         'Olay aralığı':'Bilinmiyor','Kapsam':'İl düzeyi sayı belirlenemedi'})
    return pd.DataFrame(rows)

def dryness()->pd.DataFrame:
    mapper=region_map()
    return pd.DataFrame([{'İl':name,'Bölge':mapper[name],
         'Bölge yağış sapması (%)':YAGIS_SAPMASI_2024[mapper[name]],
         'Gözlem ölçeği':'7 bölge; il bazında ayrı ölçülmedi'} for name in provinces()])

def get(afet:str,year:int=2024,metric:str|None=None)->dict:
    if afet=='Orman yangını':
        tab=fire(year)
        col=metric if metric in ('Yangın sayısı','Yanan alan (ha)') else 'Yangın sayısı'
        return {'afet':afet,'yil':year,'tablo':tab,'harita_kolonu':col,'birim':col,
                'ulusal_toplam':{2024:3797,2025:3224}[year] if col=='Yangın sayısı' else None,
                'kaynak':OGM_URL[year], 'tip':'ikincil_sayisal',
                'not':'İl tablosu OGM 2.14 istatistiklerine dayandırılan ikincil web aktarımıdır. Ulusal toplam kontrolü yapıldı, ancak resmî Excel ile satır bazında karşılaştırma henüz yapılmadı. Sıfır olmayan eksik hücreler bilinmiyor olarak tutulur.'}
    if year!=2024:raise ValueError('MGM değerlendirme kayıtları yalnızca 2024 yılı için işlendi.')
    if afet=='Kuraklık':
        return {'afet':afet,'yil':year,'tablo':dryness(),'harita_kolonu':'Bölge yağış sapması (%)',
                'birim':'1991–2020 normallerine göre 2024 bölgesel yağış değişimi (%)',
                'ulusal_toplam':None,'kaynak':MGM_URL,'tip':'bolgesel_meteoroloji',
                'not':'Bu haritadaki renkler coğrafi BÖLGE ortalamasını gösterir. Aynı bölgedeki iller aynı değeri alır. Yağış azalması SPI değeri veya kuraklık olayı sayısı değildir; 2024 MGM iklim raporundan alınmıştır.'}
    if afet in MGM_ULUSAL:
        return {'afet':afet,'yil':year,'tablo':report_provinces(afet),'harita_kolonu':'Rapor vurgusu',
                'birim':'MGM raporunda anılma durumu (1=anıldı, 2=öne çıktı)',
                'ulusal_toplam':MGM_ULUSAL[afet]['adet'],'kaynak':MGM_URL,'tip':'rapor_kaniti',
                'not':'Renkler olay sayısı veya resmî tehlike endeksi DEĞİLDİR. Yalnızca MGM 2024 raporunun metninde adı açıkça geçen illeri ve öne çıkarılanları gösterir. Gri illerde olay olmadığı sonucuna varılamaz. Kesin il sayıları raporun haritasında sınıflar hâlindedir.'}
    raise ValueError('Desteklenmeyen afet')
