"""Genel Bakış'ın veri temelli, modüller arası keşif katmanı.

Ana sayfa veri kaynağı olarak paketlenmiş 2025 nüfus, SEGE, OSM ve afet
özetlerini kullanır; USGS isteği veya deprem endeksi çalıştırmaz.
"""
from __future__ import annotations

import pandas as pd
from atlas_analiz import illere_ozet, sirala_ilceler
from atlas_afet_veri import fire
from ilce_veri import normalize_name
from atlas_il_yorumlari import yasam_il_yorumu, ticaret_il_yorumu, yangin_il_yorumu

OVERVIEW_TOPICS = ('Yaşam ve nüfus', 'Ticari hareketlilik', 'Doğal afetler')
TOPIC_DESTINATIONS = {
    'Yaşam ve nüfus': 'Yaşam Kalitesi',
    'Ticari hareketlilik': 'Ticari Potansiyel',
    'Doğal afetler': 'Afet Analizi',
}

# Ticari puanlar mevcut sektör modelinin ulusal ölçeğiyle hesaplanır.
# OSM eksikse model yalnızca kullanılabilir gerçek girdilere göre ağırlıklandırır.
OPPORTUNITY_SECTORS = {
    'Fırsat puanı · Yeme-içme': 'Yeme-içme',
    'Fırsat puanı · Perakende': 'Market / perakende',
    'Fırsat puanı · Hizmetler': 'Hizmetler',
    'Fırsat puanı · Lojistik': 'Lojistik / depolama',
}

LAYERS = {
    'Yaşam ve nüfus': {
        'Nüfus (2025)': 'Nüfus (2025)',
        'İlçe sayısı': 'İlçe sayısı',
        'Sosyoekonomik gelişmişlik': 'Ortalama ilçe SEGE sırası',
    },
    'Ticari hareketlilik': {
        **{label: label for label in OPPORTUNITY_SECTORS},
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
    'Ticari hareketlilik': 'Sektörel fırsat puanlarını, mevcut işletme kayıtlarını ve ulaşım göstergelerini karşılaştır.',
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
    provinces = illere_ozet(districts)
    # Yaşam/ticaret sıralamasında zaten kullanılan model; ulusal puanlar
    # karşılaştırılabilir olduğundan her ilin en yüksek üç ilçesinin ortalaması.
    for label, sector in OPPORTUNITY_SECTORS.items():
        ranked, _ = sirala_ilceler(districts, 'ticaret', 'Türkiye geneli', '', sector)
        best_three = ranked.groupby('il', sort=False).head(3)
        score = best_three.groupby('il')['Fırsat puanı'].mean()
        provinces[label] = provinces['İl'].map(score).round(1)
    return districts, provinces


def available_layers(provinces: pd.DataFrame, topic: str) -> list[str]:
    if topic not in LAYERS: raise ValueError('Bilinmeyen keşif konusu')
    if topic == 'Doğal afetler': return list(LAYERS[topic])
    return [name for name, column in LAYERS[topic].items() if column in provinces.columns]


def _validated_fire(year: int) -> pd.DataFrame:
    """Kullanılan özel veri bozulursa doğrulanmış paket verisini kullan."""
    try:
        return fire(year)
    except (ValueError, OSError, KeyError, TypeError):
        from atlas_yonetim_depo import BUNDLED
        return fire(year, data_dir=BUNDLED)


def layer_frame(provinces: pd.DataFrame, topic: str, label: str) -> tuple[pd.DataFrame, str, str]:
    """81 il için bir katman: (tablo, sütun adı, gösterim etiketi)."""
    if label not in LAYERS.get(topic, {}): raise ValueError('Seçilen katman tanınmıyor')
    col = LAYERS[topic][label]
    if topic == 'Doğal afetler':
        year=2024 if '2024' in label else 2025
        data=_validated_fire(year)
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
        if label in OPPORTUNITY_SECTORS:
            sector=OPPORTUNITY_SECTORS[label]
            ranked, meta=sirala_ilceler(districts, 'ticaret', 'Türkiye geneli', '', sector)
            local_best=ranked.loc[ranked.il.eq(city)].iloc[0]
            score=float(p[col])
            result.update({
                'title':'Sektörel fırsat ön değerlendirmesi',
                'text':(f'{city} için {sector} sektöründeki il puanı {score:.1f}. '
                        f'Bu değer, ilin ulusal ölçekle puanlanan en güçlü üç ilçesinin ortalamasıdır. '
                        f'İlde en yüksek puanlı ilçe {local_best.ilce} ({float(local_best["Fırsat puanı"]):.1f}). '
                        'Model yalnızca doğrulanabilen göstergeleri kullanır.'),
                'key_label':'İl fırsat puanı', 'key_value':f'{score:.1f} / 100',
                'secondary_label':'İl içindeki öncü ilçe', 'secondary_value':str(local_best.ilce),
            })
            return result
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
        previous=_validated_fire(2024) if year==2025 else None
        result.update({
            'title':'Afet profili',
            'text':yangin_il_yorumu(city,year,col,_validated_fire(year),previous),
            'key_label':label,
            'key_value': ((f'{value:,.1f} ha'.replace(',','X').replace('.',',').replace('X','.'))
                          if col=='Yanan alan (ha)' and pd.notna(value) else
                          (f'{int(value):,}'.replace(',','.') if pd.notna(value) else '—')),
        })
    return result
