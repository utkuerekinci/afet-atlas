"""İl sınırlarına uzaklıkları ve kullanıcı tanımlı deprem hareketliliği puanlarını hesaplar."""
from __future__ import annotations

import math

import pandas as pd
from pyproj import CRS, Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform

# Türkiye merkezli eşit uzaklık projeksiyonu: uzaklıkları metre cinsinden hesaplarız.
PROJEKSIYON = CRS.from_proj4('+proj=aeqd +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs')
DONUSTURUCU = Transformer.from_crs('EPSG:4326', PROJEKSIYON, always_xy=True)


def olay_puani(buyukluk: float) -> int:
    """Bunlar bilimsel risk katsayıları değil, proje için örnek ağırlıklardır."""
    if buyukluk >= 7.0:
        return 7
    if buyukluk >= 6.0:
        return 5
    if buyukluk >= 5.0:
        return 3
    if buyukluk >= 4.5:
        return 1
    return 0


def illeri_hazirla(geojson: dict) -> list[tuple[str, object]]:
    iller = []
    for kayit in geojson['features']:
        isim = kayit['properties']['shapeName']
        geometri = transform(DONUSTURUCU.transform, shape(kayit['geometry']))
        if not geometri.is_valid:
            geometri = geometri.buffer(0)
        iller.append((isim, geometri))
    return iller


def puanlari_hesapla(depremler: pd.DataFrame, geojson: dict, mesafe_km: int):
    """Her olayı merkez üssüne belirlenen km kadar yakın illerle ilişkilendirir.

    Aynı deprem birden çok ili etkileyebilecek konumda olduğundan birden çok
    il için sayılabilir. Bu bir yer hareketi / hasar tahmini DEĞİLDİR.
    """
    iller = illeri_hazirla(geojson)
    uzaklik_m = mesafe_km * 1000
    satirlar = []
    for olay in depremler.itertuples(index=False):
        buyukluk = float(olay.mag)
        agirlik = olay_puani(buyukluk)
        if agirlik == 0:
            continue
        merkez = Point(*DONUSTURUCU.transform(float(olay.longitude), float(olay.latitude)))
        x, y = merkez.x, merkez.y
        for il, sinir in iller:
            x_min, y_min, x_max, y_max = sinir.bounds
            if not (x_min - uzaklik_m <= x <= x_max + uzaklik_m and y_min - uzaklik_m <= y <= y_max + uzaklik_m):
                continue
            if sinir.distance(merkez) <= uzaklik_m:
                satirlar.append({
                    'İl': il,
                    'Tarih': olay.time,
                    'Büyüklük': buyukluk,
                    'Puan': agirlik,
                    'İl sınırına uzaklık (km)': round(sinir.distance(merkez) / 1000, 1),
                    'USGS Olay ID': str(getattr(olay, 'id', '')),
                    'Yer': str(getattr(olay, 'place', '')),
                })

    kolonlar = ['İl', 'Tarih', 'Büyüklük', 'Puan', 'İl sınırına uzaklık (km)', 'USGS Olay ID', 'Yer']
    eslesenler = pd.DataFrame(satirlar, columns=kolonlar)
    ozet = pd.DataFrame({'İl': [isim for isim, _ in iller]})
    if not eslesenler.empty:
        grup = eslesenler.groupby('İl').agg(
            **{'Deprem sayısı': ('Puan', 'size'), 'Toplam puan': ('Puan', 'sum'), 'En büyük deprem': ('Büyüklük', 'max')}
        ).reset_index()
        ozet = ozet.merge(grup, on='İl', how='left')
    else:
        ozet['Deprem sayısı'] = 0
        ozet['Toplam puan'] = 0
        ozet['En büyük deprem'] = float('nan')

    ozet['Deprem sayısı'] = ozet['Deprem sayısı'].fillna(0).astype(int)
    ozet['Toplam puan'] = ozet['Toplam puan'].fillna(0).astype(int)
    en_yuksek = int(ozet['Toplam puan'].max())
    # 0 eşleşme bir risk gözlemi değildir: "100/100 güvenli" gibi gösterilmez.
    # Pozitif puanlar kendi aralarında göreli olarak karşılaştırılabilir.
    if en_yuksek:
        ozet['Karşılaştırma endeksi'] = ozet['Toplam puan'].apply(
            lambda p: round(100 * (1 - math.log1p(int(p)) / math.log1p(en_yuksek)), 1)
            if p > 0 else float('nan')
        )
    else:
        ozet['Karşılaştırma endeksi'] = float('nan')

    ozet['Gözlem durumu'] = ozet['Deprem sayısı'].apply(
        lambda adet: 'Eşleşme var' if adet > 0 else 'Seçilen kapsamda eşleşme yok'
    )
    # Kayıt olmayan iller birinci sıraya yazılmaz; kendi gruplarında gösterilir.
    # Puanı aynı olan iller ortak sıralamaya sahiptir.
    # Asıl sıralama puana göre: önce kayıt olanlar, kendi içinde azdan çoğa.
    ozet = ozet.assign(_kayit_var=ozet['Deprem sayısı'].gt(0)).sort_values(
        ['_kayit_var', 'Toplam puan', 'İl'],
        ascending=[False, True, True],
    ).drop(columns=['_kayit_var']).reset_index(drop=True)
    sira = ozet['Toplam puan'].where(ozet['Deprem sayısı'].gt(0)).rank(method='min', ascending=True)
    ozet.insert(0, 'Sıra', sira.astype('Int64'))
    return ozet, eslesenler
