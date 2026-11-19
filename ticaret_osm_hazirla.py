"""Geofabrik .osm.pbf + gerçek 973 ilçe sınırlarından OSM özetini hazırla.

KULLANIM:
  pip install osmium
  python ticaret_osm_hazirla.py --pbf turkey-latest.osm.pbf --geojson ilce_sinir_osm.geojson

Coğrafi analiz geliştirici bilgisayarında BİR KEZ çalıştırılır. Kullanıcı uygulamasına
600+ MB ham PBF koymayın; oluşan küçük CSV + manifesti koyun.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json
from pathlib import Path
from shapely.geometry import shape,Point
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree
from ticaret_veri import DATA,OSM_CSV,OSM_META,OSM_SUTUNLAR,canonical_key
from ilce_veri import read_population_bytes, POP_LOCAL

GEOFABRIK='https://download.geofabrik.de/europe/turkey-latest.osm.pbf'
BOUNDARIES='https://rodostoteknoloji.com/online-tools/turkey-boundaries.html'  # GeoJSON kullanıcının alternatif kaynağından


def classify(tags:dict)->set[str]:
    if tags.get('disused')=='yes' or tags.get('abandoned')=='yes' or tags.get('construction')=='yes' or tags.get('demolished')=='yes':
        return set()
    if tags.get('disused:amenity') or tags.get('disused:shop') or tags.get('abandoned:shop'):return set()
    a,s,o=tags.get('amenity',''),tags.get('shop',''),tags.get('office','')
    result=set()
    if a in {'restaurant','cafe','fast_food','bar','pub','food_court','ice_cream','biergarten'}:
        result.add('osm_yeme_icme')
    if s and s not in {'vacant','no','closed'}:
        result.add('osm_market_perakende')
    if a in {'bank','pharmacy','clinic','doctors','dentist','veterinary','car_wash','car_rental','post_office'} or o in {'lawyer','accountant','insurance','estate_agent','travel_agent','company','consulting'} or tags.get('craft') in {'hairdresser','tailor','shoemaker'} or s in {'hairdresser','beauty','laundry','dry_cleaning'}:
        result.add('osm_hizmetler')
    if o in {'logistics','freight','transport'} or tags.get('industrial') in {'warehouse','logistics'}:
        result.add('osm_lojistik')
    if tags.get('highway')=='bus_stop' or a in {'bus_station','ferry_terminal'} or tags.get('railway') in {'station','halt','tram_stop','subway_entrance'} or tags.get('public_transport') in {'stop_position','station','platform'}:
        result.add('osm_ulasim')
    return result


def _property(properties,keys):
    for key in keys:
        if properties.get(key) is not None:return str(properties[key])
    return None


def load_boundaries(filepath:Path):
    payload=json.loads(filepath.read_text(encoding='utf-8'))
    polygons=[]; keys=[]
    for f in payload.get('features',[]):
        pr=f.get('properties') or {}
        il=_property(pr,('il','il_adi','ilAdi','province','province_name','ADM1_TR','NAME_1'))
        ilce=_property(pr,('ilce','ilce_adi','ilceAdi','district','district_name','ADM2_TR','NAME_2'))
        if not il or not ilce:raise ValueError('Sınır dosyasında il/ilçe adı bulunamadı. Anahtarlar: '+repr(list(pr)))
        geo=shape(f['geometry'])
        if geo.is_empty or not geo.is_valid:raise ValueError(il+'/'+ilce+' sınırı geçersiz.')
        polygons.append(geo);keys.append(canonical_key(il,ilce))
    if len(polygons)!=973 or len(set(keys))!=973:
        raise ValueError(f'Sınır verisi 973 tekil ilçe içermeli, bulunan {len(polygons)}; tekil {len(set(keys))}.')
    return polygons,keys


def build_spatial_index(polygons,keys):
    tree=STRtree(polygons)
    return tree,keys


def aggregate_points(points,polygons,keys):
    """Test edilebilir saf toplama fonksiyonu: (enlem, boylam, etiketler) akışı."""
    tree,_=build_spatial_index(polygons,keys)
    counts=defaultdict(Counter)
    seen=set()
    for lat,lon,tags,osm_id in points:
        if osm_id in seen:continue
        seen.add(osm_id)
        categories=classify(tags)
        if not categories:continue
        p=Point(lon,lat)
        matches=[int(i) for i in tree.query(p,predicate='within')]
        if len(matches)!=1:continue  # sınırda/boşlukta belirsizliği sayma
        k=keys[matches[0]]
        for col in categories: counts[k][col]+=1
    return counts


def iter_pbf(path:Path, consume):
    """PBF'yi akış halinde işle; milyonlarca OSM nesnesini belleğe toplama."""
    try:import osmium
    except ImportError as e:raise RuntimeError('PBF için pip install osmium komutunu çalıştır.') from e
    from shapely import wkb
    class Reader(osmium.SimpleHandler):
        def __init__(self):super().__init__();self.factory=osmium.geom.WKBFactory()
        def node(self,o):
            tags=dict(o.tags)
            if classify(tags) and o.location.valid():
                consume(o.location.lat,o.location.lon,tags,'n'+str(o.id))
        def area(self,o):
            tags=dict(o.tags)
            if not classify(tags):return
            try:
                geom=wkb.loads(self.factory.create_multipolygon(o), hex=True)
                p=geom.representative_point()
                consume(p.y,p.x,tags,'a'+str(o.id))
            except (RuntimeError,ValueError):return
    reader=Reader()
    reader.apply_file(str(path),locations=True)


