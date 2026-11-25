"""Afet Atlas v4.3 — tüm il poligonları tıklanabilen sabit Türkiye haritası.

Folium/Leaflet kullanır. Harita sürüklenmez, yakınlaşmaz; tıklama ili seçer.
Analiz verilerini veya ilin koordinatlarını değiştirmez.
"""
from __future__ import annotations

from functools import lru_cache
import math
from typing import Any

import folium
import pandas as pd
from plotly.colors import sample_colorscale
from shapely.geometry import mapping, shape

from atlas_harita import gosterge_paleti


@lru_cache(maxsize=1)
def _hafif_il_geometrileri() -> tuple[dict, ...]:
    """Tek defa hesaplanan basitleştirilmiş 81 il poligonu; orijinal veri korunur."""
    from veri import il_sinirlarini_getir
    sinirlar = il_sinirlarini_getir()
    features = sinirlar.get('features', [])
    if len(features) != 81:
        raise ValueError('Türkiye haritasında 81 il sınırı bekleniyor.')
    result = []
    for feat in features:
        geom = shape(feat['geometry']).simplify(0.013, preserve_topology=True)
        result.append({
            'type': 'Feature',
            'properties': {'il': feat['properties']['shapeName']},
            'geometry': mapping(geom),
        })
    return tuple(result)


def il_olayi(data: Any) -> str | None:
    """GeoJSON alan tıklamasını tooltip veya coğrafi koordinattan şehre çevirir."""
    if not isinstance(data, dict):
        return None
    # Streamlit-folium'un GeoJSON tıklamasındaki garantili olayı tooltip'tir.
    names = {feat['properties']['il'] for feat in _hafif_il_geometrileri()}
    tooltip = data.get('last_object_clicked_tooltip')
    if isinstance(tooltip, str):
        name = tooltip.strip()
        if name in names:
            return name
    # Bazı sürümlerde yalnızca tıklanan koordinat gelebilir.
    location = data.get('last_object_clicked')
    if isinstance(location, dict):
        lat, lng = location.get('lat'), location.get('lng')
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            from shapely.geometry import Point
            point = Point(float(lng), float(lat))
            for feat in _hafif_il_geometrileri():
                if shape(feat['geometry']).covers(point):
                    return feat['properties']['il']
    clicked = data.get('last_active_drawing')
    if isinstance(clicked, dict):
        prop = clicked.get('properties') or {}
        name = prop.get('il') if isinstance(prop, dict) else None
        if name in names:
            return name
    return None


def _value_string(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return '—'
    return f'{float(value):,.1f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def hazirla_harita(tablo: pd.DataFrame, deger: str, etiket: str, secili: str) -> folium.Map:
    """Her il için gerçek geometrinin tüm yüzeyini tıklanabilir yapar."""
    if not {'İl', deger}.issubset(tablo.columns):
        raise ValueError('Harita için İl ve gösterge sütunu gerekiyor.')
    data = tablo.drop_duplicates('İl').set_index('İl')
    values = pd.to_numeric(data[deger], errors='coerce')
    feats = _hafif_il_geometrileri()
    names = {x['properties']['il'] for x in feats}
    if names != set(data.index) or len(data) != 81:
        raise ValueError('Harita ile 81 il verisi eşleşmeli.')
    valid = values.dropna()
    low, high = (float(valid.min()), float(valid.max())) if not valid.empty else (0.0, 1.0)
    span = (high-low) or 1.0
    collection = {'type': 'FeatureCollection', 'features': []}
    for feat in feats:
        name = feat['properties']['il']
        val = values.get(name)
        norm = max(0.0, min(1.0, (float(val) - low) / span)) if pd.notna(val) else None
        color = sample_colorscale(gosterge_paleti(deger), [norm])[0] if norm is not None else '#263243'
        collection['features'].append({
            'type': 'Feature', 'geometry': feat['geometry'],
            'properties': {
                'il': name,
                'deger': _value_string(val),
                'dolgu': color,
                'secili': bool(name == secili),
            },
        })

    m = folium.Map(
        location=(39.0, 35.2), zoom_start=5, tiles=None,
        zoom_control=False, dragging=False, scroll_wheel_zoom=False,
        double_click_zoom=False, touch_zoom=False, box_zoom=False,
        keyboard=False, attribution_control=False, prefer_canvas=True,
        max_bounds=True,
    )
    m.get_root().header.add_child(folium.Element('''<style>
      .leaflet-container{background:#0c1a2e!important;cursor:default!important;}
      .leaflet-interactive{cursor:pointer!important;}
      .leaflet-tooltip{background:#142a40;color:#eafbf7;border:1px solid #3d6e7d;
        font:12px sans-serif;border-radius:8px;}
      .leaflet-tooltip::before{border-top-color:#3d6e7d!important;}
    </style>'''))
    folium.GeoJson(
        collection,
        name='İller',
        style_function=lambda feat: {
            'fillColor': feat['properties']['dolgu'],
            'color': '#b8f8eb' if feat['properties']['secili'] else '#14253b',
            'weight': 2.8 if feat['properties']['secili'] else 0.9,
            'fillOpacity': 0.95,
            'opacity': 1,
        },
        highlight_function=lambda feat: {
            'color': '#fafcff', 'weight': 2.2, 'fillOpacity': 1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['il'], labels=False,
            sticky=True,
        ),
        smooth_factor=1,
    ).add_to(m)
    # Görüntünün yalnızca ilk açılıştaki kadrajını ayarlar; kullanıcı hareket ettiremez.
    m.fit_bounds([[35.6, 25.4], [42.4, 45.3]], padding=(8, 8))
    return m
