"""BBY261 — Afet Atlas. Çalıştır: python -m streamlit run app.py"""
from __future__ import annotations

from datetime import date
import os
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from hesaplama import puanlari_hesapla
from harita_cizimi import turkiye_haritasi
from afet_atlas_adk.calistir import ajana_sor_ayrintili
from veri import depremleri_getir, il_sinirlarini_getir
from atlas_ui import yasam_ticaret_sayfasi, veri_yukle, il_sinirlari, ortak_harita, il_secimi
from atlas_afet_ui import diger_afet_sayfasi
from atlas_analiz import illere_ozet
from atlas_gemini_yorum import il_baglam, gemini_yorum_butonu, api_anahtari
from genel_bakis import (OVERVIEW_TOPICS, TOPIC_DESCRIPTIONS, TOPIC_DESTINATIONS,
                         prepare_provinces, available_layers, layer_frame, city_summary)

st.set_page_config(
    page_title="Afet Atlas | Türkiye Bölgesel Analiz ve Karar Destek Platformu",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Yalnızca görsel tasarım: hesaplamalar hesaplama.py dosyasında tutulur.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {color-scheme:dark;}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family:'DM Sans', Inter, sans-serif;
}
.stApp {
    background:
      radial-gradient(ellipse 58% 35% at 82% 0%, rgba(20,93,122,.16), transparent 78%),
      radial-gradient(ellipse 55% 40% at 15% 35%, rgba(28,61,119,.11), transparent 75%),
      #080f1d;
    color: #dce6f3;
}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stMain"] .block-container {max-width:1380px; padding:1.05rem 2.2rem 5rem;}
[data-testid="stSidebar"] {background:#0d1828; border-right:1px solid #26354b;}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {padding-top:1.6rem;}
[data-testid="stSidebar"] p {color:#acbdd2;}
[data-testid="stSidebar"] label {color:#d5e6f3!important; font-size:13px;}
[data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stSelectSlider {margin-bottom:6px;}
[data-testid="stSidebar"] [data-baseweb="select"]>div {background:#152337!important; border-color:#32465f!important; color:#eef7ff!important;}
[data-testid="stSidebar"] .stSlider [role="slider"] {background-color:#61e0d1;}
[data-testid="stSidebar"] hr {border-color:#27384e;}
[data-testid="stExpander"] {background:#101d30; border:1px solid #24364c; border-radius:18px;}
[data-testid="stDataFrame"] {border:1px solid #2a3a53; border-radius:16px; overflow:hidden;}
[data-testid="stMetric"] {background:#111e31; border:1px solid #26364d; padding:18px; border-radius:18px;}
[data-testid="stMetricLabel"] {color:#a6bdd0;}
[data-testid="stMetricValue"] {color:#f4f8fe;}
[data-testid="stAlert"] {border-radius:14px;}
[data-testid="stDownloadButton"] button {
    background:#18324a!important; border:1px solid #346277!important; color:#bdf7ef!important;
    border-radius:14px!important; padding:10px 16px!important;
}
[data-testid="stDownloadButton"] button:hover {background:#22536a!important; border-color:#65e2d3!important;}
button[data-baseweb="tab"] {font-family:'DM Sans', sans-serif!important; font-weight:700; font-size:14px; color:#a7b8cc!important;}
button[data-baseweb="tab"][aria-selected="true"] {color:#65e6d5!important;}
[data-baseweb="tab-highlight"] {background-color:#65e6d5!important;}
[data-baseweb="tab-border"] {background-color:#23344b!important;}
h1, h2, h3 {font-family:'Space Grotesk', 'DM Sans', sans-serif!important; color:#f4f8ff!important; letter-spacing:-.035em;}
h2 {font-size:1.55rem!important;} h3 {font-size:1.22rem!important;}
a {color:#7ce8d9!important;}
.hero {position:relative; overflow:hidden; isolation:isolate; display:flex; justify-content:space-between; align-items:center;
  min-height:280px; padding:38px 45px; border:1px solid #27475b; border-radius:26px;
  background:linear-gradient(112deg, #142c44 0%, #11243a 55%, #113746 100%);
  box-shadow:0 25px 65px rgba(0,0,0,.2); margin-bottom:21px;
}
.hero:before {content:''; position:absolute; inset:0; background:linear-gradient(90deg, transparent, rgba(79,198,188,.04)), repeating-linear-gradient(90deg,transparent,transparent 77px,rgba(255,255,255,.026) 78px), repeating-linear-gradient(0deg,transparent,transparent 77px,rgba(255,255,255,.019) 78px); z-index:-1;}
.hero-text {position:relative; z-index:2; max-width:680px;}
.overline {display:inline-flex; align-items:center; gap:8px; font-size:11px; letter-spacing:.19em; text-transform:uppercase; font-weight:800; color:#6ceddc;}
.dot {display:inline-block; width:7px; height:7px; background:#6df0dc; box-shadow:0 0 14px #6df0dc; border-radius:50%;}
.hero h1 {font-size:clamp(2.35rem,4.45vw,4.5rem); font-weight:700; line-height:1.05; margin:20px 0 12px; letter-spacing:-.07em;}
.hero h1 em {color:#72e7da; font-style:normal;}
.hero h1.safety-title {font-size:clamp(2.15rem,3.5vw,3.65rem);letter-spacing:-.058em;max-width:720px;}
.hero .module-title {font-family:'Space Grotesk', sans-serif; font-weight:600; font-size:19px; color:#e0f3f7; margin:0 0 13px; letter-spacing:-.025em;}
.hero p {color:#bdccdc; font-size:15px; max-width:510px; line-height:1.8; margin:0;}
.hero-tags {display:flex; gap:9px; margin-top:22px; flex-wrap:wrap;}
.hero-tag {border:1px solid rgba(136,209,220,.2); background:rgba(8,24,44,.44); color:#bed4e7; font-size:11px; font-weight:700; letter-spacing:.05em; border-radius:99px; padding:8px 11px;}
.radar {position:relative; flex:none; width:230px; height:230px; margin:0 15px 0 25px; border:1px solid rgba(112,236,226,.32); border-radius:50%; box-shadow:inset 0 0 55px rgba(84,221,209,.045),0 0 60px rgba(84,221,209,.025); background:conic-gradient(from 20deg,transparent 0deg,transparent 290deg,rgba(116,233,220,.14) 336deg,transparent 360deg);}
.radar:before,.radar:after {content:''; position:absolute; border:1px solid rgba(112,236,226,.23); border-radius:50%; inset:24%;}
.radar:after {inset:41%; border:1px solid rgba(112,236,226,.45);}
.radar-line-h,.radar-line-v {position:absolute; background:rgba(112,236,226,.19);}
.radar-line-h {height:1px; width:100%; top:50%;} .radar-line-v {width:1px; height:100%; left:50%;}
.radar-core {position:absolute; z-index:2; width:11px; height:11px; background:#62e8d9; box-shadow:0 0 0 8px rgba(103,240,221,.09),0 0 25px #62e8d9; border-radius:50%; left:calc(50% - 5px); top:calc(50% - 5px);}
.radar-ping,.radar-ping2 {position:absolute; border-radius:50%; background:#ffa46a; box-shadow:0 0 0 6px rgba(255,156,90,.12),0 0 20px rgba(255,156,90,.6); width:8px; height:8px; left:70%; top:31%;}
.radar-ping2 {left:23%; top:59%; width:5px; height:5px;}
.radar-label {position:absolute; left:50%; bottom:-20px; transform:translateX(-50%); font-size:10px; color:#8dbbba; letter-spacing:.15em; white-space:nowrap;}
.metrics {display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:8px 0 26px;}
.metric {background:linear-gradient(135deg,#132236,#0e1b2c); border:1px solid #25384f; border-radius:18px; padding:21px 23px; min-height:125px; position:relative; overflow:hidden;}
.metric:before {content:''; position:absolute; left:0; top:24px; bottom:24px; width:3px; background:var(--accent,#65e6d5); border-radius:4px;}
.metric-label {font-size:11px; letter-spacing:.1em; font-weight:800; text-transform:uppercase; color:#94aac2;}
.metric-value {font-family:'Space Grotesk',sans-serif; color:#f4f9ff; font-size:2.65rem; font-weight:700; line-height:1.35; letter-spacing:-.055em;}
.metric-foot {color:#849bb4; font-size:11px; font-weight:500;}
.subheading {display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin:26px 0 11px;}
.subheading h2 {font-size:1.43rem!important; margin:0!important;}
.subheading p {font-size:12px; color:#8da4bc; margin:0;}
.kicker {font-size:10px; font-weight:800; letter-spacing:.16em; color:#61dfd0; text-transform:uppercase; margin-bottom:8px;}
.card {border:1px solid #25394f; border-radius:20px; background:#111e31; padding:21px; margin:5px 0 12px;}
.card-title {font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700; color:#eff7fe; margin-bottom:8px; letter-spacing:-.03em;}
.card-note {font-size:12px; color:#90a7be; line-height:1.7;}
.ranking-list {display:flex; flex-direction:column; gap:15px; padding:8px 2px 4px;}
.rank-top {display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:7px; font-size:13px;}
.rank-top strong {font-weight:700; color:#e5f3fe;} .rank-top span {font-weight:700; color:#f4a77d;}
.rank-track {height:7px; background:#223249; border-radius:15px; overflow:hidden;}
.rank-fill {height:100%; border-radius:15px; background:linear-gradient(90deg,#d56862,#f3a273);}
.caption-note {color:#8ea6bd; font-size:12px; line-height:1.7; margin:11px 0 15px;}
.warning-note {border:1px solid #5f4b3d; background:linear-gradient(90deg,rgba(107,65,35,.16),rgba(10,27,42,.18)); color:#d5c1ad; padding:13px 17px; border-radius:14px; font-size:12px; line-height:1.6; margin:12px 0 14px;}
.warning-note strong {color:#ffcc9c;}
.sidebar-head {font-family:'Space Grotesk',sans-serif; color:#eaf7ff; font-size:22px; font-weight:700; letter-spacing:-.04em; margin:8px 0 2px;}
.sidebar-small {font-size:12px; color:#849bb4; margin-bottom:24px;}
.sidebar-label {font-size:10px; font-weight:800; letter-spacing:.16em; color:#64daca; margin:20px 0 11px; text-transform:uppercase;}
.sidebar-scale {border:1px solid #273b51; border-radius:14px; overflow:hidden;}
.sidebar-scale-row {display:flex; justify-content:space-between; align-items:center; padding:9px 11px; border-bottom:1px solid #22334a; font-size:12px; color:#b7cadd;}
.sidebar-scale-row:last-child {border-bottom:0;}
.scale-num {color:#8ae7dd; font-weight:800; font-family:'Space Grotesk',sans-serif;}
.two-stat {display:grid; grid-template-columns:repeat(2,1fr); gap:12px;}
.mini-stat {border:1px solid #2b415a; border-radius:14px; padding:16px; background:#13253a;}
.mini-stat-label {color:#9bb0c6; font-size:11px; margin-bottom:5px;}
.mini-stat-value {color:#eaf7ff; font-size:25px; font-weight:700; font-family:'Space Grotesk',sans-serif;}
.footer-brand {margin-top:35px; padding:16px 0; border-top:1px solid #29384b; color:#8399b2; font-size:11px; display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;}
@media(max-width:1000px){.radar {width:170px; height:170px;}.hero{padding:27px;min-height:230px}.metrics{grid-template-columns:repeat(2,1fr)}}
@media(max-width:700px){[data-testid="stMain"] .block-container{padding:1rem 1rem 3rem}.radar{display:none}.hero{padding:26px 21px;min-height:210px}.hero h1{font-size:2.45rem}.metrics{gap:9px}.metric{padding:15px;min-height:111px}.metric-value{font-size:2rem}.metric-label{font-size:9px}}
[data-testid="stSidebar"] [role="radiogroup"] label {background:#132338; border:1px solid #263b52; border-radius:12px; padding:9px 10px; margin-bottom:3px;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {border-color:#60cdbf;}
.atlas-action {background:linear-gradient(120deg,#132e42,#112136);border:1px solid #2d5064;border-radius:20px;padding:20px 22px;min-height:145px;}
.atlas-action strong {display:block;font-family:'Space Grotesk',sans-serif;font-size:18px;color:#f4f8ff;margin-bottom:9px;}
.atlas-action p {font-size:13px;color:#a6c1cd;line-height:1.6;}
/* Ana sayfa: deprem radarının yerine üç ana araştırma alanını birleştiren atlas figürü */
.atlas-orbit {position:relative;flex:none;width:250px;height:236px;margin:0 7px 0 25px;}
.atlas-orbit .orbit-ring {position:absolute;inset:17px 18px 16px 15px;border:1px dashed rgba(104,217,206,.36);border-radius:50%;transform:rotate(-17deg);}
.atlas-orbit .orbit-ring.inner {inset:52px 55px 50px 52px;border:1px solid rgba(104,217,206,.22);transform:none;}
.atlas-orbit .orbit-center {position:absolute;inset:83px 79px 80px 78px;background:linear-gradient(145deg,#204e5b,#123247);border:1px solid #5cc9be;border-radius:24px;display:flex;align-items:center;justify-content:center;flex-direction:column;box-shadow:0 0 35px rgba(102,224,213,.16);}
.orbit-center strong {font-family:'Space Grotesk',sans-serif;font-size:28px;line-height:1;color:#e8fff9;}
.orbit-center span {font-size:9px;letter-spacing:.11em;color:#8dcdcb;margin-top:4px;}
.orbit-node {position:absolute;z-index:2;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;letter-spacing:.04em;box-shadow:0 8px 24px rgba(0,0,0,.25);border-radius:13px;padding:13px 16px;}
.orbit-node.life {top:4px;right:14px;color:#b2fff0;background:#184a48;border:1px solid #419e92;}
.orbit-node.trade {bottom:13px;right:0;color:#ffe4b7;background:#503b37;border:1px solid #9a7860;}
.orbit-node.disaster {bottom:36px;left:-4px;color:#d0d6ff;background:#283954;border:1px solid #5c709e;}
.overview-lead {color:#98b2c9;font-size:13px;line-height:1.75;margin:0 0 15px;}
.overview-meta {display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:18px 0 12px;}
.overview-meta h2 {margin:0!important;font-size:1.42rem!important;}
.overview-meta p {margin:5px 0 0;color:#92aec3;font-size:12px;}
.overview-pane {border:1px solid #2b4557;background:linear-gradient(145deg,#132638,#101e31);border-radius:20px;padding:21px;margin-top:5px;}
.overview-pane .eyebrow {color:#6bddce;font-size:10px;font-weight:800;letter-spacing:.15em;text-transform:uppercase;}
.overview-pane h3 {font-family:'Space Grotesk',sans-serif;color:#eef8ff;font-size:24px!important;margin:7px 0 6px!important;}
.overview-pane p {font-size:13px;line-height:1.7;color:#b3c8d6;margin:10px 0 0;}
.overview-data {display:flex;gap:9px;flex-wrap:wrap;margin:14px 0 6px;}
.overview-chip {background:#182f43;border:1px solid #33556a;border-radius:12px;padding:10px 12px;flex:1;min-width:110px;}
.overview-chip b {display:block;font-family:'Space Grotesk',sans-serif;font-size:17px;color:#f3f8ff;}
.overview-chip span {display:block;font-size:10px;color:#9ab4c8;margin-top:5px;}
.overview-thought {color:#86c8c5;font-size:12px;letter-spacing:.015em;margin:13px 0 16px;line-height:1.65;}
@media(max-width:1000px){.atlas-orbit{width:200px;height:200px;margin-left:12px}.atlas-orbit .orbit-center{inset:65px 62px}.atlas-orbit .orbit-node{padding:10px 11px}}
@media(max-width:700px){.atlas-orbit{display:none}.overview-pane{padding:16px}}
</style>
""", unsafe_allow_html=True)


def metric(kisa_baslik: str, deger: str, alt: str, renk: str = "#65e6d5") -> str:
    return (f'<div class="metric" style="--accent:{renk}">'
            f'<div class="metric-label">{escape(kisa_baslik)}</div>'
            f'<div class="metric-value">{escape(deger)}</div>'
            f'<div class="metric-foot">{escape(alt)}</div></div>')


def bolum(baslik: str, aciklama: str = "", ust: str = "") -> None:
    st.markdown(
        f'<div class="subheading"><div>'
        f'{f"<div class=kicker>{escape(ust)}</div>" if ust else ""}'
        f'<h2>{escape(baslik)}</h2></div>'
        f'<p>{escape(aciklama)}</p></div>', unsafe_allow_html=True
    )


def panel_baslik(baslik: str, notu: str = "") -> None:
    st.markdown(f'<div style="margin:3px 0 9px"><div class="card-title">{escape(baslik)}</div>'
                f'<div class="card-note">{escape(notu)}</div></div>', unsafe_allow_html=True)



@st.cache_data(ttl=6 * 3600, show_spinner=False)
def verileri_yukle(baslangic_yili: int, bitis_yili: int, min_buyukluk: float):
    sinirlar = il_sinirlarini_getir()
    olaylar = depremleri_getir(baslangic_yili, bitis_yili, min_buyukluk)
    return sinirlar, olaylar


@st.cache_data(show_spinner=False)
def hesapla(depremler: pd.DataFrame, sinirlar: dict, mesafe: int):
    return puanlari_hesapla(depremler, sinirlar, mesafe)






# ---------- v3.4 Modüller / harita çapında ortak il seçimi ----------
MODULES=['Genel Bakış','Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel','Siz Sorun','Veri ve Yöntem']
if 'secilen_il' not in st.session_state:
    st.session_state['secilen_il']='Ankara'
with st.sidebar:
    st.markdown('<div class="overline"><span class="dot"></span> BBY261 · İLERİ PROGRAMLAMA</div>'
                '<div class="sidebar-head">AFET ATLAS</div>'
                '<div class="sidebar-small">Bölgesel Analiz ve Karar Destek</div>',unsafe_allow_html=True)
    module=st.radio('Bölüm',MODULES,key='v34_bolum')
    st.divider()
    st.markdown('<div class="sidebar-label">SEÇİLİ BÖLGE</div>',unsafe_allow_html=True)
    st.write('**'+st.session_state.get('secilen_il','Ankara')+'**')
    if module=='Afet Analizi':
        chosen_disaster=st.selectbox('Afet türü',['Deprem','Orman yangını','Sel / taşkın','Heyelan','Çığ','Fırtına','Kuraklık'],key='v36_disaster')
    else:
        chosen_disaster='Deprem'
    if (module=='Afet Analizi' and chosen_disaster=='Deprem') or module=='Siz Sorun':
        st.markdown('<div class="sidebar-label">DEPREM FİLTRELERİ</div>',unsafe_allow_html=True)
        years=list(range(2015,date.today().year+1))
        y0=st.selectbox('Başlangıç yılı',years,index=years.index(2025),key='v34_year_start')
        valid=[x for x in years if x>=y0]
        y1=st.selectbox('Bitiş yılı',valid,index=valid.index(max(2025,y0)),key='v34_year_end')
        m=st.selectbox('Minimum büyüklük',[4.5,5.0],key='v34_min_m')
        distance=st.select_slider('İl sınırına yakınlık (km)',options=[0,50,75,100,150],value=0,key='v34_distance')
    else:
        y0,y1,m,distance=2025,2025,4.5,0

    st.divider()
    st.caption('Veri → Analiz → Harita → Açıklama · v4.2')


def heading(section:str,text:str,description:str,overview:bool=False):
    illustration = (
        '<div class="atlas-orbit" aria-hidden="true"><div class="orbit-ring"></div>'
        '<div class="orbit-ring inner"></div>'
        '<div class="orbit-center"><strong>TR</strong><span>KEŞFET</span></div>'
        '<div class="orbit-node life">YAŞAM</div><div class="orbit-node trade">TİCARET</div>'
        '<div class="orbit-node disaster">AFET</div></div>'
        if overview else
        '<div class="radar"><div class="radar-line-h"></div><div class="radar-line-v"></div>'
        '<div class="radar-core"></div><div class="radar-ping"></div></div>'
    )
    st.markdown(f'<div class="hero"><div class="hero-text">'
                f'<div class="overline"><span class="dot"></span>{escape(section)}</div>'
                f'<h1>AFET <em>ATLAS.</em></h1>'
                f'<div class="module-title">{escape(text)}</div>'
                f'<p>{escape(description)}</p></div>'
                f'{illustration}</div>',unsafe_allow_html=True)


def deprem_bul(y0:int,y1:int,m:float,d:int):
    sinirlar,depremler=verileri_yukle(y0,y1,m)
    iller,eslesenler=hesapla(depremler,sinirlar,d)
    return sinirlar,depremler,iller,eslesenler


def dis_dashboard(geo,depremler,illers,eslesenler,overview=False):
    st.markdown('<div class="metrics">'+
        metric('DEPREM KAYDI',str(len(depremler)),'USGS olay sayısı')+
        metric('İL KAPSAMI','81','Türkiye il sınırları','#89a8ff')+
        metric('EN BÜYÜK M',f'{depremler.mag.max():.1f}','Seçilen veri dönemi','#efa67c')+
        metric('EŞLEŞME',str(len(eslesenler)),'İl × olay eşleşmeleri','#88dba8')+'</div>',unsafe_allow_html=True)
    display=illers[['İl','Toplam puan','Deprem sayısı','Karşılaştırma endeksi']].copy()
    st.markdown('### Türkiye haritası · Deprem hareketliliği')
    left,right=st.columns([1.7,1],gap='large')
    with left:
        ortak_harita(geo,display,'Toplam puan','Olay puanı','overview' if overview else 'disaster')
    with right:
        selected=il_secimi(sorted(display.İl), 'overview' if overview else 'disaster')
        province=display.set_index('İl').loc[selected]
        st.metric(f'{selected} — toplam olay puanı',int(province['Toplam puan']))
        st.metric('Eşleşen deprem sayısı',int(province['Deprem sayısı']))
        st.write(f"{selected} için seçilen dönemde {int(province['Deprem sayısı'])} eşleşen olay ve "
                 f"{int(province['Toplam puan'])} olay puanı bulunuyor. "
                 "İlin bu dönemdeki hareketliliği diğer illerle karşılaştırılabilir.")
        gemini_yorum_butonu({
            'konu':'Deprem hareketliliği il profili', 'il':selected,
            'veri_yillari':[int(y0),int(y1)], 'minimum_buyukluk':float(m),
            'il_sinir_mesafesi_km':int(distance),
            'il_gostergeleri':{'deprem_sayisi':int(province['Deprem sayısı']),
                              'olay_puani':float(province['Toplam puan'])},
            'ulke_karsilastirma':display.sort_values('Toplam puan',ascending=False).head(5).to_dict('records'),
            'not':'Bu puan tarihsel deprem hareketliliğidir; güvenlik olasılığı değildir.',
        },key='deprem_'+selected)

        st.markdown('#### Hareketliliği en yüksek 5 il')
        st.dataframe(display.sort_values('Toplam puan',ascending=False).head(5),hide_index=True,use_container_width=True)

    if not overview:
        t1,t2=st.tabs(['İl sıralaması','Seçilen ilin kayıtları'])
        with t1:
            positive=illers[illers['Deprem sayısı']>0]
            st.dataframe(positive[['Sıra','İl','Deprem sayısı','En büyük deprem','Toplam puan','Karşılaştırma endeksi']],
                         hide_index=True,use_container_width=True)
            with st.expander('Eşleşen depremi olmayan iller'):
                st.dataframe(illers.loc[illers['Deprem sayısı']==0,['İl','Deprem sayısı']],hide_index=True,use_container_width=True)
        with t2:
            chosen=st.session_state.get('secilen_il','Ankara')
            recent=eslesenler[eslesenler['İl']==chosen].sort_values('Tarih',ascending=False)
            if recent.empty:st.info('Seçilen kapsamda bu il için eşleşme bulunmadı.')
            else:st.dataframe(recent,use_container_width=True,hide_index=True)


if module=='Genel Bakış':
    heading('BİR ÜLKE · ÜÇ FARKLI BAKIŞ', 'Türkiye’nin haritasından fazlası.',
            'Nerede yaşamak isterdin? Hangi bölgede yeni bir iş kurardın? Doğal afetler hangi illerde öne çıkıyor? '
            'Türkiye’yi yaşam, ticaret ve afet perspektiflerinden keşfet; ilçelerin hikâyesini verilerle karşılaştır.',
            overview=True)

    st.markdown('<div class="metrics">'+
        metric('İL KAPSAMI','81','Türkiye’nin tüm illeri','#67dfd0')+
        metric('İLÇE KAPSAMI','973','İlçe düzeyinde karşılaştırma','#87acf5')+
        metric('AFET KATMANLARI','7','İl bazında afet analizi','#f2b081')+
        metric('TİCARİ ALANLAR','4','İlçe bazında fırsat keşfi','#ac9af1')+'</div>',unsafe_allow_html=True)

    st.markdown('<div class="overview-meta"><div>'
                '<div class="kicker">ETKİLEŞİMLİ TÜRKİYE ATLASI</div>'
                '<h2>Haritanın bakış açısını değiştir.</h2>'
                '<p>Aynı ülke, farklı sorular. Bir konu seç, şehirleri karşılaştır ve ayrıntılara in.</p>'
                '</div></div>',unsafe_allow_html=True)
    topic=st.radio('Neyi keşfetmek istersin?', OVERVIEW_TOPICS,
                   horizontal=True, key='home_v40_topic')
    try:
        with st.spinner('Türkiye atlası hazırlanıyor...'):
            raw, overview_status = veri_yukle()
            if raw is None:
                st.stop()
            geo=il_sinirlari()
            districts, provinces=prepare_provinces(raw,geo)
        labels=available_layers(provinces,topic)
        if not labels:
            st.info('Bu konu için harita katmanları hazırlanıyor.')
        else:
            a,b=st.columns([1.52,1],gap='large')
            with a:
                layer=st.selectbox('Harita göstergesi',labels,key='home_v40_layer_'+topic)
                st.markdown(f'<p class="overview-lead">{escape(TOPIC_DESCRIPTIONS[topic])}</p>',unsafe_allow_html=True)
                layer_data, layer_col, layer_text=layer_frame(provinces,topic,layer)
                ortak_harita(geo, layer_data, layer_col, layer_text,'home_v40')
            with b:
                city=il_secimi(sorted(provinces['İl'].tolist()),'home_v40',label='Şehir seç')
                details=city_summary(districts,provinces,city,topic,layer)
                population_text=f'{details["nufus"]:,}'.replace(',','.')
                st.markdown(
                    '<div class="overview-pane">'
                    '<div class="eyebrow">SEÇİLİ ŞEHİR · YAKINDAN BAKIŞ</div>'
                    f'<h3>{escape(city)}</h3>'
                    '<div class="overview-data">'
                    f'<div class="overview-chip"><b>{population_text}</b><span>2025 nüfusu</span></div>'
                    f'<div class="overview-chip"><b>{details["ilce"]}</b><span>İlçe</span></div>'
                    '</div>'
                    f'<div class="card-title" style="margin-top:18px">{escape(details["title"])}</div>'
                    f'<p>{escape(details["text"])}</p>'
                    '<div class="overview-data">'
                    f'<div class="overview-chip"><b>{escape(details["key_value"])}</b>'
                    f'<span>{escape(details["key_label"])}</span></div>'
                    +(f'<div class="overview-chip"><b>{escape(details["secondary_value"])}</b>'
                      f'<span>{escape(details["secondary_label"])}</span></div>'
                      if 'secondary_value' in details else '')+
                    '</div></div>',unsafe_allow_html=True
                )
                gemini_yorum_butonu(il_baglam(districts, provinces, city, topic, layer, details),
                                    key='genel_bakis_'+topic.replace(' ','_'))
                target=TOPIC_DESTINATIONS[topic]
                if st.button(f'{target} bölümünde ayrıntıları gör',
                             key='home_v40_explore_'+topic,use_container_width=True,type='primary'):
                    st.session_state['v34_bolum']=target
                    st.rerun()
        st.markdown('<div class="overview-thought">Büyük resmi haritada gör. Bir ili seçtiğinde ilçelerin yaşam düzenini, '
                    'ticari karakterini ve doğal koşullarını ayrı ayrı keşfedebilirsin.</div>',unsafe_allow_html=True)
    except Exception as exc:
        st.error('Genel bakış haritası şu anda görüntülenemedi.')
        with st.expander('Teknik ayrıntılar'):st.code(str(exc))
    st.markdown('### Analiz alanları')
    a,b,c=st.columns(3)
    for col,title,desc,target in [(a,'Afet Analizi','7 afet türü, il haritaları ve karşılaştırmalar','Afet Analizi'),
                                  (b,'Yaşam Kalitesi','Türkiye ve il içi ilçe sıralamaları','Yaşam Kalitesi'),
                                  (c,'Ticari Potansiyel','Sektörel fırsat, OSM işletme ve ulaşım katmanları','Ticari Potansiyel')]:
        with col:
            st.markdown(f'<div class="atlas-action"><strong>{escape(title)}</strong><p>{escape(desc)}</p></div>',unsafe_allow_html=True)
            if st.button(title+' bölümüne git',key='open_'+target,use_container_width=True):
                st.session_state['v34_bolum']=target
                st.rerun()

elif module=='Yaşam Kalitesi':
    heading('TÜRKİYE GENELİ / İL İÇİ','Yaşam Kalitesi','Nüfus, yoğunluk ve varsa SEGE ile yaşam tercihine uygunluk analizlerini karşılaştır.')
    yasam_ticaret_sayfasi('yasam')

elif module=='Ticari Potansiyel':
    heading('SEKTÖREL ANALİZ / İLÇELER','Ticari Potansiyel','İlçe nüfusu ve SEGE ile karşılaştır; doğrulanmış OSM verisi yüklendiğinde işletme ve ulaşım katmanlarını incele.')
    yasam_ticaret_sayfasi('ticaret')

elif module=='Afet Analizi':
    heading('DOĞAL AFET ANALİZİ','İl bazında afet göstergeleri','Yedi afet türüne ilişkin kaynaklı il haritaları, rapor bulguları ve karşılaştırmalar.')
    disaster=chosen_disaster
    if disaster!='Deprem':
        diger_afet_sayfasi(disaster)
    else:
        try:
            with st.spinner('USGS deprem analizi yapılıyor...'):
                geo,depremler,illers,eslesenler=deprem_bul(y0,y1,m,distance)
            dis_dashboard(geo,depremler,illers,eslesenler)
        except Exception as exc:st.error('Deprem verisi yüklenemedi.');st.code(str(exc))

elif module=='Siz Sorun':
    heading('GOOGLE ADK / GEMINI','Siz Sorun','Yedi afetin mevcut veri kapsamını, deprem istatistiklerini ve ilçe karşılaştırmalarını açıklayan Google ADK ajanı.')
    try:
        geo,depremler,illers,eslesenler=deprem_bul(y0,y1,m,distance)
    except Exception:
        # Diğer modüllerin ajanı, USGS geçici olarak erişilemezse de çalışır.
        geo,depremler,illers,eslesenler=None,None,None,None
    df,status=veri_yukle()
    if api_anahtari():
        os.environ['GOOGLE_API_KEY']=api_anahtari()
    try:
        value=st.secrets.get('AFET_ATLAS_MODEL')
        if value:os.environ['AFET_ATLAS_MODEL']=str(value)
    except Exception:pass
    os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI','FALSE')
    deprem_kapsam=(f' · Deprem: {y0}–{y1}, M ≥ {m}, {distance} km' if depremler is not None
                   else ' · Deprem: bağlantı yok')
    st.caption('Seçili il: **'+st.session_state.get('secilen_il','Ankara')+'**' + deprem_kapsam +
               (' · Yaşam/ticaret: 973 ilçe' if df is not None else ''))
    if not api_anahtari():
        st.warning('ADK için Google API anahtarı Streamlit Secrets bölümünde tanımlanmalı.')
    example=st.selectbox('Örnek soru',["Kendi sorum",'Ankara ile İstanbul’un deprem puanlarını karşılaştır.',
        '2025 yılında Balıkesir’de kaç deprem gerçekleşmiş?',
        'Türkiye genelinde hizmet sektörü için en yüksek 5 ilçeyi bul.',
        'Ankara’da yeme-içme sektöründe neden bu ilçe birinci?',
        'İzmir ilçelerinde daha sakin yaşam tercihine göre ilk 5 ilçe hangisi?',
        '2025 deprem kayıtlarında en büyük 10 olayı sırala.',
        'Türkiye genelindeki depremlerin aylık dağılımını göster.',
        'Balıkesir toplam deprem puanını hangi büyüklük gruplarından aldı?',
        '81 ilin deprem olay sayısına göre ilk 10 sıralamasını çıkar.',
        'Ankara ve İzmir nüfuslarını karşılaştır.',
        'Türkiye genelinde en kalabalık 10 ilçeyi sırala.',
        'Dört ticaret sektöründe birinci gelen ilçeler hangileri?',
        'Şu an hangi afetler ve ticari veriler sayısal olarak hazır?',
        '2025 orman yangını sayısına göre en yüksek 10 il hangisi?',
        '2024 yılında kaç sel ve fırtına afeti raporlanmış?',
        '2024 yılında Van ilindeki çığ kayıtları ne gösteriyor?',
        '2024 yağışları hangi coğrafi bölgelerde normale göre azdı?'])
    query=st.text_area('Sorunuz',value='' if example=='Kendi sorum' else example,height=100,key='v34_question_'+example)
    if st.button('✦ Soruyu gönder',type='primary',disabled=not api_anahtari(),use_container_width=True):
        try:
            with st.spinner('Google ADK veri araçlarını çalıştırıyor...'):
                contextual=query+f'\n(Sitede seçili il: {st.session_state.get("secilen_il","Ankara")}. İl belirtilmemişse bu ili kullan.)'
                res=ajana_sor_ayrintili(contextual,illers,depremler,eslesenler,y0,y1,m,distance,df)
                st.session_state['last_adk_v34']={**res,'kapsam':(y0,y1,m,distance),'il':st.session_state.get('secilen_il')}
        except Exception as exc:
            st.error('Google ADK isteği başarısız.');
            with st.expander('Teknik ayrıntı'):st.code(str(exc))
    if st.session_state.get('last_adk_v34') and (
            st.session_state['last_adk_v34'].get('kapsam')==(y0,y1,m,distance) and
            st.session_state['last_adk_v34'].get('il')==st.session_state.get('secilen_il')):
        res=st.session_state['last_adk_v34']
        st.markdown('### Ajan yanıtı')
        st.write(res.get('cevap'))
        with st.expander('ADK araç çağrıları',expanded=True):
            if not res.get('arac_cagrilari'):st.warning('Veri aracı çağrısı yok; sayısal iddiaları kontrol et.')
            for item in res.get('arac_cagrilari',[]):st.write(item['arac']);st.json(item.get('parametreler',{}))

else:
    heading('VERİ & YÖNTEM','Kaynaklar ve Puanlama','Veriler, model ağırlıkları ve geçerli kapsamları ayrı ayrı incele.')
    st.markdown("""### Veri kaynakları
- [OGM 2024 il yangın istatistikleri](https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2053) ve [2025 il yangın istatistikleri](https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2364): gösterilen il tabloları ikincil aktarım; resmî Excel satır kontrolü bekliyor.
- [MGM 2024 meteorolojik afetler raporu](https://www.mgm.gov.tr/FILES/genel/raporlar/2024%20MetAfet%20Degerlendirme%20Raporu_V1.pdf): 434 sel, 257 fırtına, 42 heyelan, 17 çığ ulusal toplamı ve illerin metindeki varlığı.
- [MGM 2024 iklim raporu](https://mgm.gov.tr/FILES/iklim/yillikiklim/2024-iklim-raporu.pdf): bölgelere göre yağış sapması; il düzeyi SPI değildir.
- [USGS Earthquake Catalog](https://earthquake.usgs.gov/earthquakes/search/) — olay koordinatları ve büyüklükleri.
- [geoBoundaries TUR ADM1](https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/) — 81 il sınırı.
- [2025 ilçe nüfus CSV](https://github.com/topografya/veri) — TÜİK ADNKS 2025 temelli üçüncü taraf aktarım.
- [İlçe SEGE-2022](https://www.sanayi.gov.tr/assets/pdf/birimler/2022-ilce-sege.pdf) — 973 ilçe gelişmişlik profili.
- [© OpenStreetMap katkıcıları / Geofabrik Türkiye](https://download.geofabrik.de/europe/turkey.html) — işletme ve ulaşım noktaları; © OpenStreetMap katkıcıları, ODbL 1.0.
- [İlçe sınırları: kullanıcı tarafından sağlanan alternatif GeoJSON](https://rodostoteknoloji.com/online-tools/turkey-boundaries.html) — 973 ilçe sınırı.
- [Tapusor işyeri kiraları](https://www.ai.tapusor.com/public/api/) — işyeri kira verisi kaynağı.

### Puanlama
- Deprem: M4.5–4.9 = 1, M5–5.9 = 3, M6–6.9 = 5, M7+ = 7 olay puanı.
- Ticaret: Sektöre göre nüfus, yaklaşık nüfus yoğunluğu ve varsa SEGE ağırlıklandırılır. Türkiye ve il bazında ayrı normalize edilir. 973/973 OSM kaydı yüklenirse sektörel işletme kümelenmesi, nüfusa göre rekabet baskısı ve lojistik dışı sektörlerde toplu taşıma kayıtları eklenir. 973 ilçede geçerli ve yeterli örneklemli ticari kira varsa ancak o zaman ortak puana katılır.
- Model göstergeleri nüfus, SEGE-2022, sektörel OSM ve erişilebilirlik kayıtlarından oluşturulur.
- Yaşam: Tercih edilen yerleşim ritmi %60, İlçe SEGE gelişmişlik profili %30 ve OSM ulaşım göstergesi %10 ağırlıkla birleştirilir; erişilebilir bileşenler üzerinden hesaplama yapılır.
- **“Neden Bu İlçe Birinci?”** sıralama, ağırlık ve katkılardan otomatik hesaplanır.
""")

st.markdown('<div class="footer-brand"><span>◉ AFET ATLAS · TÜRKİYE BÖLGESEL ANALİZ</span><span>BBY261 · Python · Google ADK · Gemini · v4.2</span></div>',unsafe_allow_html=True)
