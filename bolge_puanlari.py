"""Afet Atlas'ın AÇIKÇA TANIMLANMIŞ keşif endeksleri.

Bunlar resmî yaşam kalitesi, ticaret kârı veya güvenlik oranı değildir.
Sadece gerçek kayıtlardan hesaplanan girdilere göre, seçilen il içindeki
ilçelerin göreli sırasını göstermek üzere tasarlanmış proje modelidir.
"""
from __future__ import annotations

import pandas as pd

# Plan ağırlıkları (model varsayımıdır, ampirik olarak kalibre edilmedi).
# Yerel kiralar ulusal 973/973 gözlemi olmadan ortak sıralamada kullanılmaz.
SEKTOR_AGIRLIKLARI = {
    "Yeme-içme": {"nufus": .30, "yogunluk": .10, "sege": .15,
                  "isletme_kumesi": .10, "rekabet_baskisi": .15, "ulasim": .10, "kira": .10},
    "Market / perakende": {"nufus": .35, "yogunluk": .10, "sege": .10,
                           "isletme_kumesi": .10, "rekabet_baskisi": .15, "ulasim": .10, "kira": .10},
    "Hizmetler": {"nufus": .20, "yogunluk": .10, "sege": .20,
                  "isletme_kumesi": .10, "rekabet_baskisi": .15, "ulasim": .15, "kira": .10},
    "Lojistik / depolama": {"nufus": .15, "dusuk_yogunluk": .25, "sege": .10,
                            "isletme_kumesi": .15, "rekabet_baskisi": .10, "kira": .25},
}

# 'rekabet_baskisi' düşük sektörel işletme sayısı / yerleşik nüfus oranını
# pozitif sayar; bir ilçenin gerçekten az rakibe sahip olduğu iddia edilmez.
# 'isletme_kumesi' daha çok OSM kaydı olan merkezleri pozitif talep sinyali sayar.


def _sirala(series: pd.Series, reverse: bool = False) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() <= 1 or numeric.dropna().nunique() <= 1:
        return pd.Series(50.0, index=series.index).where(numeric.notna())
    pct = numeric.rank(pct=True, method="average", ascending=not reverse)
    return ((pct - 1 / numeric.notna().sum()) / (1 - 1 / numeric.notna().sum()) * 100).clip(0,100)


def ticari_gosterge_puanlari(data:pd.DataFrame, sektor:str)->dict[str,pd.Series]:
    import numpy as np
    from ticaret_veri import SEKTOR_SUTUNLARI
    metrics={"nufus":_sirala(data['nufus'])}
    if ('nufus_yogunlugu_km2' in data and
        pd.to_numeric(data['nufus_yogunlugu_km2'],errors='coerce').notna().all()):
        metrics['yogunluk']=_sirala(data['nufus_yogunlugu_km2'])
        metrics['dusuk_yogunluk']=_sirala(data['nufus_yogunlugu_km2'],reverse=True)
    if 'sege_sira' in data and pd.to_numeric(data['sege_sira'],errors='coerce').notna().all():
        metrics['sege']=_sirala(data['sege_sira'],reverse=True)
    col=SEKTOR_SUTUNLARI[sektor]
    if col in data and pd.to_numeric(data[col],errors='coerce').notna().all():
        competitors=pd.to_numeric(data[col],errors='raise')
        # OSM eksiksiz işletme envanteri değildir. Çok seyrek etiketlerde
        # "0 kayıt = az rekabet" yorumunu sıralama avantajına dönüştürmeyelim.
        # Bu %20 kuralı istatistiksel eşik değil; açıkça belirtilen proje
        # veri-kapsam korumasıdır. Ham kayıtlar tabloda görünmeye devam eder.
        positive=int((competitors>0).sum())
        threshold=max(3,int(np.ceil(.20*len(data))))
        if positive>=threshold:
            pop=pd.to_numeric(data.nufus,errors='raise')
            metrics['isletme_kumesi']=_sirala(np.log1p(competitors))
            # 50 bin nüfusluk dayanak ufak kırsal ilçelerde oransal patlamayı yumuşatır.
            pressure=competitors/(pop/10000.0+5.0)
            metrics['rekabet_baskisi']=_sirala(pressure,reverse=True)
    if sektor != 'Lojistik / depolama' and 'osm_ulasim' in data and pd.to_numeric(data.osm_ulasim,errors='coerce').notna().all():
        metrics['ulasim']=_sirala(np.log1p(pd.to_numeric(data.osm_ulasim)))
    if ('kira_m2_tl' in data and 'kira_ulusal_tam' in data and
        data.kira_ulusal_tam.eq(True).all() and
        pd.to_numeric(data.kira_m2_tl,errors='coerce').notna().all()):
        metrics['kira']=_sirala(np.log1p(data.kira_m2_tl),reverse=True)
    return metrics


