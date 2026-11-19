"""Gerçek 2025 kayıtlarını kullanarak hızlı doğrulama (pytest veya doğrudan Python)."""
from pathlib import Path
import json

import pandas as pd

from hesaplama import olay_puani, puanlari_hesapla

KOK = Path(__file__).resolve().parent


def test_puan_araliklari():
    assert [olay_puani(m) for m in [4.49, 4.5, 4.99, 5.0, 5.99, 6.0, 6.99, 7.0, 7.8]] == [0, 1, 1, 3, 3, 5, 5, 7, 7]


def test_gercek_veri_ve_il_eslesmeleri():
    csv = pd.read_csv(KOK / 'indirilen_veriler' / 'usgs_2025_m4_5.csv')
    geojson = json.loads((KOK / 'indirilen_veriler' / 'turkiye_81_il.geojson').read_text(encoding='utf-8'))
    assert len(csv) == 159
    assert len(csv['id'].unique()) == 159
    assert len(geojson['features']) == 81
    assert float(csv['mag'].max()) == 6.2

    sonuc, eslesme = puanlari_hesapla(csv, geojson, 0)
    assert len(sonuc) == 81
    assert len(eslesme) == 33
    assert eslesme['USGS Olay ID'].nunique() == 33
    assert (eslesme['İl sınırına uzaklık (km)'] == 0).all()
    assert (eslesme['Puan'] == eslesme['Büyüklük'].apply(olay_puani)).all()
    assert int(eslesme['Puan'].sum()) == int(sonuc['Toplam puan'].sum())
    assert 0 in sonuc['Toplam puan'].values
    sifirlar = sonuc[sonuc['Deprem sayısı'] == 0]
    kayitlilar = sonuc[sonuc['Deprem sayısı'] > 0]
    assert len(sifirlar) == 72
    assert sifirlar['Karşılaştırma endeksi'].isna().all()
    assert sifirlar['Sıra'].isna().all()
    assert kayitlilar['Karşılaştırma endeksi'].notna().all()
    assert kayitlilar['Sıra'].notna().all()
    assert list(kayitlilar['Toplam puan']) == sorted(kayitlilar['Toplam puan'].tolist())
    assert set(sonuc['Gözlem durumu'].unique()) == {'Eşleşme var', 'Seçilen kapsamda eşleşme yok'}
    assert 'Balıkesir' in sonuc['İl'].values

    # Daha önce indirilen eşleşme dosyası ile yeniden hesaplanan kayıt kimliklerini
    # ve illerini bağımsız şekilde karşılaştır.
    onceki = KOK / 'test_referans_2025_eslesmeler.csv'
    if onceki.exists():
        eski = pd.read_csv(onceki, encoding='utf-8-sig')
        beklenen = set(zip(eski['USGS Olay ID'], eski['İl']))
        hesaplanan = set(zip(eslesme['USGS Olay ID'], eslesme['İl']))
        assert beklenen == hesaplanan

    # Kullanıcının istediği beş mesafenin hepsi çalışmalı; km arttıkça eşleşmeler azalmamalı.
    onceki_sayi = 0
    for km in [0, 50, 75, 100, 150]:
        iller, olaylar = puanlari_hesapla(csv, geojson, km)
        assert len(iller) == 81
        assert len(olaylar) >= onceki_sayi
        onceki_sayi = len(olaylar)
        assert olaylar['Puan'].isin([1, 3, 5, 7]).all()


if __name__ == '__main__':
    test_puan_araliklari()
    test_gercek_veri_ve_il_eslesmeleri()
    print('BAŞARILI: 2025 gerçek verileri, 81 il, 33 temel eşleşme, 1/3/5/7, 5 yakınlık ve sıfır eşleşme gösterimi kontrol edildi.')
