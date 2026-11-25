"""Türkiye'nin 81 il sınırına dayalı ortak, katmanlı, tıklanabilir harita.

Poligonlar geoBoundaries'den. İllerin temsil noktaları tıklama alanıdır;
coğrafi analizde bu çizim geometri dönüşümü kullanılmaz.
"""
from __future__ import annotations

from math import cos, radians
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from shapely.geometry import shape

PALET = [[0.0,"#20354c"],[0.24,"#277080"],[0.54,"#57a69b"],[0.77,"#f5bb79"],[1.0,"#ea7566"]]
# Nüfusta lacivertin koyu uçlarını açan özel geçiş. Diğer harita türleri orijinal paleti korur.
NUFUS_PALET = [[0.0,"#426885"],[0.24,"#4c93a6"],[0.54,"#78b9ac"],[0.77,"#f5bb79"],[1.0,"#ea7566"]]


def gosterge_paleti(gosterge: str):
    if 'güvenlik skoru' in str(gosterge).casefold():
        return [[0.0,'#db5964'],[0.28,'#ef9c72'],[0.54,'#f3c57a'],[0.74,'#68b9a9'],[1.0,'#257e9a']]
    return NUFUS_PALET if 'nüfus' in str(gosterge).casefold() else PALET


def katman_haritasi(sinirlar: dict, tablo: pd.DataFrame, deger: str,
                    etiket: str, secilen_il: str | None = None) -> go.Figure:
    """81 il için bir tek sayısal katman çizer; olmayan değerleri puan saymaz."""
    if not {'İl', deger}.issubset(tablo.columns):
        raise ValueError('Harita katmanı için İl ve değer sütunu gerekli.')
    rows = tablo.drop_duplicates('İl').set_index('İl')
    feats = sinirlar.get('features', [])
    adlar = [f['properties']['shapeName'] for f in feats]
    if len(feats) != 81 or set(adlar) != set(rows.index):
        raise ValueError('81 il ile harita değerlerinin birebir eşleşmesi gerekiyor.')
    values = pd.to_numeric(rows[deger], errors='coerce')
    finite = values.dropna()
    low, high = (float(finite.min()), float(finite.max())) if len(finite) else (0.0, 1.0)
    if high <= low: high = low + 1
    fig=go.Figure()
    scale_x=cos(radians(39))
    centers=[]
    for feat in feats:
        il=feat['properties']['shapeName']
        poly=shape(feat['geometry']).simplify(0.007, preserve_topology=True)
        parts=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
        x,y=[],[]
        for part in parts:
            if part.is_empty: continue
            x += [p[0]*scale_x for p in part.exterior.coords] + [None]
            y += [p[1] for p in part.exterior.coords] + [None]
        v=values.get(il, np.nan)
        fill='#263243' if pd.isna(v) else sample_colorscale(gosterge_paleti(deger),[max(0.,min(1.,(float(v)-low)/(high-low)))])[0]
        fig.add_trace(go.Scatter(x=x,y=y,mode='lines',fill='toself',name=il,showlegend=False,
            line=dict(width=1.5 if il==secilen_il else 0.65,color='#8df6e7' if il==secilen_il else '#101b2d'),
            fillcolor=fill,hoveron='fills',hovertemplate=f'<b>{il}</b><br>{etiket}: '+('Veri yok' if pd.isna(v) else f'{float(v):,.1f}')+'<extra></extra>'))
        point=poly.representative_point()
        centers.append((il, point.x*scale_x, point.y, v))
    # Seçim olayları poligon dolgularında kararsız olduğundan ayrıca nokta izleri kullanılır.
    fig.add_trace(go.Scatter(
        x=[p[1] for p in centers],y=[p[2] for p in centers],
        mode='markers',name='İl seçimi',showlegend=False,
        customdata=[[p[0]] for p in centers],
        marker=dict(size=[14 if p[0]==secilen_il else 10 for p in centers],
                    color=['#ffffff' if p[0]==secilen_il else '#d4f0ed' for p in centers],
                    opacity=.95,line=dict(color='#123043',width=1.4)),
        hovertemplate='<b>%{customdata[0]}</b><br>İli seçmek için tıklayın<extra></extra>',
        selected=dict(marker=dict(opacity=1)),unselected=dict(marker=dict(opacity=.65))
    ))
    fig.add_trace(go.Scatter(x=[None],y=[None],showlegend=False,mode='markers',hoverinfo='skip',
        marker=dict(color=[low],cmin=low,cmax=high,colorscale=gosterge_paleti(deger),showscale=True,
                    colorbar=dict(title=dict(text=etiket,font=dict(color='#c1d8de',size=10)),len=.56,
                                  thickness=10,x=1.01,outlinewidth=0,tickfont=dict(color='#cadce9')))))
    fig.update_layout(height=490,margin=dict(l=1,r=16,t=6,b=3),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False,constrain='domain'),
        yaxis=dict(visible=False,scaleanchor='x',scaleratio=1),
        clickmode='event+select',dragmode=False,
        hoverlabel=dict(bgcolor='#142840',font=dict(color='#f4fffc',size=13)))
    return fig


def secilen_nokta(event) -> str | None:
    """Streamlit plotly_chart(on_select='rerun') çıktısındaki ilin adı."""
    try:
        points=event.selection.points
        for p in points:
            cd=p.get('customdata',[])
            if cd and isinstance(cd[0],str):return cd[0]
    except (AttributeError, KeyError, TypeError):
        return None
    return None
