"""Yaşam / ticaret modülleri; gerçek demografik veriler + şeffaf proje modelleri."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ilce_veri import POP_URL, SEGE_LOCAL, SEGE_URL, combine, fetch_population, read_sege_csv
from bolge_puanlari import ticari_on_endeks, yasam_tercih_endeksi, SEKTOR_AGIRLIKLARI


@st.cache_data(ttl=21600, show_spinner=False)
def _population():
    return fetch_population()


def tr_fmt(x:float|int):
    return f"{x:,.0f}".replace(",", ".")


def _grafik(data:pd.DataFrame, x:str, title:str, y:str='ilce'):
    vis = data.head(15).iloc[::-1].copy()
    fig=px.bar(vis,x=x,y=y,orientation='h',labels={x:title,y:'İlçe'},
               hover_data=['nufus'] if x!='nufus' else None, template='plotly_dark')
    fig.update_traces(marker_color='#65e6d5')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font_color='#cde6ed',height=min(690,max(340, len(vis)*34)), margin=dict(l=0,r=18,t=15,b=10))
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})


def show_page(mode:str='yasam'):
    if mode not in ('yasam','ticaret'):
        raise ValueError('Tanımsız modül')
    try:
        with st.spinner('Türkiye ilçe verileri alınıyor...'):
            pop=_population()
    except Exception as exc:
        st.error('İlçe nüfusu kaynağına erişilemedi. Bu bölümün veri kaynağını yenilemek gerekiyor.')
        with st.expander('Bağlantı ayrıntısı'):
            st.code(str(exc))
            st.markdown(f'[CSV kaynağı]({POP_URL})')
        return

    sege=None
    sege_error=None
    if SEGE_LOCAL.is_file():
        try:
            sege=read_sege_csv()
        except Exception as exc:
            sege_error=str(exc)
    try:
        df, status=combine(pop,sege)
    except Exception as exc:
        sege_error=str(exc)
        df,status=combine(pop)
        sege=None

    cities=sorted(df.il.unique().tolist())
    city=st.selectbox('İl seç',cities,index=cities.index('Ankara') if 'Ankara' in cities else 0,key=f'{mode}_il')
    district=df[df.il==city].copy()
    district=district.sort_values('nufus',ascending=False)
    a,b,c=st.columns(3)
    a.metric('İlçe',tr_fmt(len(district)))
    b.metric('Toplam yerleşik nüfus (2025)',tr_fmt(district.nufus.sum()))
    c.metric('En kalabalık ilçe',str(district.iloc[0].ilce))

    if mode=='yasam':
        st.markdown('### İlçelerin nüfus ve yerleşim profili')

        with st.container():
            left,right=st.columns([1,2])
            with left:
                preference=st.selectbox('Yaşamak istediğin yerin karakteri', ['Dengeli','Daha sakin','Daha hareketli'],key='yasam_preferans')

            with right:
                interpreted=yasam_tercih_endeksi(district,preference)
                best=interpreted.iloc[0]
                st.metric('Tercihinle en çok eşleşen ilçe',best.ilce, f'{best["Tercih uyumu"]:.0f}/100 model puanı',delta_color='off')
        c1,c2=st.tabs(['Nüfus karşılaştırması','Tercih uyumu'])
        with c1:
            _grafik(district,'nufus','Nüfus (2025)')
        with c2:
            _grafik(interpreted,'Tercih uyumu','Tercih uyum puanı')
            st.dataframe(interpreted[['ilce','nufus','Tercih uyumu']].rename(columns={'ilce':'İlçe','nufus':'Nüfus (2025)'}),hide_index=True,use_container_width=True)
        if sege is not None:
            st.markdown('### Resmî SEGE-2022 gelişmişlik göstergeleri')
            st.dataframe(district[['ilce','nufus','sege_sira','sege_skor','sege_kademe']].rename(columns={
                'ilce':'İlçe','nufus':'Nüfus 2025','sege_sira':'Türkiye sırası','sege_skor':'SEGE skoru','sege_kademe':'Kademe'}),
                use_container_width=True,hide_index=True)
        else:
            st.markdown('### Sosyoekonomik gelişmişlik')
            st.caption('Gelişmişlik verileri güncellendiğinde burada görüntülenecek.')
    else:
        st.markdown('### Sektöre göre ticari fırsat keşfi')
        sektor=st.selectbox('İncelemek istediğin sektör',list(SEKTOR_AGIRLIKLARI),key='ticari_sektor_v33')
        scored,meta=ticari_on_endeks(district,sektor)
        best=scored.iloc[0]
        a,b,c=st.columns(3)
        a.metric('Modelde öne çıkan ilçe',str(best.ilce))
        b.metric('Ön fırsat puanı',f'{best["Fırsat puanı"]:.0f}/100')
        c.metric('Analiz edilen ilçe',len(scored))

        l,r=st.columns([1.35,1],gap='large')
        with l:
            _grafik(scored,'Fırsat puanı',f'{sektor} — göreli fırsat puanı')
        with r:
            st.markdown('#### İlk beş ilçe')
            st.dataframe(scored[['ilce','Fırsat puanı','nufus']].head(5).rename(columns={'ilce':'İlçe','nufus':'Nüfus 2025'}),
                         use_container_width=True,hide_index=True)
            st.markdown('#### Modelin kullandığı göstergeler')
            labels={'nufus':'Yerleşik nüfus','yogunluk':'Nüfus yoğunluğu','dusuk_yogunluk':'Düşük yerleşim yoğunluğu','sege':'SEGE gelişmişlik sırası'}
            for k,v in meta['agirliklar'].items():
                st.progress(float(v),text=f'{labels[k]}: %{v*100:.0f}')
        st.markdown('#### İlçeleri yan yana karşılaştır')
        cols=st.columns(2)
        top=list(scored.ilce)
        with cols[0]: first=st.selectbox('Birinci ilçe',top,index=0,key='ticaret_ilce_a')
        with cols[1]: second=st.selectbox('İkinci ilçe',top,index=min(1,len(top)-1),key='ticaret_ilce_b')
        picks=scored[scored.ilce.isin([first,second])][['ilce','nufus','Fırsat puanı']]
        st.dataframe(picks.rename(columns={'ilce':'İlçe','nufus':'Yerleşik nüfus','Fırsat puanı':'Model puanı'}),
                     hide_index=True,use_container_width=True)
        with st.expander('Bu puan nasıl hesaplanıyor?'):
            st.write('Bu sürümde sektör ağırlıkları proje kapsamında tarafımızdan seçildi. Göstergeler, seçilen ilin ilçeleri arasında sıralanır ve 0–100 ölçeğine çevrilir. Ölçüm bulunmayan göstergeye 0 verilmez; kalan ağırlıklar oransal olarak yeniden dağıtılır.')
            if meta['kullanilamayan']:
                st.write('Bu il için hesaplamaya katılmayan göstergeler:', ', '.join(labels[x] for x in meta['kullanilamayan']))

        st.download_button('↓ Sektörel ilçe tablosunu CSV indir', scored.drop(columns=['anahtar'],errors='ignore').to_csv(index=False).encode('utf-8-sig'),
                          file_name=f'afet_atlas_{city.lower()}_{sektor.replace(" ","_")}_firsat.csv',mime='text/csv')
    with st.expander('Veri kaynakları ve teknik doğrulama'):
        st.markdown(f'''- [2025 ilçe nüfus aktarımı]({POP_URL}) — dayandığı kaynak TÜİK ADNKS.
- [İlçe SEGE-2022 resmî raporu]({SEGE_URL}).
- İşletme verisi OpenStreetMap/Geofabrik üzerinden değerlendirilir.''')
        if sege_error:
            st.caption('SEGE dönüştürme kontrol notu: '+sege_error)
