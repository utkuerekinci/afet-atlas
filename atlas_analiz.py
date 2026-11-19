"""Açıklanabilir yaşam tercihi ve ticaret sıralama motoru.

Ham gözlemler ve proje modeli ayrıdır. Sektörlerin gerçek kârlılığı iddia edilmez.
"""
from __future__ import annotations
import pandas as pd
from bolge_puanlari import _sirala, SEKTOR_AGIRLIKLARI, ticari_on_endeks, yasam_tercih_endeksi

NAMES = {
    'nufus':'Yerleşik nüfus', 'yogunluk':'Yaklaşık nüfus yoğunluğu',
    'dusuk_yogunluk':'Düşük nüfus yoğunluğu', 'sege':'SEGE-2022 gelişmişlik sırası',
    'isletme_kumesi':'OSM sektörel işletme kümelenmesi',
    'rekabet_baskisi':'OSM nüfusa göre rekabet baskısı (ters)',
    'ulasim':'OSM toplu taşıma durak/istasyon kaydı',
    'kira':'İlan kaynaklı ticari kira m² (ters)',
    'yasam_ritmi':'Yerleşim karakterine uyum',
}

def sirala_ilceler(all_districts: pd.DataFrame, mode: str, kapsam: str, il: str,
                   sektor: str = 'Yeme-içme', tercih: str = 'Dengeli') -> tuple[pd.DataFrame, dict]:
    """Türkiye ya da il içi; tek ve aynı evrene göre puanlama yapar."""
    if kapsam not in {'Türkiye geneli','İl içi'}: raise ValueError('Geçersiz kapsam')
    data=all_districts.copy() if kapsam=='Türkiye geneli' else all_districts[all_districts.il==il].copy()
    if data.empty: raise ValueError('Seçilen kapsamda ilçe yok')
    if mode=='ticaret':
        ranked,meta=ticari_on_endeks(data,sektor)
        col='Fırsat puanı'
        for key,weight in meta['agirliklar'].items():
            ranked['Katkı: '+NAMES[key]]=ranked['Katkı: '+key]
        meta.update({'puan_sutunu':col,'mod':mode,'kapsam':kapsam,'il':il,
                     'model':'Sektör ağırlıklı göreli ön değerlendirme'})
    elif mode=='yasam':
        ranked=yasam_tercih_endeksi(data,tercih)
        pop_percent=_sirala(data.nufus)
        density_valid=('nufus_yogunlugu_km2' in data and
                       data.nufus_yogunlugu_km2.notna().all())
        density_percent=_sirala(data.nufus_yogunlugu_km2) if density_valid else None
        level=(pop_percent*.5+density_percent*.5) if density_valid else pop_percent
        ranked['Nüfus gösterge puanı']=pop_percent.reindex(ranked.index).round(2)
        if density_valid:ranked['Yoğunluk gösterge puanı']=density_percent.reindex(ranked.index).round(2)
        ranked['Yerleşim hareketlilik düzeyi']=level.reindex(ranked.index).round(2)
        weights0={'yasam_ritmi':.60,'sege':.30,'ulasim':.10}
        used=[key for key in weights0 if 'Yaşam katkısı: '+key in ranked]
        total=sum(weights0[key] for key in used)
        weights={key:weights0[key]/total for key in used}
        meta={'puan_sutunu':'Tercih uyumu','mod':mode,'kapsam':kapsam,'il':il,
              'model':'Yaşam ritmi, sosyoekonomik gelişmişlik ve erişim dengesi',
              'agirliklar':weights,'kullanilan':used,
              'kullanilamayan':[k for k in weights0 if k not in used],
              'tercih':tercih}
    else: raise ValueError('Tanımsız mod')
    ranked=ranked.copy().reset_index(drop=True)
    ranked['Sıra']=range(1,len(ranked)+1)
    return ranked,meta



def _sayici(value: float) -> str:
    """Okunabilir nüfus değeri; hiçbir gözleme müdahale edilmez."""
    return f"{int(value):,}".replace(",", ".")


