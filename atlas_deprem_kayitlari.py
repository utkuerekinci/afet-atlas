"""Afet Atlas: seçilen ile ait USGS kayıtları için saf tablo hazırlayıcıları."""
from __future__ import annotations
import pandas as pd

KAYIT_SUTUNLARI = ['Tarih','Büyüklük','Yer','İl sınırına uzaklık (km)','Puan']

def secilen_il_kayitlari(eslesenler: pd.DataFrame, il: str) -> pd.DataFrame:
    """Yalnızca seçilen ilin eşleşmiş depremleri; en yeni olay ilk sırada."""
    if not {'İl',*KAYIT_SUTUNLARI}.issubset(eslesenler.columns):
        raise ValueError('İl kayıtları için gerekli sütunlar eksik.')
    df=eslesenler.loc[eslesenler['İl'].eq(il),KAYIT_SUTUNLARI].copy()
    if not df.empty:
        df=df.sort_values('Tarih',ascending=False,kind='stable')
    return df.reset_index(drop=True)

def hareketliligi_yuksek_bes_il(display: pd.DataFrame) -> pd.DataFrame:
    """İl panelindeki birincil tablo yerine alt sekmede ülke karşılaştırması."""
    required=['İl','Toplam puan','Deprem sayısı','Karşılaştırma endeksi']
    if not set(required).issubset(display.columns):
        raise ValueError('Ülke karşılaştırma sütunları eksik.')
    return display.loc[display['Deprem sayısı'].gt(0),required].sort_values(['Toplam puan','İl'],ascending=[False,True]).head(5).reset_index(drop=True)
