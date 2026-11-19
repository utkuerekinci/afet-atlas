"""Afet Atlas v3.4 — ortak harita ile yaşam, ticaret ve açıklamalı sıralama."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from atlas_harita import katman_haritasi, secilen_nokta
from atlas_analiz import illere_ozet, sirala_ilceler, neden_birinci, NAMES
from atlas_gemini_yorum import ilce_baglam, gemini_yorum_butonu
from bolge_puanlari import SEKTOR_AGIRLIKLARI
from ticaret_veri import zenginlestir_ilceler, SEKTOR_SUTUNLARI
from ilce_veri import SEGE_LOCAL, combine, fetch_population, read_sege_csv, normalize_name
from veri import il_sinirlarini_getir

@st.cache_data(ttl=21600,show_spinner=False)
def ilce_tablolari():
    pop=fetch_population()
    sege=None
    if SEGE_LOCAL.exists():
        try: sege=read_sege_csv()
        except (ValueError,KeyError) as exc:
            st.warning('SEGE aktarımı doğrulanamadı: '+str(exc))
    merged,status=combine(pop,sege)
    extra,extra_status=zenginlestir_ilceler(merged)
    return extra,{**status,**extra_status}

@st.cache_data(show_spinner=False)
def il_sinirlari():
    return il_sinirlarini_getir()


def veri_yukle():
    try:
        return ilce_tablolari()
    except Exception as exc:
        st.error('2025 ilçe nüfusu indirilemedi veya 973 ilçe doğrulamasından geçmedi. Doğrulanmayan sayılar gösterilmeyecek.')
        with st.expander('Veri bağlantısı ayrıntısı'):
            st.code(str(exc))
            st.markdown('[İndirilebilir 2025 ilçe nüfusu](https://github.com/topografya/veri)')
        return None, {'nufus':'Bulunamadı','sege':'Bulunamadı'}


def ortak_harita(sinirlar:dict, province:pd.DataFrame, col:str, label:str, key:str, secim:bool=True):
    chosen=st.session_state.get('secilen_il','Ankara')
    fig=katman_haritasi(sinirlar,province,col,label,secilen_il=chosen)
    try:
        event=st.plotly_chart(fig,use_container_width=True,key='map_'+key+'_'+chosen,
                              on_select='rerun' if secim else 'ignore',selection_mode='points',
                              config={'displaylogo':False,'scrollZoom':False})
        new=secilen_nokta(event)
        if new and new!=chosen:
            st.session_state['secilen_il']=new
            st.session_state['il_select_'+key]=new
            st.rerun()
    except TypeError: # Eski Streamlit sürümleri için çizim geri dönüşü
        st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
    st.caption('Haritadaki beyaz il noktalarına tıklayabilir veya aşağıdaki listeden il seçebilirsin. Renkler seçili katmanın değerlerini gösterir.')


def il_secimi(illist:list[str],key:str,label:str="İncelenecek il"):
    selection=st.session_state.get('secilen_il','Ankara')
    if selection not in illist:selection=illist[0]
    chosen=st.selectbox(label,illist,index=illist.index(selection),key='il_select_'+key)
    if chosen!=st.session_state.get('secilen_il'):
        st.session_state['secilen_il']=chosen
        st.rerun()
    return chosen


def _bar(df:pd.DataFrame,score:str,n:int=10):
    plot=df.head(n).sort_values(score,ascending=True)
    tags=plot.il.astype(str)+' / '+plot.ilce.astype(str)
    fig=go.Figure(go.Bar(x=plot[score],y=tags,orientation='h',marker_color='#66d7c8',
                         hovertemplate='%{y}<br>Puan: %{x:.1f}<extra></extra>'))
    fig.update_layout(height=max(340,n*32+80),margin=dict(l=5,r=4,t=15,b=8),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#d5e7f2'),xaxis=dict(range=[0,105],gridcolor='#243c51'))
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})


def aciklama_alani(ranked:pd.DataFrame, meta:dict):
    data=neden_birinci(ranked,meta)
    if 'hata' in data:return
    top=data['birinci']; runner=data.get('ikinci')
    st.markdown('### 🏆 Neden Bu İlçe Birinci?')
    st.markdown(f"**{top['il']} / {top['ilce']}** · {top['puan']:.1f} puan")
    st.write(data['yorum_paragrafi'])
    gemini_yorum_butonu(ilce_baglam(ranked, meta, data),
                        key='ilce_'+meta['mod']+'_'+meta['kapsam'].replace(' ','_'))
    # Yorum önce gelir; ayrıntılı sayılar ve model katkıları isteğe bağlıdır.
    with st.expander('Karşılaştırmanın sayısal ayrıntıları'):
        if runner:
            st.write(f"İkinci ilçe: **{runner['il']} / {runner['ilce']}** · "
                     f"{runner['puan']:.1f} puan · fark: {data['fark']:.1f} puan")
        factors=pd.DataFrame(data['gostergeler']).rename(columns={
            'gosterge':'Gösterge','agirlik_yuzde':'Ağırlık (%)',
            'birinci_katki':'Birincinin katkısı','ikinci_katki':'İkincinin katkısı',
            'katki_farki':'Katkı farkı'})
        columns=[c for c in ['Gösterge','Ağırlık (%)','Birincinin katkısı',
                             'İkincinin katkısı','Katkı farkı'] if c in factors]
        st.dataframe(factors[columns],hide_index=True,use_container_width=True)


def siralama_alani(all_districts:pd.DataFrame,mode:str,city:str,sector:str,preference:str):
    a,b=st.tabs(['Türkiye genelindeki enler','Seçilen ildeki enler'])
    for tab,scope in ((a,'Türkiye geneli'),(b,'İl içi')):
        with tab:
            rank,meta=sirala_ilceler(all_districts,mode,scope,city,sector,preference)
            score=meta['puan_sutunu']
            st.markdown(f"#### {scope} — ilk 10")
            st.caption(f"{len(rank)} ilçe · {meta['model']}")
            l,r=st.columns([1.3,1],gap='large')
            with l:_bar(rank,score,min(10,len(rank)))
            with r:
                show=['Sıra','il','ilce','nufus',score]
                if 'sege_sira' in rank:show.insert(-1,'sege_sira')
                if mode=='ticaret' and SEKTOR_SUTUNLARI[sector] in rank:
                    show.extend([SEKTOR_SUTUNLARI[sector],'osm_ulasim'])
                st.dataframe(rank[show].head(10).rename(columns={'il':'İl','ilce':'İlçe','nufus':'Nüfus (2025)','sege_sira':'SEGE Türkiye sırası'}),
                             hide_index=True,use_container_width=True,height=375)
            aciklama_alani(rank,meta)
            with st.expander('İki ilçeyi karşılaştır'):
                labels=[f"{row.il} / {row.ilce}" for row in rank.itertuples(index=False)]
                ca,cb=st.columns(2)
                one=ca.selectbox('Birinci ilçe',range(len(labels)),format_func=lambda i:labels[i],index=0,key=f'cmp_{mode}_{scope}_a')
                two=cb.selectbox('İkinci ilçe',range(len(labels)),format_func=lambda i:labels[i],index=min(1,len(labels)-1),key=f'cmp_{mode}_{scope}_b')
                st.dataframe(rank.iloc[list(dict.fromkeys([one,two]))][['il','ilce','nufus',score]],hide_index=True,use_container_width=True)
            st.download_button('Bu kapsamın sıralamasını indir',rank.to_csv(index=False).encode('utf-8-sig'),
                               file_name=f"afet_atlas_{mode}_{'turkiye' if scope=='Türkiye geneli' else city}.csv",
                               mime='text/csv',key=f'download_{mode}_{scope}')


def yasam_ticaret_sayfasi(mode:str):
    df,status=veri_yukle()
    if df is None: return None
    geo=il_sinirlari()
    canonical={normalize_name(f['properties']['shapeName']):f['properties']['shapeName']
               for f in geo['features']}
    if set(df.il.map(normalize_name)) != set(canonical):
        st.error('İlçe nüfusu ile 81 ilin harita adları örtüşmüyor; eksik alanlar düzeltilecek.')
        return None
    df=df.copy()
    df['il']=df['il'].map(lambda value: canonical[normalize_name(value)])
    province=illere_ozet(df)
    city=st.session_state.get('secilen_il','Ankara')
    if city not in province.İl.tolist():city='Ankara'
    name='Yaşam Kalitesi' if mode=='yasam' else 'Ticari Potansiyel'
    st.markdown(f'## {name} · Türkiye il haritası')
    if mode=='yasam':
        options=['Nüfus (2025)','İlçe sayısı']
        if 'Ortalama ilçe SEGE sırası' in province:options.append('Ortalama ilçe SEGE sırası')
        layer=st.selectbox('Harita katmanı',options,key='yasam_layer')

    else:
        layers=['Nüfus (2025)','İlçe sayısı']
        if status.get('osm_aktif'):
            layers+=['OSM yeme-içme kaydı','OSM perakende kaydı','OSM hizmet kaydı','OSM lojistik kaydı','OSM ulaşım kaydı']
        layer=st.selectbox('Harita katmanı',layers,key='ticaret_layer')

        if not status.get('osm_aktif'):
            st.info('İşletme haritası hazırlanıyor; nüfus ve SEGE analizi kullanılabilir.')

    left,right=st.columns([1.75,1],gap='large')
    with left:ortak_harita(geo,province,layer,layer,mode)
    with right:
        city=il_secimi(sorted(province.İl.tolist()),mode)
        row=province.set_index('İl').loc[city]
        st.metric(f'{city} toplam nüfus (2025)',f"{int(row['Nüfus (2025)']):,}".replace(',','.'))
        st.metric('İlçe sayısı',int(row['İlçe sayısı']))
        local=df[df.il==city]
        biggest=local.loc[local.nufus.idxmax()]
        st.metric('En kalabalık ilçesi',biggest.ilce)
        if mode=='ticaret' and status.get('osm_aktif'):
            st.metric('İl genelindeki OSM ulaşım kayıtları',int(local.osm_ulasim.sum()))
    
    if mode=='ticaret':
        sector=st.selectbox('Analiz edilecek sektör',list(SEKTOR_AGIRLIKLARI),key='v34_sektor')
        pref='Dengeli'
    else:
        pref=st.radio('Yaşam tercihi',['Dengeli','Daha sakin','Daha hareketli'],horizontal=True,key='v34_preference')
        sector='Yeme-içme'
    siralama_alani(df,mode,city,sector,pref)
    if mode=='ticaret':
        if status.get('osm_aktif'):
            st.markdown('### OSM işletme ve ulaşım görünümü')
            subset=df[df.il==city].copy()
            business=SEKTOR_SUTUNLARI[sector]

            cols=['ilce','nufus',business,'osm_ulasim']
            st.dataframe(subset[cols].sort_values(business,ascending=False).rename(columns={
                'ilce':'İlçe','nufus':'Nüfus (2025)',business:'OSM sektörel kayıt','osm_ulasim':'OSM durak/istasyon kaydı'}),
                hide_index=True,use_container_width=True)
        if status.get('kira_kapsami'):
            st.markdown('### Ticari kira')
            local_rent=df[(df.il==city)&df.kira_m2_tl.notna()]
            if not local_rent.empty:
                st.dataframe(local_rent[['ilce','kira_m2_tl','ilan_adedi','kaynak','tarih']].rename(columns={
                    'ilce':'İlçe','kira_m2_tl':'İşyeri ilan kirası TL/m²',
                    'ilan_adedi':'İlan örneklemi','kaynak':'Kaynak','tarih':'Güncelleme tarihi'}),
                    hide_index=True,use_container_width=True)



    with st.expander('Veri kaynakları ve puanlama yöntemi'):
        st.markdown('**Nüfus:** 2025 TÜİK ADNKS temelli ilçe derlemesi. '
                    '**Gelişmişlik:** İlçe SEGE-2022, eğitim ve sağlık dahil 56 değişkenli araştırma. '
                    '**İşletme ve ulaşım:** OpenStreetMap / Geofabrik kayıtları.')
        st.write('Her ilçe aynı karşılaştırma evreninde kendi göstergelerine göre puanlanır. '
                 'Sektör ağırlıkları ve ikinci ilçeyle karşılaştırma yukarıdaki sayısal ayrıntılarda yer alır.')
        st.markdown('[OpenStreetMap / Geofabrik](https://download.geofabrik.de/europe/turkey.html) · '
                    '[2022 İlçe SEGE (Sanayi ve Teknoloji Bakanlığı)](https://www.sanayi.gov.tr/bolgesel-kalkinma-faaliyetleri/analitik-calismalar/01161b) · '
                    '[İlçe nüfusu](https://github.com/topografya/veri) · '
                    '[Sınır verisi](https://rodostoteknoloji.com/online-tools/turkey-boundaries.html)')
    return df