def _yorum_paragrafi(ranked: pd.DataFrame, meta: dict, factors: list[dict]) -> str:
    """Her liderin kendi verisine ve en yakın rakibine göre açıklama oluştur."""
    from atlas_yorum_motoru import yorum_uret
    return yorum_uret(ranked, meta, factors)


def neden_birinci(ranked: pd.DataFrame, meta: dict) -> dict:
    """Birinci ve ikinci ilçenin gerçek sütunlarını, katkılarını verir."""
    if ranked.empty:return {'hata':'İlçe verisi yok.'}
    a=ranked.iloc[0]; b=ranked.iloc[1] if len(ranked)>1 else None
    col=meta['puan_sutunu']; factors=[]
    if meta['mod']=='ticaret':
        for k,weight in meta['agirliklar'].items():
            name='Katkı: '+NAMES[k]
            factors.append({'anahtar':k, 'gosterge':NAMES[k], 'agirlik_yuzde':round(weight*100,1),
                            'birinci_katki':round(float(a[name]),2),
                            'ikinci_katki':round(float(b[name]),2) if b is not None else None,
                            'katki_farki':round(float(a[name]-b[name]),2) if b is not None else None})
    else:
        factors=[{'anahtar':k, 'gosterge':NAMES[k], 'agirlik_yuzde':round(w*100,1),
                  'birinci_katki':round(float(a['Yaşam katkısı: '+k]),2),
                  'ikinci_katki':round(float(b['Yaşam katkısı: '+k]),2) if b is not None else None,
                  'katki_farki':round(float(a['Yaşam katkısı: '+k]-b['Yaşam katkısı: '+k]),2) if b is not None else None}
                 for k,w in meta['agirliklar'].items()]
    return {'birinci':{'il':str(a.il),'ilce':str(a.ilce),'puan':round(float(a[col]),1)},
            'ikinci':{'il':str(b.il),'ilce':str(b.ilce),'puan':round(float(b[col]),1)} if b is not None else None,
            'fark':round(float(a[col]-b[col]),1) if b is not None else None,
            'gostergeler':factors,'kapsam':meta['kapsam'],'model':meta['model'],
            'veri_kapsami':{'osm_isletme_ulasim':'osm_ulasim' in ranked,'osm_sektor_puanda':bool(meta.get('osm_aktif')),'kira_puana_dahil':bool(meta.get('kira_puana_dahil'))} if meta['mod']=='ticaret' else {},
            'yorum_paragrafi':_yorum_paragrafi(ranked,meta,factors),
            'ozet':'Seçilen ilçenin güçlü yönleri, alternatifleri ve önerilen kullanım senaryosu.'}


def illere_ozet(ilceler:pd.DataFrame) -> pd.DataFrame:
    out=ilceler.groupby('il',as_index=False).agg(nufus=('nufus','sum'),ilce_sayisi=('ilce','count'))
    out=out.rename(columns={'il':'İl','nufus':'Nüfus (2025)','ilce_sayisi':'İlçe sayısı'})
    if 'sege_sira' in ilceler and ilceler.sege_sira.notna().all():
        out=out.merge(ilceler.groupby('il',as_index=False)['sege_sira'].mean().rename(columns={'il':'İl','sege_sira':'Ortalama ilçe SEGE sırası'}),on='İl')
    if all(x in ilceler for x in ('osm_yeme_icme','osm_market_perakende','osm_hizmetler','osm_lojistik','osm_ulasim')):
        names={'osm_yeme_icme':'OSM yeme-içme kaydı','osm_market_perakende':'OSM perakende kaydı',
               'osm_hizmetler':'OSM hizmet kaydı','osm_lojistik':'OSM lojistik kaydı',
               'osm_ulasim':'OSM ulaşım kaydı'}
        counts=ilceler.groupby('il',as_index=False)[list(names)].sum().rename(columns={'il':'İl',**names})
        out=out.merge(counts,on='İl',validate='one_to_one')
    if len(out)!=81: raise ValueError('81 ilin nüfus toplamları bulunamadı')
    return out
