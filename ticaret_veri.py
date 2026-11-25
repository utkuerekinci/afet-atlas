"""Ticaret veri katmanı: 973 ilçelik doğrulanmış OSM gözlemleri ve isteğe bağlı kira.

Boş OSM dosyasını veya kısmi kapsamı 0 rakip/0 durak olarak sunmaz.
Kira CSV'si yalnızca referans gösterilir; kısmi kira ulusal endekse girmez.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import pandas as pd
from ilce_veri import normalize_name

ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('AFET_ATLAS_DATA_DIR') or (ROOT/'indirilen_veriler'))
OSM_CSV=DATA/'ticaret_osm_ilce.csv'
OSM_META=DATA/'ticaret_osm_manifest.json'
KIRA_CSV=DATA/'ticaret_kira_ilce.csv'
SEKTOR_SUTUNLARI={
    'Yeme-içme':'osm_yeme_icme',
    'Market / perakende':'osm_market_perakende',
    'Hizmetler':'osm_hizmetler',
    'Lojistik / depolama':'osm_lojistik',
}
OSM_SUTUNLAR=list(SEKTOR_SUTUNLARI.values())+['osm_ulasim']


def _key(il,ilce): return normalize_name(il)+':'+normalize_name(ilce)

# OSM/coğrafi kaynak ile nüfus kaydının yayımlanmış ad farkları; belirsiz fuzzy eşleme yok.
ALIASES={
    ('amasya','amasya'):'amasyamerkez',
    ('canakkale','canakkale'):'canakkalemerkez',
    ('igdir','igdir'):'igdirmerkez',
    ('siirt','siirt'):'siirtmerkez',
    ('tokat','tokat'):'tokatmerkez',
    ('usak','usak'):'usakmerkez',
    ('agri','panos'):'patnos',
    ('kirikkale','balisih'):'baliseyh',
    ('tunceli','nazmiye'):'nazimiye',
    ('yozgat','sarikayaderesi'):'sarikaya',
    ('samsun','ondokuzmayis'):'19mayis',
}


def canonical_key(il,ilce):
    province,district=normalize_name(il),normalize_name(ilce)
    district=ALIASES.get((province,district),district)
    if district==province:district+='merkez'  # yalnızca adın il ile aynı olduğu merkez ilçeler
    return province+':'+district


def _base_keys(base:pd.DataFrame):
    district_col='ilce_nufus_kaynagi' if 'ilce_nufus_kaynagi' in base else 'ilce'
    return pd.Series([canonical_key(il,ilce) for il,ilce in zip(base.il,base[district_col])],index=base.index)


def _aligned(base:pd.DataFrame,other:pd.DataFrame,require_full:bool):
    if not {'il','ilce'}.issubset(other): raise ValueError('İl ve ilçe alanları eksik.')
    d=other.copy()
    d['_anahtar']=[canonical_key(il,ic) for il,ic in zip(d.il,d.ilce)]
    if d['_anahtar'].duplicated().any():raise ValueError('Aynı ilçeye ait birden fazla satır var.')
    keyed=_base_keys(base)
    if keyed.duplicated().any():raise ValueError('Ana nüfus tablosunda yinelenen ilçe var.')
    other_keys=set(d._anahtar)
    missing=set(keyed)-other_keys
    extra=other_keys-set(keyed)
    if extra or (require_full and missing):
        raise ValueError(f'Eşleşme doğrulanamadı: {len(missing)} eksik, {len(extra)} yabancı. Örnek: {sorted(missing)[:4]}, {sorted(extra)[:4]}')
    d=d.set_index('_anahtar').drop(columns=['il','ilce'])
    return d.reindex(keyed.to_numpy()).set_axis(base.index,axis=0)


def osm_oku(base:pd.DataFrame) -> tuple[pd.DataFrame|None,str]:
    if not OSM_CSV.exists() or not OSM_META.exists():
        return None,'OSM işletme/ulaşım veri özeti henüz oluşturulmadı.'
    try:
        meta=json.loads(OSM_META.read_text(encoding='utf-8'))
        if meta.get('kaynak')!='OpenStreetMap / Geofabrik' or meta.get('olcek')!='Türkiye 973 ilçe' or not meta.get('olusturma_tarihi'):
            raise ValueError('Veri manifestosu doğrulanamadı.')
        data=pd.read_csv(OSM_CSV,encoding='utf-8-sig')
        if len(data)!=973 or not set(OSM_SUTUNLAR).issubset(data):
            raise ValueError('OSM tablosu 973 satır ve gerekli sektörel sütunları içermiyor.')
        for col in OSM_SUTUNLAR:
            numbers=pd.to_numeric(data[col],errors='raise')
            if numbers.isna().any() or (numbers<0).any() or not (numbers%1==0).all():
                raise ValueError(col+' geçersiz veya eksik.')
            data[col]=numbers.astype('int64')
        # Bütün Türkiye için gönderilen özet dosya, küçük bir coğrafi alt küme
        # olup geri kalanı 0 ile doldurulmuşsa yanlış sıralama yapmayalım.
        active=data[OSM_SUTUNLAR].sum(axis=1)>0
        if data.loc[active,'il'].nunique()!=81:
            raise ValueError('81 ilin tamamında en az bir OSM etiketi gözlenmedi; kapsam kısmi olabilir.')
        matched=_aligned(base,data,require_full=True)
        return matched,'OSM kayıtları eşleşti (973/973). Kaynak tarihi: '+str(meta.get('osm_veri_tarihi','bilinmiyor'))
    except (ValueError,KeyError,OSError,pd.errors.ParserError) as exc:
        return None,'OSM verisi kullanılamıyor: '+str(exc)


def kira_oku(base:pd.DataFrame) -> tuple[pd.DataFrame|None,str]:
    if not KIRA_CSV.exists():
        return None,'Ticari kira verisi yüklenmedi; erişim anahtarı/izin gerektiren kaynak kullanılmadı.'
    try:
        d=pd.read_csv(KIRA_CSV,encoding='utf-8-sig')
        fields={'il','ilce','kira_m2_tl','kaynak','tarih','ilan_adedi'}
        if not fields.issubset(d):raise ValueError('Kira CSV alanları eksik.')
        if len(d)>973 or len(d)==0:raise ValueError('Kira satır sayısı geçersiz.')
        d['kira_m2_tl']=pd.to_numeric(d.kira_m2_tl,errors='raise')
        d['ilan_adedi']=pd.to_numeric(d.ilan_adedi,errors='raise')
        if (d.kira_m2_tl<=0).any() or (d.ilan_adedi<=0).any() or d[['kaynak','tarih']].isna().any().any():
            raise ValueError('Kira fiyatı, ilan örneklemi veya kaynak bilgisi geçersiz.')
        m=_aligned(base,d,require_full=False)
        return m, f'İlan kaynaklı işyeri kiraları: {len(d)}/973 ilçe; gerçekleşmiş kira değildir.'
    except (ValueError,KeyError,OSError,pd.errors.ParserError) as exc:
        return None,'Kira verisi kullanılamıyor: '+str(exc)


def zenginlestir_ilceler(base:pd.DataFrame)->tuple[pd.DataFrame,dict]:
    out=base.copy()
    osm,status=osm_oku(out)
    out_status={'osm':status,'osm_aktif':osm is not None}
    if osm is not None:
        for col in OSM_SUTUNLAR:out[col]=osm[col]
    kira,kira_status=kira_oku(out)
    out_status['kira']=kira_status
    out_status['kira_kapsami']=int(kira['kira_m2_tl'].notna().sum()) if kira is not None else 0
    if kira is not None:
        for col in ('kira_m2_tl','kaynak','tarih','ilan_adedi'):
            out[col]=kira[col]
        out['kira_ulusal_tam']= bool(len(out)==973 and kira.kira_m2_tl.notna().all() and (kira.ilan_adedi>=5).all())
    return out,out_status
