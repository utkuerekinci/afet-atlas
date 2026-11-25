"""ADK: Orman yangını ve MGM 2024 kaynaklı altı afet aracı."""
from __future__ import annotations
import pandas as pd
from atlas_afet_veri import AFETLER, get, MGM_IL, MGM_ULUSAL


def diger_afet_araclari_olustur():
    def afet_ulusal_ozet(afet_turu: str, yil: int = 2024) -> dict:
        """Deprem dışı afetin ulusal toplamını, yılını ve kaynak kapsamını açıkla.

        Args:
            afet_turu: Orman yangını, Sel / taşkın, Heyelan, Çığ, Fırtına veya Kuraklık.
            yil: 2024 veya orman yangınında 2025.
        """
        if afet_turu not in AFETLER:return {'hata':'Bilinmeyen afet türü','seçenekler':AFETLER}
        try:d=get(afet_turu,yil)
        except ValueError as e:return {'hata':str(e)}
        tab=d['tablo']
        out={'afet':afet_turu,'yil':yil,'kaynak':d['kaynak'],'veri_turu':d['tip'],
             'ulusal_olay_sayisi':d['ulusal_toplam'],'kapsam_aciklamasi':d['not']}
        if d['tip']=='ikincil_sayisal':
            out['il_sayisi']=81;out['yangin_sayisi_mevcut_il']=int(tab['Yangın sayısı'].notna().sum())
        elif d['tip']=='rapor_kaniti':
            out['il_metninde_adi_gecen_iller']=int(tab['Rapor vurgusu'].notna().sum())
        else:out['bolgeler']=tab[['Bölge','Bölge yağış sapması (%)']].drop_duplicates().to_dict('records')
        return out

    def afet_il_detayi(afet_turu: str, il_adi: str, yil: int = 2024) -> dict:
        """Seçilen ilin yangın istatistiği veya MGM 2024 raporunda açıkça geçen kaydını getir.

        Args:
            afet_turu: Orman yangını, Sel / taşkın, Heyelan, Çığ, Fırtına veya Kuraklık.
            il_adi: Türkiye'de 81 ilden biri.
            yil: MGM için 2024, orman yangını için 2024 veya 2025.
        """
        if afet_turu not in AFETLER:return {'hata':'Desteklenmeyen afet'}
        try:d=get(afet_turu,yil)
        except ValueError as e:return {'hata':str(e)}
        row=d['tablo'].set_index('İl')
        if il_adi not in row.index:
            import atlas_afet_veri as ver
            match=[x for x in row.index if ver.key(x)==ver.key(il_adi)]
            if len(match)!=1:return {'hata':'İl eşleşmedi','ornek':'Hakkâri'}
            il_adi=match[0]
        record={k:(None if pd.isna(v) else v.item() if hasattr(v,'item') else v)
                for k,v in row.loc[il_adi].to_dict().items()}
        return {'il':il_adi,'afet':afet_turu,'yil':yil,'degerler':record,
                'olcum_birimi':d['birim'],'veri_turu':d['tip'],'kaynak':d['kaynak'],
                'onemli_not':d['not']}

    def afet_illeri_sirala(afet_turu: str, yil: int = 2024, gosterge: str = 'Yangın sayısı', adet: int = 10) -> dict:
        """Yalnızca orman yangını için sayısal il sıralaması yap; diğerlerinde rapor bulgularını getir.

        Args:
            afet_turu: Orman yangını, Sel / taşkın, Heyelan, Çığ, Fırtına veya Kuraklık.
            yil: 2024 veya yangında 2025.
            gosterge: Yangın sayısı veya Yanan alan (ha).
            adet: En çok 20 il.
        """
        if afet_turu not in AFETLER:return {'hata':'Desteklenmeyen afet'}
        if type(adet) is not int or not 1<=adet<=20:return {'hata':'adet 1 ile 20 arasında olmalıdır'}
        try:d=get(afet_turu,yil,metric=gosterge)
        except ValueError as e:return {'hata':str(e)}
        tab=d['tablo']
        if d['tip']=='ikincil_sayisal':
            c=d['harita_kolonu']
            records=tab.dropna(subset=[c]).sort_values([c,'İl'],ascending=[False,True]).head(adet)
            return {'afet':afet_turu,'yil':yil,'gosterge':c,'siralama':records[['İl',c]].rename(columns={'İl':'il',c:'deger'}).to_dict('records'),
                    'kaynak':d['kaynak'],'uyari':d['not']}
        if d['tip']=='rapor_kaniti':
            return {'afet':afet_turu,'yil':yil,'ulusal_olay_sayisi':d['ulusal_toplam'],
                    'metinde_adi_gecen_iller':tab.dropna(subset=['Rapor vurgusu'])[['İl','Açıklama','Olay aralığı']].rename(columns={'İl':'il'}).to_dict('records'),
                    'kesin_il_siralamasi_mumkun_mu':False,'neden':'Raporun tüm illeri için kesin sayılar CSV olarak çıkarılmış değil.',
                    'kaynak':d['kaynak']}
        return {'afet':afet_turu,'yil':yil,'bolgesel_yagis_degisimi':tab[['Bölge','Bölge yağış sapması (%)']].drop_duplicates().sort_values('Bölge yağış sapması (%)').to_dict('records'),
                'kesin_il_siralamasi_mumkun_mu':False,'kaynak':d['kaynak']}

    def afet_veri_kaynagi(afet_turu:str)->dict:
        """Deprem dışı bir afetin kaynağını, yıllarını, kanıt tipini ve sınırlarını ver.

        Args:
            afet_turu: Orman yangını, Sel / taşkın, Heyelan, Çığ, Fırtına veya Kuraklık.
        """
        if afet_turu not in AFETLER:return {'hata':'Desteklenmeyen afet'}
        d=get(afet_turu,2024)
        return {'afet':afet_turu,'mevcut_yillar':[2024,2025] if afet_turu=='Orman yangını' else [2024],
                'veri_turu':d['tip'],'kaynak':d['kaynak'],'metodoloji_notu':d['not']}
    return [afet_ulusal_ozet, afet_il_detayi, afet_illeri_sirala, afet_veri_kaynagi]
