"""ADK bölgesel veri araçları. Aynı analiz motorunu hem UI hem ajan kullanır."""
from __future__ import annotations

import pandas as pd
from atlas_analiz import illere_ozet, neden_birinci as nedeni_hesapla, sirala_ilceler
from bolge_puanlari import SEKTOR_AGIRLIKLARI
from ilce_veri import normalize_name


def bolge_araclari_olustur(df: pd.DataFrame):
    """Doğrulanmış 973 ilçe tablosu yoksa araç açılmaz."""
    if df is None or len(df)!=973 or df.il.nunique()!=81:
        raise ValueError('Bölgesel ajan araçları için 973 ilçe / 81 il nüfusu gerekli.')
    rows=df.copy()
    cities=sorted(rows.il.unique())

    def _city(value:str):
        return next((x for x in cities if normalize_name(x)==normalize_name(value)), None)

    def il_nufus_ozeti(il_adi:str) -> dict:
        """Seçilen ilin 2025 TÜİK temelli toplam nüfusunu ve ilçe sayısını getirir.

        Args:
            il_adi: Türkiye ili (ör. Ankara, İstanbul).
        """
        city=_city(il_adi)
        if not city:return {'hata':'İl bulunamadı.'}
        subset=rows[rows.il==city]
        return {'il':city,'nufus_2025':int(subset.nufus.sum()),'ilce_sayisi':len(subset),
                'en_kalabalik_ilce':str(subset.loc[subset.nufus.idxmax()].ilce),'kaynak':'TÜİK ADNKS 2025 temelli ilçe CSV'}

    def ilce_bilgi(il_adi:str,ilce_adi:str) -> dict:
        """İlçe nüfusunu, yaklaşık yoğunluğunu ve varsa SEGE sırasını getirir.

        Args:
            il_adi: İl adı.
            ilce_adi: İlçe adı.
        """
        city=_city(il_adi)
        if not city:return {'hata':'İl bulunamadı.'}
        match=rows[(rows.il==city)&(rows.ilce.map(normalize_name)==normalize_name(ilce_adi))]
        if match.empty:return {'hata':'İlçe bulunamadı.'}
        r=match.iloc[0]
        out={'il':city,'ilce':str(r.ilce),'nufus_2025':int(r.nufus)}
        if pd.notna(r.get('nufus_yogunlugu_km2')):out['yaklasik_yogunluk_km2']=round(float(r.nufus_yogunlugu_km2),1)
        if 'sege_sira' in r and pd.notna(r.sege_sira):out['sege_turkiye_sirasi_2022']=int(r.sege_sira)
        return out

    def sektorel_ilce_siralamasi(kapsam:str, il_adi:str='Ankara', sektor:str='Yeme-içme', adet:int=5) -> dict:
        """Türkiye genelinde veya seçilen ilde sektörel model puanına göre en yüksek ilçeleri sıralar.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi sıralama yapılacak il.
            sektor: Yeme-içme, Market / perakende, Hizmetler, Lojistik / depolama.
            adet: 1-10 arası sonuç sayısı.
        """
        city=_city(il_adi)
        if kapsam not in ('Türkiye geneli','İl içi') or sektor not in SEKTOR_AGIRLIKLARI or not 1<=adet<=10:
            return {'hata':'Kapsam, sektör veya adet geçersiz.'}
        if kapsam=='İl içi' and city is None:return {'hata':'İl bulunamadı.'}
        ranked,meta=sirala_ilceler(rows,'ticaret',kapsam,city or 'Ankara',sektor)
        from ticaret_veri import SEKTOR_SUTUNLARI
        raw_col=SEKTOR_SUTUNLARI[sektor]
        return {'sektor':sektor,'kapsam':kapsam,'model_agirliklari':meta['agirliklar'],
                'osm_aktif':meta.get('osm_aktif',False),
                'osm_veri_durumu':'İlçe bazlı sektörel OSM kayıtları' if raw_col in rows else 'OSM özeti henüz yok',
                'ilk_ilceler':[{'sira':int(r['Sıra']),'il':r.il,'ilce':r.ilce,
                                'nufus':int(r.nufus),'puan':float(r['Fırsat puanı']),
                                **({'osm_sektor_kaydi':int(r[raw_col]),'osm_ulasim_kaydi':int(r.osm_ulasim)} if raw_col in rows else {})}
                               for _,r in ranked.head(adet).iterrows()],
                'yorum':'İlk ilçelerin yerleşik pazar, rekabet ve erişim dengelerini sektör bağlamında karşılaştırın.'}

    def neden_bu_ilce_birinci(kapsam:str, il_adi:str='Ankara',sektor:str='Yeme-içme') -> dict:
        """Birinci ilçenin neden birinci olduğunu; ağırlıklar, katkılar ve ikinci ilçe farkıyla açıklar.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi karşılaştırma ili.
            sektor: Desteklenen sektör adı.
        """
        if kapsam not in ('Türkiye geneli','İl içi') or sektor not in SEKTOR_AGIRLIKLARI:
            return {'hata':'Kapsam/sektör geçersiz.'}
        city=_city(il_adi)
        if kapsam=='İl içi' and city is None:return {'hata':'İl bulunamadı.'}
        ranked,meta=sirala_ilceler(rows,'ticaret',kapsam,city or 'Ankara',sektor)
        return nedeni_hesapla(ranked,meta)

    def yasam_tercihi_siralamasi(kapsam:str,il_adi:str='Ankara',tercih:str='Dengeli',adet:int=5) -> dict:
        """Sakin/dengeli/hareketli tercihine göre ilçe sıralaması üretir.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi sıralama ili.
            tercih: 'Dengeli', 'Daha sakin', 'Daha hareketli'.
            adet: 1-10 arası sonuç sayısı.
        """
        city=_city(il_adi)
        if kapsam not in ('Türkiye geneli','İl içi') or tercih not in ('Dengeli','Daha sakin','Daha hareketli') or not 1<=adet<=10:
            return {'hata':'Kapsam, tercih veya adet geçersiz.'}
        if kapsam=='İl içi' and city is None:return {'hata':'İl bulunamadı.'}
        ranked,meta=sirala_ilceler(rows,'yasam',kapsam,city or 'Ankara',tercih=tercih)
        return {'kapsam':kapsam,'tercih':tercih,'model':meta['model'],
                'ilk_ilceler':[{'sira':int(r['Sıra']),'il':r.il,'ilce':r.ilce,
                                'puan':float(r['Tercih uyumu'])} for _,r in ranked.head(adet).iterrows()]}

    def illeri_nufusa_gore_sirala(yon: str = 'En yüksek', adet: int = 10) -> dict:
        """2025 ilçe toplamlarından 81 ili nüfuslarına göre sıralar.

        Args:
            yon: 'En yüksek' veya 'En düşük'.
            adet: 1-20 arası il sayısı.
        """
        if yon not in ('En yüksek','En düşük') or not 1<=adet<=20:
            return {'hata':'Yön veya adet geçersiz.'}
        agg=rows.groupby('il',as_index=False).agg(nufus=('nufus','sum'),ilce_sayisi=('ilce','count'))
        agg=agg.sort_values(['nufus','il'],ascending=[yon=='En düşük',True])
        return {'yil':2025,'yon':yon,'ilk_iller':[{'il':str(x.il),'nufus':int(x.nufus),
                   'ilce_sayisi':int(x.ilce_sayisi)} for x in agg.head(adet).itertuples(index=False)],
                'kaynak':'2025 TÜİK ADNKS kaynaklı ilçe toplamları'}

    def iki_ili_nufusa_gore_karsilastir(il_1: str, il_2: str) -> dict:
        """İki ilin toplam nüfuslarını, nüfus farkını ve ilçe sayılarını kıyaslar.

        Args:
            il_1: Birinci il.
            il_2: İkinci il.
        """
        names=(_city(il_1),_city(il_2))
        if any(x is None for x in names):return {'hata':'İl adlarından biri bulunamadı.'}
        values=[rows.loc[rows.il==city,'nufus'] for city in names]
        totals=[int(x.sum()) for x in values]
        return {'birinci':{'il':names[0],'nufus':totals[0],'ilce_sayisi':len(values[0])},
                'ikinci':{'il':names[1],'nufus':totals[1],'ilce_sayisi':len(values[1])},
                'nufus_farki_birinci_eksi_ikinci':totals[0]-totals[1], 'yil':2025}

    def ilceleri_nufusa_gore_sirala(kapsam:str='Türkiye geneli',il_adi:str='Ankara',yon:str='En yüksek',adet:int=10) -> dict:
        """Türkiye geneli veya bir ilin ilçeleri için nüfus sıralaması verir.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi kapsam için il adı.
            yon: 'En yüksek' veya 'En düşük'.
            adet: 1-20 arası sonuç sayısı.
        """
        if kapsam not in ('Türkiye geneli','İl içi') or yon not in ('En yüksek','En düşük') or not 1<=adet<=20:
            return {'hata':'Kapsam, yön veya adet geçersiz.'}
        city=_city(il_adi)
        if kapsam=='İl içi' and city is None:return {'hata':'İl bulunamadı.'}
        data=rows if kapsam=='Türkiye geneli' else rows.loc[rows.il==city]
        data=data.sort_values(['nufus','il','ilce'],ascending=[yon=='En düşük',True,True])
        return {'kapsam':kapsam,'il':city if kapsam=='İl içi' else None,'yil':2025,
                'sonuclar':[{'il':str(r.il),'ilce':str(r.ilce),'nufus':int(r.nufus)}
                            for r in data.head(adet).itertuples(index=False)]}

    def iki_ilceyi_karsilastir(il_1:str, ilce_1:str, il_2:str, ilce_2:str,
                               sektor:str='Hizmetler') -> dict:
        """İki ilçenin nüfus, varsa SEGE ve aynı ulusal modelde ticaret puanını karşılaştırır.

        Args:
            il_1: İlk ilçenin ili.
            ilce_1: İlk ilçenin adı.
            il_2: İkinci ilçenin ili.
            ilce_2: İkinci ilçenin adı.
            sektor: Yeme-içme, Market / perakende, Hizmetler, Lojistik / depolama.
        """
        if sektor not in SEKTOR_AGIRLIKLARI:return {'hata':'Sektör desteklenmiyor.'}
        def district(prov,dist):
            name=_city(prov)
            if name is None:return None
            matches=rows[(rows.il==name)&(rows.ilce.map(normalize_name)==normalize_name(dist))]
            return None if matches.empty else matches.iloc[0]
        pair=[district(il_1,ilce_1),district(il_2,ilce_2)]
        if any(x is None for x in pair):return {'hata':'İl veya ilçe bulunamadı.'}
        ranked,meta=sirala_ilceler(rows,'ticaret','Türkiye geneli','Ankara',sektor)
        def describe(r):
            result=ranked[(ranked.il==r.il)&(ranked.ilce==r.ilce)].iloc[0]
            out={'il':str(r.il),'ilce':str(r.ilce),'nufus':int(r.nufus),
                 'ulusal_sira':int(result['Sıra']), 'ulusal_firsat_puani':round(float(result['Fırsat puanı']),2)}
            if 'sege_sira' in r.index and pd.notna(r['sege_sira']):out['sege_2022_ulusal_sira']=int(r['sege_sira'])
            from ticaret_veri import SEKTOR_SUTUNLARI
            if meta.get('osm_aktif'):
                out['osm_sektorel_kayit']=int(result[SEKTOR_SUTUNLARI[sektor]])
                out['osm_ulasim_kaydi']=int(result['osm_ulasim'])
            return out
        a,b=map(describe,pair)
        return {'sektor':sektor,'birinci':a,'ikinci':b,'puan_farki':round(a['ulusal_firsat_puani']-b['ulusal_firsat_puani'],2),
                'agirliklar':meta['agirliklar'],
                'yorum':'Sektörel fırsatı pazar büyüklüğü, ticari yapı ve erişim arasındaki ilişkiyle değerlendirin.'}

    def sektorlerin_birincilerini_karsilastir(kapsam:str='Türkiye geneli',il_adi:str='Ankara') -> dict:
        """Dört sektörde birinci gelen ilçeleri karşılaştırarak sektör seçiminin etkisini gösterir.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi kapsam için il adı.
        """
        city=_city(il_adi)
        if kapsam not in ('Türkiye geneli','İl içi') or (kapsam=='İl içi' and city is None):
            return {'hata':'Kapsam veya il bulunamadı.'}
        winners=[]
        used=[]
        for sector in SEKTOR_AGIRLIKLARI:
            rank,meta=sirala_ilceler(rows,'ticaret',kapsam,city or 'Ankara',sector)
            leader=rank.iloc[0]
            winners.append({'sektor':sector,'il':str(leader.il),'ilce':str(leader.ilce),
                            'firsat_puani':round(float(leader['Fırsat puanı']),2),
                            'kullanilan_gostergeler':list(meta['agirliklar'])})
            used.append(tuple(sorted(meta['agirliklar'])))
        return {'kapsam':kapsam,'il':city if kapsam=='İl içi' else None,'liderler':winners,
                'yorum':'Sektörlerin öncelikleri farklıdır; her lider ilçe için müşteri yapısı, rekabet ve yer seçimini ayrı yorumlayın.'}

    def yasamda_neden_bu_ilce_birinci(kapsam:str='Türkiye geneli',il_adi:str='Ankara',tercih:str='Dengeli') -> dict:
        """Yaşam tercihi sıralamasında birinci ve ikinci ilçenin açıklanabilir karşılaştırmasını verir.

        Args:
            kapsam: 'Türkiye geneli' veya 'İl içi'.
            il_adi: İl içi kapsamda il adı.
            tercih: 'Dengeli', 'Daha sakin' veya 'Daha hareketli'.
        """
        city=_city(il_adi)
        if kapsam not in ('Türkiye geneli','İl içi') or tercih not in ('Dengeli','Daha sakin','Daha hareketli') or (kapsam=='İl içi' and city is None):
            return {'hata':'Parametreler geçersiz.'}
        ranked,meta=sirala_ilceler(rows,'yasam',kapsam,city or 'Ankara',tercih=tercih)
        return nedeni_hesapla(ranked,meta)

    def sege_en_gelismis_ilceler(adet:int=10, il_adi:str='Türkiye') -> dict:
        """2022 SEGE belgesi tamamen eşleşmişse en yüksek gelişmişlik sırasındaki ilçeleri gösterir.

        Args:
            adet: 1-20 arası sonuç sayısı.
            il_adi: 'Türkiye' veya bir il adı.
        """
        if not 1<=adet<=20:return {'hata':'Adet 1-20 arasında olmalı.'}
        if 'sege_sira' not in rows.columns or rows.sege_sira.isna().any():
            return {'hata':'973 ilçenin doğrulanmış SEGE tablosu henüz mevcut değil.'}
        if normalize_name(il_adi) in ('turkiye','turkey'):
            subset=rows
        else:
            city=_city(il_adi)
            if not city:return {'hata':'İl bulunamadı.'}
            subset=rows[rows.il==city]
        subset=subset.sort_values(['sege_sira','il','ilce'])
        return {'yil':2022,'sonuclar':[{'il':str(r.il),'ilce':str(r.ilce),'sege_sirasi':int(r.sege_sira)}
                      for r in subset.head(adet).itertuples(index=False)]}

    def bolgesel_veri_durumu() -> dict:
        """İlçe nüfus verisinin varlığını ve SEGE/işletme verisinin gerçek kapsamını raporlar."""
        return {'ilce_sayisi':len(rows),'il_sayisi':len(cities),'nufus_yili':2025,
                'sege_tam_eslesme':bool('sege_sira' in rows and rows.sege_sira.notna().sum()==973),
                'yogunluk_tam_kapsam':bool('nufus_yogunlugu_km2' in rows and rows.nufus_yogunlugu_km2.notna().all()),
                'kafe_sayisi_verisi':False,'yaya_trafigi_verisi':False,
                'osm_sektorel_etiket_kayitlari':bool('osm_yeme_icme' in rows),
                'osm_ulasim_etiket_kayitlari':bool('osm_ulasim' in rows),
                'ticari_model':'Nüfus, yerleşim yoğunluğu, İlçe SEGE-2022, sektörel OSM kümelenmesi, rekabet baskısı ve ulaşım ilişkileri.'}

    return [il_nufus_ozeti, ilce_bilgi, sektorel_ilce_siralamasi,
            neden_bu_ilce_birinci, yasam_tercihi_siralamasi,
            illeri_nufusa_gore_sirala, iki_ili_nufusa_gore_karsilastir,
            ilceleri_nufusa_gore_sirala, iki_ilceyi_karsilastir,
            sektorlerin_birincilerini_karsilastir,
            yasamda_neden_bu_ilce_birinci, sege_en_gelismis_ilceler,
            bolgesel_veri_durumu]