def produce(pbf:Path, boundaries:Path):
    if not pbf.is_file():raise FileNotFoundError('PBF bulunamadı: '+str(pbf))
    if not boundaries.is_file():raise FileNotFoundError('GeoJSON bulunamadı: '+str(boundaries))
    polygons,keys=load_boundaries(boundaries)
    population=read_population_bytes(POP_LOCAL.read_bytes())
    expected={canonical_key(row.il,row.ilce) for row in population.itertuples(index=False)}
    if set(keys)!=expected:
        raise ValueError(f'Sınırlar nüfusla uyuşmadı: eksik {sorted(expected-set(keys))[:15]}; fazla {sorted(set(keys)-expected)[:15]}')
    tree,_=build_spatial_index(polygons,keys)
    counts=defaultdict(Counter)
    def consume(lat,lon,tags,osm_id):
        categories=classify(tags)
        if not categories:return
        point=Point(lon,lat)
        hit=[int(i) for i in tree.query(point,predicate='within')]
        if len(hit)!=1:return
        for col in categories:counts[keys[hit[0]]][col]+=1
    iter_pbf(pbf,consume)
    if not counts:raise ValueError('PBF içinde hiç eşleşen ticari/ulaşım noktası bulunamadı; sahte 0 kaydı yazılmaz.')
    key_to_province={canonical_key(r.il,r.ilce):r.il for r in population.itertuples(index=False)}
    provinces_with_poi={key_to_province[k] for k,v in counts.items() if sum(v.values())>0}
    if len(provinces_with_poi)!=81:
        raise ValueError(f'81 ilin tamamında bir OSM kaydı bulunmadı ({len(provinces_with_poi)}/81). Eksik/yanlış PBF olabilir; dışa aktarım reddedildi.')
    key_to_display={canonical_key(r.il,r.ilce):(r.il,r.ilce) for r in population.itertuples(index=False)}
    rows=[]
    for key in keys:
        il,ilce=key_to_display[key]
        rows.append({'il':il,'ilce':ilce,**{c:counts[key][c] for c in OSM_SUTUNLAR}})
    from io import StringIO
    import pandas as pd
    tmp=OSM_CSV.with_suffix('.csv.tmp')
    pd.DataFrame(rows).to_csv(tmp,index=False,encoding='utf-8-sig')
    # OSM tarihini PBF basename'den varsaymıyoruz; kullanıcının veri dosyası zamanını belirtiyoruz.
    manifest={'kaynak':'OpenStreetMap / Geofabrik','olcek':'Türkiye 973 ilçe',
              'osm_veri_tarihi':'PBF üstverisi bu betikte doğrulanmadı; Geofabrik indirme sayfasından kontrol edin',
              'pbf_dosya_son_degistirilme_tarihi':datetime.fromtimestamp(pbf.stat().st_mtime,timezone.utc).date().isoformat(),
              'olusturma_tarihi':datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'osm_indirme_adresi':GEOFABRIK,'sinir_kaynagi':BOUNDARIES,
              'not':'OSM gönüllü kayıtlarıdır; nokta sayısı resmî işyeri, müşteri ya da yaya sayısı değildir. Bölgeler arası kapsama farklıdır.',
              'kapsam_ozet':'973 ilçenin poligonunun tamamı analiz edildi; sıfırlar OSM etiketli unsur bulunmadığı anlamındadır, hiç işletme yok demek değildir.'}
    OSMM=OSM_META.with_suffix('.json.tmp')
    OSMM.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(OSM_CSV);OSMM.replace(OSM_META)
    return len(rows),sum(sum(row[c] for c in OSM_SUTUNLAR) for row in rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Afet Atlas OSM ilçe verisi üretici')
    p.add_argument('--pbf',type=Path,required=True,help='Geofabrik Turkey OSM PBF dosyası')
    p.add_argument('--geojson',type=Path,required=True,help='973 ilçelik ilçe sınırları GeoJSON')
    a=p.parse_args()
    n,total=produce(a.pbf,a.geojson)
    print(f'{n} ilçelik tablo yazıldı. OSM sektörel etiket toplamı (kategori örtüşmesi olabilir): {total}')
