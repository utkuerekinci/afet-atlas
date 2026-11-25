"""Genel Bakış'ın veri temelli, modüller arası keşif katmanı.

Ana sayfa veri kaynağı olarak paketlenmiş 2025 nüfus, SEGE, OSM ve afet
özetlerini kullanır; USGS isteği veya deprem endeksi çalıştırmaz.
"""
from __future__ import annotations

import pandas as pd
from atlas_analiz import illere_ozet, sirala_ilceler
from atlas_afet_veri import safe_fire, MGM_IL, YAGIS_SAPMASI_2024, region_map, ROOT
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
        'Ortalama ticari puan': 'Ortalama ticari puan',
    },
    'Doğal afetler': {
        'Güvenlik skoru (%)': 'Güvenlik skoru (%)',
    },
}

TOPIC_DESCRIPTIONS = {
    'Yaşam ve nüfus': 'Nüfusun dağılımını, ilçelerin büyüklüğünü ve gelişmişlik profilini birlikte keşfet.',
    'Ticari hareketlilik': 'Dört sektörün birlikte değerlendirilmesiyle oluşan il bazlı ortalama ticari puanları keşfet.',
    'Doğal afetler': 'Deprem, yangın, sel, heyelan, çığ, fırtına ve kuraklık göstergelerini birleştiren il güvenlik skorlarını keşfet.',
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
    # Ana sayfada sektör filtresi yoktur: dört model sonucunun eşit ağırlıklı ortalaması.
    # Ticari Potansiyel sayfasındaki sektör seçimi değişmez.
    provinces['Ortalama ticari puan'] = provinces[list(OPPORTUNITY_SECTORS)].mean(axis=1).round(1)
    return districts, provinces


def available_layers(provinces: pd.DataFrame, topic: str) -> list[str]:
    if topic not in LAYERS: raise ValueError('Bilinmeyen keşif konusu')
    if topic == 'Doğal afetler': return list(LAYERS[topic])
    return [name for name, column in LAYERS[topic].items() if column in provinces.columns]


def _validated_fire(year: int) -> pd.DataFrame:
    return safe_fire(year)


# Afet Atlas'ın ders projesi için belirlenmiş model ağırlıkları.
# Bileşenler farklı ölçü birimlerinden geldiği için önce 0..1 karşılaştırma
# sırasına dönüştürülür. Resmî tehlike olasılığı veya bilimsel güvenlik oranı değildir.
AFET_GUVENLIK_AGIRLIKLARI = {
    'deprem': 0.30,
    'orman_yangini': 0.20,
    'sel': 0.12,
    'heyelan': 0.10,
    'cig': 0.06,
    'firtina': 0.10,
    'kuraklik': 0.12,
}


def _sira_riski(series: pd.Series) -> pd.Series:
    """Daha büyük gözlem = daha büyük göreli faaliyet; eşitler aynı değeri alır."""
    numeric = pd.to_numeric(series, errors='coerce').clip(lower=0)
    if numeric.dropna().nunique() <= 1:
        return pd.Series(0.5, index=series.index, dtype=float)
    # Null değerleri asla sıfır olay gibi değerlendirme.
    count = numeric.notna().sum()
    ranks = numeric.rank(method='average', pct=True)
    return ((ranks*count - 1) / (count - 1)).clip(0, 1)


def _deprem_2025_faaliyeti(illler: list[str]) -> pd.Series:
    """Paketlenmiş 2025 USGS M>=4.5 katalogundaki olayları illere eşleştir.

    Kayıt coğrafi açıdan sınırda değilse yalnızca sınıra yaklaşık 30 km
    mesafedeki en yakın il dikkate alınır; uzak deniz depremleri sayılmaz.
    Her olay yalnızca bir ile bağlanır.
    """
    from shapely.geometry import shape, Point
    import json
    import numpy as np
    boundaries = json.loads((ROOT/'indirilen_veriler'/'turkiye_81_il.geojson').read_text('utf-8'))
    polygons = {f['properties']['shapeName']: shape(f['geometry']) for f in boundaries['features']}
    if set(polygons) != set(illler):
        raise ValueError('Deprem analizi ile 81 il sınırı eşleşmedi')
    path = ROOT/'indirilen_veriler'/'usgs_2025_m4_5.csv'
    try:
        earthquakes = pd.read_csv(path, usecols=['latitude','longitude','mag','type','id'])
    except (OSError, ValueError, KeyError):
        # Kaynak yoksa deprem riskini 0 saymak yerine nötr değer kullan.
        return pd.Series(0.5, index=illler, dtype=float)
    earthquakes['mag'] = pd.to_numeric(earthquakes['mag'], errors='coerce')
    earthquakes['latitude'] = pd.to_numeric(earthquakes['latitude'], errors='coerce')
    earthquakes['longitude'] = pd.to_numeric(earthquakes['longitude'], errors='coerce')
    earthquakes = earthquakes.dropna(subset=['mag','latitude','longitude'])
    earthquakes = earthquakes.loc[(earthquakes['type']=='earthquake') & (earthquakes['mag']>=4.5)]
    earthquakes = earthquakes.drop_duplicates('id')
    intensity = pd.Series(0.0, index=illler, dtype=float)
    # Olay sayısı + büyüklük ölçeği; 2025 kayıtlarına dayalı tarihsel aktivite göstergesi.
    for row in earthquakes.itertuples(index=False):
        point = Point(float(row.longitude), float(row.latitude))
        inside = [name for name,geom in polygons.items() if geom.covers(point)]
        if inside:
            assigned = inside[0]
        else:
            # Derece yerine enlem ölçeğini dikkate alan yaklaşık yakınlık kontrolü.
            # 30 km = ~0.27 derece enlem; kısa enlem-boya uzaklıkları normalize edilir.
            candidate = min(((geom.distance(point), name) for name,geom in polygons.items()), key=lambda item:item[0])
            if candidate[0] > 0.32:
                continue
            assigned = candidate[1]
        intensity.loc[assigned] += (float(row.mag) - 3.5) ** 2
    return _sira_riski(intensity)


def _rapor_riski(il: list[str], afet: str) -> pd.Series:
    """MGM'de sözü edilmeyen il = nötr; var/yok sayımı yerine rapor vurgusu."""
    result = pd.Series(0.5, index=il, dtype=float)
    for name, (description, _) in MGM_IL[afet].items():
        if name in result.index:
            result.loc[name] = 0.95 if ('en çok' in description.casefold() or 'en yüksek' in description.casefold()) else 0.75
    return result


def afet_guvenlik_bilesenleri() -> pd.DataFrame:
    """Birbiriyle karşılaştırılabilir 81 il için 7 afet türü bileşenleri."""
    names = sorted(region_map())
    risk = pd.DataFrame(index=names)
    risk['deprem'] = _deprem_2025_faaliyeti(names)
    years = []
    for year in (2024, 2025):
        fire = _validated_fire(year).set_index('İl')
        if set(fire.index) != set(names):
            raise ValueError('Yangın verilerinin 81 il kapsamı eksik')
        count = _sira_riski(fire['Yangın sayısı'])
        area = _sira_riski(fire['Yanan alan (ha)'])
        years.append(pd.concat([count, area], axis=1).mean(axis=1, skipna=True))
    risk['orman_yangini'] = pd.concat(years, axis=1).mean(axis=1, skipna=True)
    for code, name in [('sel','Sel / taşkın'),('heyelan','Heyelan'),('cig','Çığ'),('firtina','Fırtına')]:
        risk[code] = _rapor_riski(names, name)
    # MGM bölgesel yağış sapması: negatif değer, kuraklık sinyali.
    areas = region_map()
    deficit = pd.Series({il: max(0.0, -YAGIS_SAPMASI_2024[areas[il]]) for il in names}, dtype=float)
    max_deficit = float(deficit.max())
    risk['kuraklik'] = (deficit/max_deficit) if max_deficit else 0.5
    # Bütün il/afet bileşenleri kaydedilmiş kaynaklar üzerinden üretilir.
    if risk.isna().any().any() or risk.shape != (81, 7):
        raise ValueError('Afet bileşenlerinde doğrulanamayan veri var')
    return risk.rename_axis('İl').reset_index()


def provincial_safety_scores() -> pd.DataFrame:
    """Yedi afetten güncel skorları hesapla; geçici veri hatasında doğrulanmış skora dön."""
    try:
        risk = afet_guvenlik_bilesenleri().set_index('İl')
        weights = AFET_GUVENLIK_AGIRLIKLARI
        weighted = sum(risk[key] * weight for key, weight in weights.items())
        score = ((1-weighted)*100).clip(lower=0,upper=100).round().astype(int)
        result = score.rename('Güvenlik skoru (%)').rename_axis('İl').reset_index()
        if len(result)!=81 or result['Güvenlik skoru (%)'].isna().any():
            raise ValueError('81 il için güvenlik skoru oluşturulamadı')
        return result
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Canlı afet göstergesi hesaplanamadı; doğrulanmış paket skorları kullanılıyor')
        from pathlib import Path
        bundled = Path(__file__).resolve().parent / 'afet_guvenlik_paket_81_il.csv'
        fallback = pd.read_csv(bundled, encoding='utf-8-sig')
        if (len(fallback)!=81 or fallback['İl'].nunique()!=81 or
            fallback['Güvenlik skoru (%)'].isna().any() or
            not fallback['Güvenlik skoru (%)'].between(0,100).all() or
            set(fallback['İl'])!=set(region_map())):
            raise ValueError('Yedek afet skorlarının doğrulaması başarısız')
        return fallback[['İl','Güvenlik skoru (%)']]


def layer_frame(provinces: pd.DataFrame, topic: str, label: str) -> tuple[pd.DataFrame, str, str]:
    """81 il için bir katman: (tablo, sütun adı, gösterim etiketi)."""
    if label not in LAYERS.get(topic, {}): raise ValueError('Seçilen katman tanınmıyor')
    col = LAYERS[topic][label]
    if topic == 'Doğal afetler':
        data=provincial_safety_scores()
        return data[['İl', col]].copy(), col, 'Güvenlik skoru (%)'
    if col not in provinces: raise ValueError('Bu veri katmanı henüz yüklenmemiş')
    return provinces[['İl', col]].copy(), col, col


def city_summary(districts: pd.DataFrame, provinces: pd.DataFrame,
                 city: str, topic: str, label: str,
                 safety_snapshot: pd.DataFrame | None = None) -> dict:
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
        if label == 'Ortalama ticari puan':
            score = float(p[col])
            result.update({
                'title': 'Ticari hareketlilik özeti',
                'text': (f'{city} için dört ticaret sektörünün il bazındaki '
                         f'ortalama model puanı {score:.1f}/100.'),
                'key_label': 'Ortalama ticari puan',
                'key_value': f'{score:.1f} / 100',
            })
            return result
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
        record = (safety_snapshot if safety_snapshot is not None else
                  provincial_safety_scores()).set_index('İl').loc[city]
        score = int(record['Güvenlik skoru (%)'])
        result.update({
            'title': 'Afet güvenlik profili',
            'text': (f'{city} için deprem, orman yangını, sel, heyelan, çığ, fırtına '
                     f've kuraklık göstergelerinden hesaplanan güvenlik skoru %{score}. '
                     'Skor geçmiş kayıtlardaki göstergeleri ortak bir ölçekte karşılaştırır.'),
            'key_label': 'Güvenlik skoru',
            'key_value': f'%{score}',
        })
    return result
