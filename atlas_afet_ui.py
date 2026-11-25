"""Deprem dışındaki altı afet için gerçek kaynaklı gösterge/harita ekranları."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from atlas_afet_veri import get, AFETLER
from atlas_ui import il_sinirlari, ortak_harita, il_secimi
from atlas_il_yorumlari import yangin_il_yorumu, yangin_lider_yorumu
from atlas_afet_veri import safe_fire
from atlas_gemini_yorum import afet_baglam, gemini_yorum_butonu


def diger_afet_sayfasi(afet:str)->None:
    if afet not in AFETLER:raise ValueError('Afet türü yok')
    years=[2024,2025] if afet=='Orman yangını' else [2024]
    cc=st.columns([1.1,1.6,2.2])
    with cc[0]:year=st.selectbox('Veri yılı',years,index=len(years)-1,key=f'afet_yil_{afet}')
    metric=None
    if afet=='Orman yangını':
        with cc[1]:metric=st.selectbox('Harita göstergesi',['Yangın sayısı','Yanan alan (ha)'],key='v36_fire_metric')
    try:
        record=get(afet,year,metric)
    except (OSError, ValueError, KeyError, TypeError):
        import logging
        logging.getLogger(__name__).exception('Afet veri dosyası okunamadı: %s (%s)', afet, year)
        st.caption('Bu afet türünün kayıtları yüklenemedi.')
        return
    df=record['tablo']
    col=record['harita_kolonu']
    known=int(df[col].notna().sum())
    with cc[2]:
        st.caption('Veri kaynağı: '+('OGM istatistiklerinden ikincil aktarım' if record['tip']=='ikincil_sayisal' else
                                     'MGM yıllık raporu' if record['tip']=='rapor_kaniti' else 'MGM iklim raporu (bölge ortalaması)'))
        st.markdown(f'[Kaynak belgesi / arşiv]({record["kaynak"]})')
    if record['tip']=='ikincil_sayisal':
        st.caption(f'{year} · Türkiye toplam yangın: {record["ulusal_toplam"]:,} · Kayıtlı il: {known}/81')
    elif record['tip']=='rapor_kaniti':
        st.caption(f'{year} · Rapordaki toplam afet: {record["ulusal_toplam"]} · İl bulgusu: {known}/81')
    else:
        st.caption('2024 · Bölgesel yağış değişimi')

    city=il_secimi(sorted(df.İl.tolist()),f'v36_{afet}_{year}',label='Şehir ara / seç')
    st.markdown('#### Türkiye haritası · '+afet)
    ortak_harita(il_sinirlari(),df[['İl',col]].copy(),col,record['birim'],f'v36_{afet}_{year}_{col}')
    city=st.session_state.get('secilen_il',city)
    row=df.set_index('İl').loc[city]
    with st.container(border=True):
        st.markdown('#### '+city+' · '+afet)
        if record['tip']=='ikincil_sayisal':
            if pd.notna(row['Yangın sayısı']):
                st.metric('Yangın sayısı',f'{int(row["Yangın sayısı"]):,}'.replace(',','.'))
            else:st.metric('Yangın sayısı','—')
            if pd.notna(row['Yanan alan (ha)']):
                st.metric('Yanan orman alanı',f'{row["Yanan alan (ha)"]:,.1f} ha'.replace(',','X').replace('.',',').replace('X','.'))
            else:st.metric('Yanan orman alanı','—')
            st.markdown('**İlin yangın profili**')
            existing=yangin_il_yorumu(city,year,col,df,safe_fire(2024) if year==2025 else None)
            st.write(existing)
        elif record['tip']=='rapor_kaniti':
            if pd.notna(row['Rapor vurgusu']):
                st.success('**Raporda yer alıyor.** '+row['Açıklama'])
                st.write('Kaydedilen olay aralığı: '+str(row['Olay aralığı']))
            else:
                st.write('Bu il için rapor metninde ayrıntılı bir il kaydı bulunmuyor.')
        else:
            st.metric('2024 bölgesel yıllık yağış farkı',f'{row[col]:+.1f}%'.replace('.',','))
            st.caption(f'Coğrafi bölge: **{row["Bölge"]}**')
    gemini_yorum_butonu(afet_baglam(afet,city,year,df,col,
                                       existing if record['tip']=='ikincil_sayisal' else ''),
                        key='afet_'+afet.replace(' ','_').replace('/','_'))
    st.markdown('### Karşılaştırma ve kaynaklı değerlendirme')
    if record['tip']=='ikincil_sayisal':
        rank=df.dropna(subset=[col]).sort_values([col,'İl'],ascending=[False,True]).reset_index(drop=True)
        st.write('**En yüksek 10 il — '+record['birim']+'**')
        st.dataframe(rank[['İl','Yangın sayısı','Yanan alan (ha)']].head(10),hide_index=True,use_container_width=True)
        if len(rank)>1:
            top=rank.iloc[0]
            old=safe_fire(2024) if year==2025 else None
            st.write(f'**{top["İl"]} neden öne çıkıyor?** '+yangin_lider_yorumu(rank,year,col,old))
    elif record['tip']=='rapor_kaniti':
        subset=df[df['Rapor vurgusu'].notna()].sort_values(['Rapor vurgusu','İl'],ascending=[False,True])
        st.write('**2024 raporunda öne çıkan iller**')
        st.dataframe(subset[['İl','Açıklama','Olay aralığı']],hide_index=True,use_container_width=True)
        if afet=='Çığ':
            st.write('MGM 2024 çığ haritasında Van **6–8** kayıt sınıfında, diğer açıkça belirtilmiş iller **1–2** kayıt sınıfındadır. Aralıklar kesin sayıya çevrilmedi.')
        st.write(f'MGM, 2024 yılı için Türkiye genelinde **{record["ulusal_toplam"]}** '
                 f'{"sel/şiddetli yağış" if afet=="Sel / taşkın" else afet.lower()} afeti kaydetmiştir. '
                 'Bu dağılım yerel afet hazırlığı ve müdahale planlaması için önemli bir karşılaştırma alanı sunuyor.')
    else:
        region=pd.DataFrame([{'Bölge':r,'Yağış değişimi (%)':float(v)} for r,v in
                            sorted(df.groupby('Bölge')[col].first().items(),key=lambda x:x[1])])
        st.dataframe(region,hide_index=True,use_container_width=True)
        st.write('**Yorum:** Yağışın uzun dönem normalinin belirgin altında kaldığı bölgelerde su yönetimi, tarımsal planlama ve kurak dönemlere hazırlık daha fazla önem kazanıyor.')
    with st.expander('Kaynak ve yöntem'):
        st.write('Tarih: 2024' if year==2024 else 'Tarih: 2025')
        st.markdown(f'**Orijinal kaynak:** {record["kaynak"]}')

    st.download_button('Bu katmanın kaynaklı kayıtlarını CSV indir',df.to_csv(index=False).encode('utf-8-sig'),
                      file_name=f'afet_atlas_{afet.replace(" ","_").replace("/","")}_{year}.csv',
                      mime='text/csv',key=f'download_v36_{afet}_{year}')
