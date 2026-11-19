"""Genel Bakış'ın veri temelli, modüller arası keşif katmanı.

Ana sayfa veri kaynağı olarak paketlenmiş 2025 nüfus, SEGE, OSM ve afet
özetlerini kullanır; USGS isteği veya deprem endeksi çalıştırmaz.
"""
from __future__ import annotations

import pandas as pd
from atlas_analiz import illere_ozet
from atlas_afet_veri import fire
from ilce_veri import normalize_name
from atlas_il_yorumlari import yasam_il_yorumu, ticaret_il_yorumu, yangin_il_yorumu

OVERVIEW_TOPICS = ('Yaşam ve nüfus', 'Ticari hareketlilik', 'Doğal afetler')
TOPIC_DESTINATIONS = {
    'Yaşam ve nüfus': 'Yaşam Kalitesi',
    'Ticari hareketlilik': 'Ticari Potansiyel',
    'Doğal afetler': 'Afet Analizi',
}

LAYERS = {
    'Yaşam ve nüfus': {
        'Nüfus (2025)': 'Nüfus (2025)',
        'İlçe sayısı': 'İlçe sayısı',
        'Sosyoekonomik gelişmişlik': 'Ortalama ilçe SEGE sırası',
    },
    'Ticari hareketlilik': {
        'Yeme-içme': 'OSM yeme-içme kaydı',
        'Perakende': 'OSM perakende kaydı',
        'Hizmetler': 'OSM hizmet kaydı',
        'Lojistik': 'OSM lojistik kaydı',
        'Ulaşım bağlantıları': 'OSM ulaşım kaydı',
    },
    'Doğal afetler': {
        'Orman yangınları · 2025': 'Yangın sayısı',
        'Orman yangınları · 2024': 'Yangın sayısı',
        'Yanan alan · 2025': 'Yanan alan (ha)',
    },
}

TOPIC_DESCRIPTIONS = {
    'Yaşam ve nüfus': 'Nüfusun dağılımını, ilçelerin büyüklüğünü ve gelişmişlik profilini birlikte keşfet.',
    'Ticari hareketlilik': 'İşletmelerin nerelerde kümelendiğini ve ulaşım bağlantılarının nasıl dağıldığını gör.',
    'Doğal afetler': 'Orman yangını kayıtlarının il bazındaki dağılımına bak; diğer afet türlerini ayrıntılı analizde incele.',
}


def prepare_provinces(districts: pd.DataFrame, boundaries: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """İlçeleri yalnızca bilinen il sınırı isimleriyle eşleştirip özetle."""
    aliases = {normalize_name(f['properties']['shapeName']):f['properties']['shapeName']
               for f in boundaries['features']}
    if len(aliases) != 81 or set(districts.il.map(normalize_name)) != set(aliases):
        raise ValueError('İlçe verileri ile 81 ilin sınırları örtüşmüyor.')
    districts = districts.copy()
    districts['il'] = districts['il'].map(lambda name: aliases[normalize_name(name)])
    return districts, illere_ozet(districts)


def available_layers(provinces: pd.DataFrame, topic: str) -> list[str]:
    if topic not in LAYERS: raise ValueError('Bilinmeyen keşif konusu')
    if topic == 'Doğal afetler': return list(LAYERS[topic])
    return [name for name, column in LAYERS[topic].items() if column in provinces.columns]


def layer_frame(provinces: pd.DataFrame, topic: str, label: str) -> tuple[pd.DataFrame, str, str]:
    """81 il için bir katman: (tablo, sütun adı, gösterim etiketi)."""
    if label not in LAYERS.get(topic, {}): raise ValueError('Seçilen katman tanınmıyor')
    col = LAYERS[topic][label]
    if topic == 'Doğal afetler':
        year=2024 if '2024' in label else 2025
        data=fire(year)
        return data[['İl', col]].copy(), col, ('Orman yangını sayısı' if col=='Yangın sayısı' else 'Yanan alan (ha)')
    if col not in provinces: raise ValueError('Bu veri katmanı henüz yüklenmemiş')
    return provinces[['İl', col]].copy(), col, col


def city_summary(districts: pd.DataFrame, provinces: pd.DataFrame,
                 city: str, topic: str, label: str) -> dict:
    """Görünen il için nokta atışı, gözleme dayalı kısa yorum üretir."""
    row = provinces.loc[provinces['İl'].eq(city)]
    local = districts.loc[districts.il.eq(city)]
    if len(row)!=1 or local.empty: raise ValueError('Seçili ilin ilçeleri bulunamadı')
    p = row.iloc[0]
    max_pop = local.sort_values(['nufus','ilce'],ascending=[False,True]).iloc[0]
    result = {
        'il':city,
        'nufus':int(p['Nüfus (2025)']),
        'ilce':int(p['İlçe sayısı']),
        'buyuk_ilce':str(max_pop.ilce),
        'buyuk_ilce_nufus':int(max_pop.nufus),
    }
    if topic=='Yaşam ve nüfus':
        result.update({
            'title': 'Yerleşim profili',
            'text': yasam_il_yorumu(local,provinces,city,label),
            'key_label':'En kalabalık ilçe','key_value':str(max_pop.ilce),
        })
    elif topic=='Ticari hareketlilik':
        col=LAYERS[topic][label]
        local_columns={
            'OSM yeme-içme kaydı':'osm_yeme_icme',
            'OSM perakende kaydı':'osm_market_perakende',
            'OSM hizmet kaydı':'osm_hizmetler',
            'OSM lojistik kaydı':'osm_lojistik',
            'OSM ulaşım kaydı':'osm_ulasim',
        }
        district_col=local_columns[col]
        if col not in p or district_col not in local:
            raise ValueError('Ticaret verileri hazır değil')
        leader=local.sort_values([district_col,'ilce'],ascending=[False,True]).iloc[0]
        count=int(p[col]);best=int(leader[district_col])
        display_names={
            'Yeme-içme':'Yeme-içme','Perakende':'Perakende',
            'Hizmetler':'Hizmet','Lojistik':'Lojistik',
            'Ulaşım bağlantıları':'Ulaşım',
        }
        result.update({
            'title':'İş ve erişim profili',
            'text':ticaret_il_yorumu(local,city,label,district_col),
            'key_label':display_names[label]+' kayıtları',
            'key_value':f'{count:,}'.replace(',','.'),
            'secondary_label':'En yoğun ilçe',
            'secondary_value':f'{leader.ilce} · {best:,}'.replace(',','.'),
        })
    else:
        region=layer_frame(provinces,topic,label)[0]
        r=region.loc[region['İl'].eq(city)].iloc[0]
        col=LAYERS[topic][label]
        value=r[col]
        year=2024 if '2024' in label else 2025
        previous=fire(2024) if year==2025 else None
        result.update({
            'title':'Afet profili',
            'text':yangin_il_yorumu(city,year,col,fire(year),previous),
            'key_label':label,
            'key_value': ((f'{value:,.1f} ha'.replace(',','X').replace('.',',').replace('X','.'))
                          if col=='Yanan alan (ha)' and pd.notna(value) else
                          (f'{int(value):,}'.replace(',','.') if pd.notna(value) else '—')),
        })
    return result
