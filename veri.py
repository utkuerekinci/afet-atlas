"""Gerçek ve kamuya açık deprem / Türkiye il sınırı verilerini indirir."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import io
import json
import time

import pandas as pd
import requests

VERI_KLASORU = Path(__file__).resolve().parent / 'indirilen_veriler'
USGS_URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
SINIR_API = 'https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/'


def _indir(url: str, params: dict | None = None) -> requests.Response:
    yanit = requests.get(
        url,
        params=params,
        timeout=90,
        headers={'User-Agent': 'BBY261-Akademik-Deprem-Prototipi/1.0'},
    )
    yanit.raise_for_status()
    return yanit


def il_sinirlarini_getir() -> dict:
    """geoBoundaries kaynağından 81 ilin GeoJSON sınırlarını edinir."""
    VERI_KLASORU.mkdir(exist_ok=True)
    hedef = VERI_KLASORU / 'turkiye_81_il.geojson'
    if hedef.exists():
        return json.loads(hedef.read_text(encoding='utf-8'))

    metadata = _indir(SINIR_API).json()
    # Türkiye ADM1 veri katmanının gerçek 81 il içerdiğini doğrula.
    if int(metadata.get('admUnitCount', 0)) != 81:
        raise ValueError('İl sınırı kaynağında 81 il doğrulanamadı.')
    konum = metadata.get('simplifiedGeometryGeoJSON') or metadata.get('gjDownloadURL')
    if not konum:
        raise ValueError('geoBoundaries verisi için GeoJSON indirme adresi yok.')
    veri = _indir(konum).json()
    if len(veri.get('features', [])) != 81:
        raise ValueError('İndirilen GeoJSON dosyasında 81 il bulunamadı.')
    for ozellik in veri['features']:
        if not ozellik.get('properties', {}).get('shapeName'):
            raise ValueError('GeoJSON içindeki bazı illerin adı bulunmuyor.')
    hedef.write_text(json.dumps(veri, ensure_ascii=False), encoding='utf-8')
    return veri


def _yil_icin_getir(yil: int, minimum: float) -> pd.DataFrame:
    """USGS kayıtlarını yıla göre bölerek 20.000 kayıt sınırını aşmaz."""
    VERI_KLASORU.mkdir(exist_ok=True)
    hedef = VERI_KLASORU / f'usgs_{yil}_m{str(minimum).replace(".", "_")}.csv'
    # Önceki yılların verisini koru; içinde bulunduğumuz yılı 6 saatte bir yenile.
    guncel = hedef.exists() and (yil < date.today().year or time.time() - hedef.stat().st_mtime < 6 * 3600)
    if guncel:
        return pd.read_csv(hedef)

    parametreler = {
        'format': 'csv',
        'starttime': f'{yil}-01-01',
        'endtime': f'{yil + 1}-01-01' if yil < date.today().year else date.today().isoformat(),
        'minmagnitude': minimum,
        'minlatitude': 34.0,
        'maxlatitude': 43.5,
        'minlongitude': 24.0,
        'maxlongitude': 46.0,
        'eventtype': 'earthquake',
        'orderby': 'time-asc',
    }
    yanit = _indir(USGS_URL, params=parametreler)
    try:
        sonuc = pd.read_csv(io.StringIO(yanit.text))
    except pd.errors.EmptyDataError:
        sonuc = pd.DataFrame(columns=['id', 'time', 'latitude', 'longitude', 'mag', 'depth', 'place', 'type'])
    if 'mag' not in sonuc.columns or 'latitude' not in sonuc.columns or 'longitude' not in sonuc.columns:
        raise ValueError('USGS verisinin beklenen sütunları bulunamadı. Veri formatı değişmiş olabilir.')
    sonuc.to_csv(hedef, index=False)
    return sonuc


def depremleri_getir(baslangic: int, bitis: int, minimum: float) -> pd.DataFrame:
    """Veriler USGS'den alınır. Hata varsa uydurma veri gösterilmez."""
    if baslangic > bitis:
        raise ValueError('Başlangıç yılı bitiş yılından sonra olamaz.')
    parcalar = [_yil_icin_getir(yil, minimum) for yil in range(baslangic, bitis + 1)]
    tablo = pd.concat(parcalar, ignore_index=True)
    tablo['mag'] = pd.to_numeric(tablo['mag'], errors='coerce')
    tablo['latitude'] = pd.to_numeric(tablo['latitude'], errors='coerce')
    tablo['longitude'] = pd.to_numeric(tablo['longitude'], errors='coerce')
    tablo['time'] = pd.to_datetime(tablo['time'], errors='coerce', utc=True)
    tablo = tablo.dropna(subset=['mag', 'latitude', 'longitude', 'time'])
    if 'id' in tablo.columns:
        tablo = tablo.drop_duplicates('id')
    if 'type' in tablo.columns:
        tablo = tablo[tablo['type'].fillna('earthquake') == 'earthquake']
    return tablo.reset_index(drop=True)