def ticari_on_endeks(ilceler: pd.DataFrame, sektor: str) -> tuple[pd.DataFrame, dict]:
    """Sektör puanı = ölçülmüş gösterge sıralarının ağırlıklı ortalaması.

    Eksik veri 0 olarak kodlanmaz; hangi ağırlıkların etkin olduğu açıklanır.
    OSM işletme sayıları resmî işyeri sicili, ulaşım durakları yaya akışı değildir.
    """
    if sektor not in SEKTOR_AGIRLIKLARI:raise ValueError('Tanımsız sektör')
    if 'nufus' not in ilceler or ilceler.empty:raise ValueError('Gerçek nüfus kaydı gerekli')
    data=ilceler.copy()
    metrics=ticari_gosterge_puanlari(data,sektor)
    available={k:v for k,v in SEKTOR_AGIRLIKLARI[sektor].items() if k in metrics}
    weight_sum=sum(available.values())
    weights={k:v/weight_sum for k,v in available.items()}
    score=sum(metrics[k]*weight for k,weight in weights.items())
    data['Fırsat puanı']=score.round(1)
    for k,w in weights.items():
        # Sıralama katmanında hesaplanan katkıları ayrıca kaydet; neden-birinci
        # bileşeni aynı sayıları tekrar başka normalizasyonla hesaplamasın.
        data['Katkı: '+k]=(metrics[k]*w).round(2)
    sorts=[x for x in ('Fırsat puanı','nufus','il','ilce') if x in data]
    data=data.sort_values(sorts,ascending=[x in ('il','ilce') for x in sorts])
    return data,{'sektor':sektor,'agirliklar':weights,'kullanilan':list(available),
                 'kullanilamayan':[k for k in SEKTOR_AGIRLIKLARI[sektor] if k not in available],
                 'osm_aktif': 'isletme_kumesi' in available,
                 'kira_puana_dahil':'kira' in available}


def yasam_tercih_endeksi(ilceler: pd.DataFrame, tercih: str) -> pd.DataFrame:
    """Yerleşim karakterini sosyoekonomik gelişmişlik ve ulaşım profiliyle birlikte değerlendirir.

    SEGE-2022, eğitim/sağlık/yaşam kalitesi dahil 56 değişkenli bileşik
    çalışmadır. Bu alanların ayrı ayrı ilçe puanı varmış gibi davranılmaz.
    """
    import numpy as np
    if tercih not in {"Daha sakin", "Dengeli", "Daha hareketli"}:
        raise ValueError("Tanımsız yaşam tercihi")
    data = ilceler.copy()
    pop = _sirala(data['nufus']).fillna(50)
    if ('nufus_yogunlugu_km2' in data and
            pd.to_numeric(data['nufus_yogunlugu_km2'], errors='coerce').notna().all()):
        intensity = .5 * pop + .5 * _sirala(data['nufus_yogunlugu_km2'])
    else:
        intensity = pop
    if tercih == 'Daha sakin':
        lifestyle = 100 - intensity
    elif tercih == 'Daha hareketli':
        lifestyle = intensity
    else:
        lifestyle = 100 - (intensity - 50).abs() * 2
    components = {'yasam_ritmi': lifestyle.clip(0, 100)}
    base_weights = {'yasam_ritmi': .60, 'sege': .30, 'ulasim': .10}
    if ('sege_sira' in data and pd.to_numeric(data.sege_sira, errors='coerce').notna().all()):
        components['sege'] = _sirala(data.sege_sira, reverse=True)
    if ('osm_ulasim' in data and pd.to_numeric(data.osm_ulasim, errors='coerce').notna().all()):
        components['ulasim'] = _sirala(np.log1p(pd.to_numeric(data.osm_ulasim)))
    denominator = sum(base_weights[k] for k in components)
    weights = {k: base_weights[k] / denominator for k in components}
    score = sum(components[k] * weights[k] for k in components)
    for k, w in weights.items():
        data['Yaşam katkısı: ' + k] = (components[k] * w).round(3)
    data['Yaşam ritmi uyumu'] = components['yasam_ritmi'].round(2)
    data['Tercih uyumu'] = score.clip(0, 100).round(1)
    order=['Tercih uyumu', 'nufus'] + [k for k in ('il', 'ilce') if k in data]
    return data.sort_values(order, ascending=[False, False]+[True]*(len(order)-2))
