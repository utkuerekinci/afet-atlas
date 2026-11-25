"""Afet Atlas v3.4 — ortak harita ile yaşam, ticaret ve açıklamalı sıralama."""
from __future__ import annotations

from html import escape

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
def ilce_tablolari(data_version: str = ""):
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
        from atlas_yonetim_depo import runtime_version
        return ilce_tablolari(runtime_version())
    except Exception as exc:
        st.error('2025 ilçe nüfusu indirilemedi veya 973 ilçe doğrulamasından geçmedi. Doğrulanmayan sayılar gösterilmeyecek.')
        with st.expander('Veri bağlantısı ayrıntısı'):
            st.code(str(exc))
            st.markdown('[İndirilebilir 2025 ilçe nüfusu](https://github.com/topografya/veri)')
        return None, {'nufus':'Bulunamadı','sege':'Bulunamadı'}


def ortak_harita(sinirlar: dict, province: pd.DataFrame, col: str,
                 label: str, key: str, secim: bool = True):
    """Tam il yüzeyinden tıklanabilir, sürüklenemeyen, tek kadrajlı atlas."""
    from streamlit_folium import st_folium
    from atlas_sabit_harita import hazirla_harita, il_olayi

    chosen = st.session_state.get('secilen_il', 'Ankara')
    gunduz = bool(st.session_state.get('atlas_gunduz_modu', False))
    harita = hazirla_harita(province, col, label, chosen, gunduz=gunduz)
    result = st_folium(
        harita, height=425, use_container_width=True,
        key='sabit_harita_'+key+('_gunduz' if gunduz else '_gece'),
        returned_objects=['last_object_clicked','last_object_clicked_count'] if secim else [],
    )
    new = il_olayi(result) if secim else None
    # Aynı GeoJSON olayı sayfa yenilenince tekrar dönebilir. Tekrar işleme.
    signature_key = '_v43_harita_olayi_'+key
    signature = (new, col, result.get('last_object_clicked_count')) if new and isinstance(result,dict) else None
    if signature and signature != st.session_state.get(signature_key):
        st.session_state[signature_key] = signature
        if new in set(province['İl']) and new != chosen:
            st.session_state['secilen_il'] = new
            st.rerun()
    v=pd.to_numeric(province[col],errors='coerce').dropna()
    if not v.empty:
        gradient = ('#db5964,#ef9c72,#f3c57a,#68b9a9,#257e9a'
                    if 'güvenlik skoru' in str(label).casefold() else
                    '#426885,#4c93a6,#78b9ac,#f5bb79,#ea7566'
                    if 'nüfus' in str(label).casefold()
                    else '#20354c,#277080,#57a69b,#f5bb79,#ea7566')
        legend_color = '#4b637a' if gunduz else '#acc4d5'
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:11px;color:{legend_color};font-size:11px;'
            'margin:3px 0 7px">'
            f'<span>{escape(label)} · Düşük: {v.min():,.1f}</span>'
            '<span style="flex:1;max-width:190px;height:7px;border-radius:8px;'
            f'background:linear-gradient(90deg,{gradient})"></span>'
            f'<span>Yüksek: {v.max():,.1f}</span></div>',unsafe_allow_html=True)
    st.caption('Bir ilin renkli alanına tıkla; harita sürüklenmez ve yakınlaşmaz.')


def _il_secimi_degisti(widget_key: str):
    st.session_state['secilen_il'] = st.session_state[widget_key]


def il_secimi(illist: list[str], key: str, label: str = 'Şehir seç'):
    """Harita ve farklı modüller arasında aynı ili koruyan seçim."""
    if not illist:
        raise ValueError('İl seçimi için liste boş olamaz.')
    chosen = st.session_state.get('secilen_il', 'Ankara')
    if chosen not in illist:
        chosen = illist[0]
        st.session_state['secilen_il'] = chosen
    widget_key = 'il_select_'+key
    # Widget'dan gelen kullanıcı değişikliği callback ile zaten ana state'e işlenir.
    if st.session_state.get(widget_key) != chosen:
        st.session_state[widget_key] = chosen
    return st.selectbox(
        label, illist, key=widget_key,
        on_change=_il_secimi_degisti, args=(widget_key,),
    )


