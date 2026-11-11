"""Afet Atlas: internet haritası/Plotly Geo tabanı gerektirmeyen il haritası.

İl geometrileri gerçek geoBoundaries GeoJSON dosyasından gelir. Bu modül
sadece grafik çizer, deprem eşleştirme ve puan hesaplamalarını değiştirmez.
"""
from __future__ import annotations

from math import cos, radians

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from shapely.geometry import shape


RENKLER = [
    [0, "#1c3650"],
    [0.17, "#2d6079"],
    [0.42, "#559a99"],
    [0.72, "#efa16c"],
    [1, "#e87863"],
]


def turkiye_haritasi(sinirlar: dict, sonuc: pd.DataFrame) -> go.Figure:
    """81 il için etkileşimli, dış harita servisine ihtiyaç duymayan görsel.

    İl koordinatlarını ekrana aktarırken sabit enlem düzeltmesi uygulanır.
    Bu çizim projeksiyonu coğrafi mesafe/eşleştirme hesabında KULLANILMAZ.
    """
    gerekli = {"İl", "Deprem sayısı", "Toplam puan", "Karşılaştırma endeksi"}
    if not gerekli.issubset(sonuc.columns):
        raise ValueError(f"Harita veri tablosunda eksik sütun: {gerekli - set(sonuc.columns)}")
    oz = {str(k["İl"]): k for _, k in sonuc.iterrows()}
    ozellikler = sinirlar.get("features", [])
    if not ozellikler:
        raise ValueError("İl sınırı GeoJSON dosyasında çizilecek geometri yok.")
    adlar = {f["properties"]["shapeName"] for f in ozellikler}
    if adlar != set(oz):
        raise ValueError(f"İl isimleri eşleşmiyor: {sorted(adlar ^ set(oz))}")

    fig = go.Figure()
    en_yuksek = max(float(sonuc["Toplam puan"].max()), 1.0)
    # Koordinatları sadece grafik için yaklaşık eş ölçekte göster.
    boylam_carpani = cos(radians(39.0))
    for feature in ozellikler:
        il = feature["properties"]["shapeName"]
        satir = oz[il]
        puan = float(satir["Toplam puan"])
        n = int(satir["Deprem sayısı"])
        endeks = satir["Karşılaştırma endeksi"]
        endeks_yazisi = f"{float(endeks):.1f}/100" if pd.notna(endeks) else "Hesaplanmadı"
        renk = sample_colorscale(RENKLER, [min(max(puan / en_yuksek, 0.0), 1.0)])[0]
        geo = shape(feature["geometry"]).simplify(0.006, preserve_topology=True)
        parcalar = [geo] if geo.geom_type == "Polygon" else list(geo.geoms)
        x, y = [], []
        for parca in parcalar:
            if parca.is_empty:
                continue
            x.extend(koor[0] * boylam_carpani for koor in parca.exterior.coords)
            y.extend(koor[1] for koor in parca.exterior.coords)
            # Plotly fill="toself" ayrı parçaları NaN boşluğunda ayrı ayrı kapatır.
            x.append(None)
            y.append(None)
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", fill="toself", hoveron="fills",
            name=il, showlegend=False,
            line=dict(color="#0b1627", width=0.8),
            fillcolor=renk,
            hovertemplate=(f"<b>{il}</b><br>Olay puanı: {puan:g}"
                           f"<br>Eşleşen deprem: {n}"
                           f"<br>Göreli endeks: {endeks_yazisi}<extra></extra>"),
        ))

    # Görünür noktası olmayan ek iz yalnızca mevcut renk ölçeği lejandını çizer.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", hoverinfo="skip", showlegend=False,
        marker=dict(size=0.01, color=[0], cmin=0, cmax=en_yuksek,
                    colorscale=RENKLER, showscale=True,
                    colorbar=dict(title=dict(text="PUAN", font=dict(size=10, color="#b8ccdd")),
                                  len=0.62, thickness=11, x=1.02,
                                  tickfont=dict(color="#b8ccdd", size=10),
                                  outlinewidth=0, bgcolor="rgba(0,0,0,0)"))
    ))
    fig.update_layout(
        height=470,
        margin=dict(l=4, r=18, t=8, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d9e7f5", family="DM Sans"),
        xaxis=dict(visible=False, constrain="domain"),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        dragmode="pan",
        hoverlabel=dict(bgcolor="#142c44", font=dict(color="#f4f8ff", size=13)),
    )
    return fig