_TR_SORT = {letter: i for i, letter in enumerate('abcçdefgğhıijklmnoöprsştuüvyz')}


def turkce_sirala(value: str) -> tuple[int, ...]:
    """İl ve ilçe listelerini işletim sistemi yerel ayarına bağlı olmadan sırala."""
    normalized = str(value).translate(str.maketrans({'I':'ı','İ':'i'})).lower()
    return tuple(_TR_SORT.get(character,100+ord(character)) for character in normalized)


def ticari_firsat_il_katmani(districts: pd.DataFrame, sector: str) -> pd.DataFrame:
    """Ulusal karşılaştırmada her ilin en güçlü 3 ilçesinin fırsat ortalaması.

    İl içi sıralamanın normalize edilmiş puanları değil, aynı ulusal ölçek
    kullanılır; dolayısıyla farklı illerin harita tonları karşılaştırılabilir.
    """
    ranked, _ = sirala_ilceler(districts, 'ticaret', 'Türkiye geneli', '', sector, 'Dengeli')
    top_three = ranked.groupby('il', sort=False).head(3)
    result = top_three.groupby('il',as_index=False)['Fırsat puanı'].mean()
    return result.rename(columns={'il':'İl','Fırsat puanı':'Sektörel fırsat puanı'})


def _bar(df: pd.DataFrame, score: str, n: int = 10):
    """Sabit puan çubukları: skor yalnızca çubuğun üstüne gelince görünür."""
    plot = df.head(n).sort_values(score, ascending=True)
    labels = plot.il.astype(str) + ' / ' + plot.ilce.astype(str)
    gunduz = bool(st.session_state.get('atlas_gunduz_modu', False))
    fig = go.Figure(go.Bar(
        x=plot[score], y=labels, orientation='h', marker_color='#66d7c8',
        hovertemplate='<b>%{y}</b><br>Puan: %{x:.1f}<extra></extra>',
        hoverlabel=dict(bgcolor='#ffffff' if gunduz else '#173149',
                        font=dict(color='#20344b' if gunduz else '#f3fafb',size=12)),
    ))
    fig.update_layout(
        height=max(345, len(plot) * 35 + 80), margin=dict(l=4,r=9,t=10,b=5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#243b53' if gunduz else '#d5e7f2',size=11), dragmode=False, hovermode='closest',
        xaxis=dict(range=[0,105],fixedrange=True,showticklabels=False,
                   showgrid=False,zeroline=False,title=None,showline=False),
        yaxis=dict(fixedrange=True,showgrid=False,title=None,automargin=True),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={'displayModeBar': False, 'scrollZoom': False,
                            'doubleClick': False, 'displaylogo': False,
                            'staticPlot': False, 'responsive': True})


def aciklama_alani(ranked:pd.DataFrame, meta:dict):
    """Özgün yorumu ve Gemini düğmesini göster; sayısal tablo ayrı bölümde kalır."""
    data=neden_birinci(ranked,meta)
    if 'hata' in data:return
    top=data['birinci']
    st.markdown('### 🏆 Neden Bu İlçe Birinci?')
    st.markdown(f"**{top['il']} / {top['ilce']}** · {top['puan']:.1f} puan")
    st.write(data['yorum_paragrafi'])
    gemini_yorum_butonu(ilce_baglam(ranked, meta, data),
                        key='ilce_'+meta['mod']+'_'+meta['kapsam'].replace(' ','_'))


def sayisal_ayrintilar_alani(ranked:pd.DataFrame, meta:dict):
    """Karşılaştırma kontrolünden SONRA gelen ağırlık ve katkı dökümü."""
    data=neden_birinci(ranked,meta)
    if 'hata' in data:return
    runner=data.get('ikinci')
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

def _iki_ilce_karsilastir(ranked: pd.DataFrame, mode: str, scope: str, city: str, score: str):
    """Önce il, sonra alfabetik ilçe: iki tarafta bağımsız seçim."""
    with st.expander('İki ilçeyi karşılaştır', expanded=False):
        st.caption('Önce il, ardından karşılaştırmak istediğin ilçeyi seç.')
        if len(ranked) < 2:
            st.info('Karşılaştırma için en az iki ilçe bulunmalı.')
            return
        places = sorted(ranked['il'].unique(), key=turkce_sirala)
        first, second = ranked.iloc[0], ranked.iloc[1]
        col_a, col_b = st.columns(2, gap='medium')
        chosen_rows = []
        for label, box, suggested in (('Birinci',col_a,first), ('İkinci',col_b,second)):
            with box:
                # İl içi sekmesinde karşılaştırma yalnızca o ilin ilçeleri arasındadır.
                default_city = city if scope == 'İl içi' else str(suggested['il'])
                index = places.index(default_city) if default_city in places else 0
                current_city = st.selectbox(
                    f'{label} il', places, index=index,
                    key=f'cmp47_{mode}_{scope}_{city if scope == "İl içi" else "ulusal"}_{label}_il',
                    disabled=scope=='İl içi',
                )
                subset = ranked.loc[ranked['il'].eq(current_city)]
                district_names = sorted(subset['ilce'].astype(str).unique(), key=turkce_sirala)
                default_district = str(suggested['ilce']) if current_city == str(suggested['il']) else district_names[0]
                district_index = district_names.index(default_district) if default_district in district_names else 0
                current_district = st.selectbox(
                    f'{label} ilçe', district_names, index=district_index,
                    key=f'cmp47_{mode}_{scope}_{current_city}_{label}_ilce',
                )
                chosen_rows.append(subset.loc[subset['ilce'].eq(current_district)].iloc[0])
        if str(chosen_rows[0]['il'])==str(chosen_rows[1]['il']) and str(chosen_rows[0]['ilce'])==str(chosen_rows[1]['ilce']):
            st.info('Karşılaştırmak için iki farklı ilçe seç.')
            return
        compared = pd.DataFrame(chosen_rows)
        columns = ['il','ilce','nufus',score]
        if 'sege_sira' in compared: columns.insert(-1,'sege_sira')
        st.dataframe(compared[columns].rename(columns={
            'il':'İl','ilce':'İlçe','nufus':'Nüfus (2025)',
            'sege_sira':'SEGE Türkiye sırası',
        }), hide_index=True, use_container_width=True)
        a_score, b_score = float(chosen_rows[0][score]), float(chosen_rows[1][score])
        if abs(a_score-b_score) < .05:
            st.caption('Seçilen iki ilçenin puanı birbirine çok yakın.')
        else:
            better = chosen_rows[0] if a_score>b_score else chosen_rows[1]
            st.caption(f"Puan farkı: {abs(a_score-b_score):.1f} · Önde olan: {better['il']} / {better['ilce']}")


def siralama_alani(all_districts:pd.DataFrame,mode:str,city:str,sector:str,preference:str):
    a,b=st.tabs(['Türkiye genelindeki enler','Seçilen ildeki enler'])
    for tab,scope in ((a,'Türkiye geneli'),(b,'İl içi')):
        with tab:
            rank,meta=sirala_ilceler(all_districts,mode,scope,city,sector,preference)
            score=meta['puan_sutunu']
            st.markdown(f"#### {scope} — ilk 10")
            st.caption(f"{len(rank)} ilçe · {meta['model']}")
            l,r=st.columns([0.92,1.48],gap='medium')
            with l:
                show=['Sıra','il','ilce','nufus',score]
                if 'sege_sira' in rank: show.insert(-1,'sege_sira')
                if mode=='ticaret' and SEKTOR_SUTUNLARI[sector] in rank:
                    show.extend([SEKTOR_SUTUNLARI[sector],'osm_ulasim'])
                st.dataframe(rank[show].head(10).rename(columns={
                    'il':'İl','ilce':'İlçe','nufus':'Nüfus (2025)',
                    'sege_sira':'SEGE Türkiye sırası'}),
                    hide_index=True,use_container_width=True,height=385)
            with r:
                _bar(rank,score,min(10,len(rank)))
            # Üstteki sağ panel hem yaşam hem ticarette tek 'Neden Birinci?' yeridir.
            # Burada ikinci kez gösterilmeyip doğrudan karşılaştırmaya geçilir.
            _iki_ilce_karsilastir(rank,mode,scope,city,score)
            sayisal_ayrintilar_alani(rank,meta)
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
    st.markdown('#### '+name+' · Türkiye haritası')
    if mode=='yasam':
        options=['Nüfus (2025)','İlçe sayısı']
        if 'Ortalama ilçe SEGE sırası' in province:
            options.append('Ortalama ilçe SEGE sırası')
    else:
        options=['Sektörel fırsat puanı','Nüfus (2025)']
        if 'Ortalama ilçe SEGE sırası' in province:
            options.append('Ortalama ilçe SEGE sırası')
        options.append('İlçe sayısı')
        if status.get('osm_aktif'):
            options+=['OSM yeme-içme kaydı','OSM perakende kaydı','OSM hizmet kaydı',
                      'OSM lojistik kaydı','OSM ulaşım kaydı']

    # Ticaret ekranında kullanıcı ilk bakışta üç filtreyi birlikte görür.
    if mode=='ticaret':
        filtre, sektor_kutusu, ilkutusu=st.columns([1.13,1.14,1.0],gap='small')
    else:
        filtre, ilkutusu=st.columns([1.25,1],gap='small')
    with filtre:
        layer=st.selectbox('Harita göstergesi',options,key=mode+'_layer')
    if mode=='ticaret':
        with sektor_kutusu:
            sector=st.selectbox('Analiz edilecek sektör',list(SEKTOR_AGIRLIKLARI),key='v34_sektor')
        province=province.merge(ticari_firsat_il_katmani(df,sector),on='İl',validate='one_to_one')
    else:
        sector='Yeme-içme'
    with ilkutusu:
        city=il_secimi(sorted(province.İl.tolist()),mode,label='Şehir ara / seç')
    ortak_harita(geo,province,layer,layer,mode)
    if mode=='ticaret' and layer=='Sektörel fırsat puanı':
        st.caption(f'Harita sektörü: **{sector}** · Her ilin ulusal ölçekte en yüksek puanlı üç ilçesinin ortalaması.')
    city=st.session_state.get('secilen_il',city)
    row=province.set_index('İl').loc[city]
    local=df[df.il==city]
    biggest=local.loc[local.nufus.idxmax()]
    facts=('<div class="quick-facts">'
           f'<span>{city}</span>'
           f'<span>{int(row["Nüfus (2025)"]):,} nüfus</span>'
           f'<span>{int(row["İlçe sayısı"])} ilçe</span>'
           f'<span>En kalabalık ilçe: {biggest.ilce}</span>'
           + (f'<span>{int(local.osm_ulasim.sum())} ulaşım kaydı</span>'
              if mode=='ticaret' and status.get('osm_aktif') else '')
           + '</div>')
    if mode=='yasam':
        st.markdown(facts,unsafe_allow_html=True)
    controls,preview=st.columns([1,1.35],gap='large')
    with controls:
        if mode=='ticaret':
            # Daha önce bu sütunda bulunan sektör filtresi yukarıya taşındı.
            # Var olan il özetini buraya alarak boş alan bırakmıyoruz.
            st.markdown(facts,unsafe_allow_html=True)
            pref='Dengeli'
        else:
            with st.container(key='yasam_tercih_grubu'):
                pref=st.radio('Yaşam tercihi',['Dengeli','Daha sakin','Daha hareketli'],
                              horizontal=False,key='v34_preference')
    local_rank,local_meta=sirala_ilceler(df,mode,'İl içi',city,sector,pref)
    with preview:
        if not local_rank.empty:
            with st.container(border=True):
                aciklama_alani(local_rank,local_meta)
    siralama_alani(df,mode,city,sector,pref)
    if mode=='ticaret':
        if status.get('osm_aktif'):
            with st.expander(f'İşletme ve ulaşım sayıları · {city}', expanded=False):
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
