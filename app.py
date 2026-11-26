"""BBY261 — Afet Atlas. Çalıştır: python -m streamlit run app.py"""
from __future__ import annotations

from datetime import date
import os
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Afet Atlas | Türkiye Bölgesel Analiz ve Karar Destek Platformu",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Kaynak kod ve özel veri deposu ayrıdır. Güncel veri deposu gerekirse uygulama
# modülleri import edilmeden önce geçici, doğrulanmış okuma alanına alınır.
from atlas_yonetim_depo import settings_from_secrets, initialize_remote_data
try:
    _atlas_data_settings = settings_from_secrets(st.secrets)
    _atlas_data_changed = initialize_remote_data(_atlas_data_settings)
    if _atlas_data_changed:
        st.cache_data.clear()
except Exception:
    # Özel depoya erişim kesilse bile herkese açık analiz arayüzü çalışabilsin.
    # Yönetici ekranı bağlantı sorununu ayrıca bildirecek.
    from atlas_yonetim_depo import Settings
    _atlas_data_settings = Settings()

from hesaplama import puanlari_hesapla
from atlas_deprem_kayitlari import secilen_il_kayitlari, hareketliligi_yuksek_bes_il
from harita_cizimi import turkiye_haritasi
from afet_atlas_adk.calistir import ajana_sor_ayrintili
from veri import depremleri_getir, il_sinirlarini_getir
from atlas_ui import yasam_ticaret_sayfasi, veri_yukle, il_sinirlari, ortak_harita, il_secimi, ilce_arama, il_paneli_gecisleri
from atlas_afet_ui import diger_afet_sayfasi
from atlas_analiz import illere_ozet
from atlas_gemini_yorum import il_baglam, gemini_yorum_butonu, genel_bakis_detay_kontrolu, api_anahtari
from genel_bakis import (OVERVIEW_TOPICS, TOPIC_DESCRIPTIONS, TOPIC_DESTINATIONS,
                         prepare_provinces, available_layers, layer_frame, city_summary)
from atlas_tema import ortak_kontrol_css
from atlas_kaydirma import kaydirma_butonu


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
[data-testid="stMain"] .block-container {max-width:1500px; padding:1rem 1.4rem 3rem;}
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
[data-testid="stMetric"] {background:#111e31; border:1px solid #26364d; padding:11px 13px; border-radius:13px;}
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
/* Ana sayfa alt bilgisindeki küçük yönetici erişimi; yalnızca görünüm. */
.atlas-footer-rule {margin-top:35px; padding-top:12px; border-top:1px solid #29384b;}
.atlas-footer-text {color:#8399b2; font-size:11px; line-height:1.65;}
.atlas-footer-text-right {text-align:right;}
.st-key-atlas_footer_lock button {
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  color:#8399b2!important;
  padding:0 4px!important;
  min-height:30px!important;
  opacity:.6;
}
.st-key-atlas_footer_lock button:hover,
.st-key-atlas_footer_lock button:focus-visible {
  background:#132338!important;
  color:#d5e6f3!important;
  opacity:1;
}
.st-key-atlas_footer_lock button:focus-visible {outline:2px solid #6395b8!important;outline-offset:2px;}
@media(max-width:700px){.atlas-footer-text-right{text-align:left;}}

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

/* v4.5: Streamlit'in iki oklu gerçek KENAR MENÜ düğmesini anlaşılır hamburger olarak göster.
   Yalnızca görünümü değiştirir; yerleşik aç/kapat işlevi ve erişilebilir buton kalır.
   Birkaç Streamlit sürümünün test-id'si desteklenir. */
:is([data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"]) button,
button[data-testid="stSidebarCollapsedControl"], button[data-testid="stSidebarCollapseButton"], button[data-testid="stExpandSidebarButton"] {
  background:#842f3d!important; color:#fff9f8!important;
  border:1px solid #db6f72!important; border-radius:11px!important;
  min-height:37px!important; min-width:39px!important;
  display:inline-flex!important; align-items:center!important; justify-content:center!important;
  box-shadow:0 2px 12px rgba(214,84,95,.23)!important;
}
:is([data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"]) button:hover,
button[data-testid="stSidebarCollapsedControl"]:hover,
button[data-testid="stSidebarCollapseButton"]:hover, button[data-testid="stExpandSidebarButton"]:hover {background:#a8404b!important;}
:is([data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"]) button > *,
button[data-testid="stSidebarCollapsedControl"] > *,
button[data-testid="stSidebarCollapseButton"] > *, button[data-testid="stExpandSidebarButton"] > * {display:none!important;}
:is([data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"]) button::after,
button[data-testid="stSidebarCollapsedControl"]::after, button[data-testid="stExpandSidebarButton"]::after {
  content:"☰"; font-size:20px; line-height:1; font-weight:800; color:#fff!important;
}
[data-testid="stSidebarCollapseButton"] button::after,
button[data-testid="stSidebarCollapseButton"]::after {
  content:"✕"; font-size:16px; line-height:1; font-weight:700; color:#fff!important;
}
/* Analizler: v4.3'teki nötr açılır/kapanır menü tasarımına dönüş. */
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
  background:#101d30!important; border-radius:10px!important;
  border-color:#2b415a!important; color:#dce6f3!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {background:#1c3046!important;}
.atlas-selection-summary {padding:16px 19px; margin-top:3px; min-height:132px;
  background:linear-gradient(120deg,#112d3a,#14283a); border:1px solid #2c5767;
  border-radius:15px;}
.atlas-selection-summary .eyebrow{color:#80dbc8;font-weight:800;letter-spacing:.14em;font-size:10px;}
.atlas-selection-summary .winner{color:#f4fbff;font-weight:750;font-size:clamp(1.15rem,2.1vw,1.65rem);margin:7px 0 2px;}
.atlas-selection-summary .detail{color:#b6d6de;font-size:12px;}
.atlas-selection-summary .hint{color:#88a8bb;font-size:11px;line-height:1.55;margin-top:12px;}
/* v4.6: v4.2.1'deki orijinal TR / Yaşam / Ticaret / Afet yörünge görseli. */
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

/* Mevcut sade v4.5 kahraman bölümünde, metinle yörüngeyi dengeli yerleştir. */
.hero-return {display:flex;align-items:center;justify-content:space-between;gap:15px;min-height:0;}
.hero-return-copy {flex:1 1 0;min-width:0;}
.hero-return .atlas-orbit {flex:0 0 195px;width:195px;height:170px;margin:0 2px 0 8px;transform:scale(.78);transform-origin:center;}
@media(max-width:1020px) {
 .hero-return .atlas-orbit {flex:0 0 205px;width:205px;height:205px;margin:0;}
 .hero-return .orbit-center {inset:66px 65px 66px 64px;}
 .hero-return .orbit-node {font-size:10px;padding:10px;}
}
@media(max-width:750px){
 .hero-return {display:block;min-height:0;}
 /* Dar ekranlarda halkaları küçültmek yerine aynı dört etiketi okunabilir mini kartlara çevir. */
 .hero-return .atlas-orbit {display:flex;flex-wrap:wrap;align-items:center;
   width:100%;height:auto;min-height:0;gap:8px;margin:16px 0 0;}
 .hero-return .orbit-ring {display:none;}
 .hero-return .orbit-center {position:static;inset:auto;display:flex;flex-direction:column;
   width:auto;height:auto;padding:8px 12px;border-radius:11px;}
 .hero-return .orbit-center strong {font-size:15px;}
 .hero-return .orbit-center span {font-size:8px;}
 .hero-return .orbit-node {position:static;font-size:10px;padding:11px 12px;box-shadow:none;}
}
.hero-return {padding:14px 23px 13px; margin:0 0 9px; border-radius:16px;
  border:1px solid #31596b; background:linear-gradient(110deg,#173047 0%,#11243b 64%,#164152 100%);}
.hero-return .overline{letter-spacing:.16em;font-size:10px;}
.hero-return h1{font-family:'Space Grotesk',sans-serif!important;font-size:clamp(2rem,4vw,3.2rem)!important;
  font-weight:800;letter-spacing:-.065em;line-height:1.02;margin:6px 0 3px!important;}
.hero-return h1 em{font-style:normal;color:#71e6d9;}
.hero-return h2{font-size:clamp(1.15rem,2.2vw,1.65rem)!important;margin:4px 0 3px!important;}
.hero-return p{font-size:12px;color:#d9e8f4;max-width:950px;line-height:1.45;margin:3px 0;}
@media(max-width:670px){.hero-return{padding:16px 17px}.hero-return p{font-size:12px}}
/* v4.3 — sade ve farklı ekranlara uyumlu başlık, kart ve menü */
.compact-hero {border:1px solid #25435a; border-radius:17px; padding:19px 23px;
 background:linear-gradient(120deg,#132d40,#0e2034);margin:4px 0 17px;}
.compact-hero h1 {font-size:clamp(1.5rem,2.8vw,2.25rem)!important;line-height:1.16;
 margin:5px 0 7px!important;letter-spacing:-.045em;}
.compact-hero p {font-size:13px;color:#b2c7d8;max-width:860px;margin:0;line-height:1.55;}
.compact-hero .overline {font-size:10px;letter-spacing:.12em;}
/* Map filters stay next to the map (not inside the narrow left navigation). */
.filter-strip-title {display:flex;justify-content:space-between;gap:12px;align-items:center;
  padding:10px 13px 4px; margin:9px 0 0;
  font-size:11px;font-weight:800;letter-spacing:.12em;color:#82eadb;}
.filter-strip-title span {letter-spacing:normal;color:#8bafc1;font-weight:500;}
@media(max-width:670px){.filter-strip-title span{display:none;}}
.quick-facts {display:flex;gap:9px;flex-wrap:wrap;margin:6px 0 13px;}
.quick-facts span {background:#1a3854;border:1px solid #5694b6;color:#f4fbff;
 border-radius:12px;padding:9px 13px;font-size:13px;font-weight:800;
 box-shadow:0 3px 14px rgba(4,17,34,.25);}
.compact-summary {background:#102336;border:1px solid #2b4a60;border-radius:15px;
 padding:17px 20px;margin:12px 0 18px;}
.compact-summary h3 {font-size:1.24rem!important;margin:0 0 7px!important;}
.compact-summary p {font-size:13px;color:#bfd2df;margin:0 0 10px;line-height:1.65;}
.compact-summary strong {color:#e8fbf7;}
[data-testid="stSidebar"] [data-testid="stButton"] button {min-height:37px;}
[data-testid="stSidebar"] [data-testid="stExpander"] {border-radius:11px;}
[data-testid="stMetricValue"] {font-size:clamp(1.05rem,1.65vw,1.55rem)!important;}
[data-testid="stMetricLabel"] {font-size:.75rem!important;}
@media (max-width:1100px) {
 [data-testid="stMain"] .block-container {padding:.85rem 1.05rem 3rem;max-width:100%;}
 [data-testid="stHorizontalBlock"] {flex-wrap:wrap!important;gap:.85rem!important;}
 [data-testid="stHorizontalBlock"] [data-testid="stColumn"] {min-width:min(100%,300px)!important;flex:1 1 100%!important;width:100%!important;}
 .metrics{grid-template-columns:repeat(2,minmax(0,1fr));}
 .atlas-action{min-height:0;padding:13px 16px;}
}
@media (max-width:670px) {
 .compact-hero {padding:14px 16px;border-radius:14px;}
 .compact-summary{padding:13px;}
 [data-testid="stMain"] .block-container{padding:.75rem .75rem 2.6rem;}
 .overview-pane{padding:12px;}
 .metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
 .metric{padding:11px;min-height:85px;}.metric-value{font-size:1.5rem;}
}

/* v4.7: Navigasyon hiyerarşisi — analizler mavi, diğer menü düğmeleri kırmızı. */
[data-testid="stSidebar"] [data-testid="stButton"] button {
 background:#df4059!important; border:1px solid #fb7284!important;
 color:#ffffff!important; border-radius:12px!important;
 min-height:43px!important; transition:background .15s,border-color .15s!important;
 box-shadow:0 3px 12px rgba(229,65,87,.13)!important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
 background:#f04e66!important; border-color:#ff9bab!important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button p,
[data-testid="stSidebar"] [data-testid="stButton"] button span {
 font-size:15px!important; font-weight:750!important; letter-spacing:.008em!important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
 background:#f04e66!important; border-color:#ffafb8!important;
}
/* Analizler bölümü: kendi alt sayfalarıyla birlikte aydınlık mavi. */
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
 background:#204b76!important; border:1px solid #438bc1!important;
 border-radius:12px!important; color:#f1f8ff!important; padding:11px 13px!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
 background:#2b608f!important; border-color:#73b9ee!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
 font-size:15px!important;font-weight:800!important; color:#f2f9ff!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stButton"] button {
 background:#193d62!important; border-color:#3b76a9!important; color:#e4f4ff!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stButton"] button:hover {
 background:#275986!important; border-color:#6bb0e4!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stButton"] button[kind="primary"] {
 background:#3475ad!important; border-color:#9bd4fa!important;
}
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


def github_kod_deposu_baglantisi() -> str:
    """Güvenli biçimde yalnızca projenin açıkça yapılandırılmış GitHub URL'sini göster."""
    from urllib.parse import urlsplit
    try:
        value = str(st.secrets.get('AFET_ATLAS_KOD_REPOSU', '')).strip()
    except (FileNotFoundError, KeyError):
        value = ''
    # Afet Atlas'ın ziyaretçilere açık kaynak kod deposu; ayrı özel veri deposu değildir.
    value = value or os.environ.get('AFET_ATLAS_KOD_REPOSU', '').strip()
    value = value or 'https://github.com/utkuerekinci/afet-atlas'
    try:
        parsed = urlsplit(value)
    except ValueError:
        return ''
    sections = [part for part in parsed.path.split('/') if part]
    if (parsed.scheme == 'https' and parsed.netloc.lower() == 'github.com'
            and len(sections) == 2 and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment):
        return value.rstrip('/')
    return ''







# Tüm kullanıcılar için sabit koyu tema (istemci sistem temasından bağımsız).
st.markdown("""<style>
:root,html,body,.stApp,[data-testid="stAppViewContainer"]{color-scheme:dark!important;
 --background-color:#080f1d;--secondary-background-color:#111e31;
 --text-color:#dce6f3;--primary-color:#65e6d5}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"]{background-color:#080f1d!important;color:#dce6f3!important}
[data-testid="stHeader"]{background:#080f1d!important}
.atlas-brand{font:700 25px 'Space Grotesk',sans-serif;color:#f0f8ff;letter-spacing:-.035em;margin:0 0 12px}
.atlas-brand b{color:#71e5da}.atlas-brand-dot{color:#71e5da}
.atlas-brand small{font:500 10px 'DM Sans',sans-serif;letter-spacing:.15em;color:#89a5bc;margin-left:14px}
.st-key-atlas_desktop_nav{background:#101d30;border:1px solid #273b51;border-radius:15px;padding:6px 8px 0;margin-bottom:20px}
.st-key-atlas_desktop_nav button{min-height:40px!important;padding:.3rem .25rem!important;font-size:.75rem!important;white-space:nowrap!important;border-radius:9px!important}
@media(min-width:901px){
 [data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
 [data-testid="stMain"] .block-container{padding-top:1.5rem!important}
}
@media(max-width:900px){
 .st-key-atlas_desktop_nav{display:none!important}
 .atlas-brand{padding-left:36px;font-size:21px}.atlas-brand small{display:block;margin:3px 0 0;font-size:9px}
 [data-testid="stMain"] .block-container{padding-left:1rem!important;padding-right:1rem!important}
}

/* Genel Bakış: dört combobox her genişlikte aynı yatay satırda kalır. */
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] {
 display:flex!important; flex-wrap:nowrap!important; align-items:flex-start!important;
 gap:.55rem!important;
}
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
 flex:1 1 0!important; width:0!important; min-width:0!important;
}
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {flex:1.08 1 0!important;}
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {flex:1.08 1 0!important;}
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {flex:.93 1 0!important;}
.stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) {flex:1.11 1 0!important;}
.stApp .st-key-home_filter_row [data-testid="stSelectbox"] {min-width:0!important;}
.stApp .st-key-home_filter_row [data-testid="stSelectbox"] [role="group"] {min-width:0!important;}
.stApp .st-key-home_filter_row [data-testid="stSelectbox"] label p {font-size:12px!important;}
.stApp .st-key-home_filter_row [data-testid="stSelectbox"] input {font-size:13px!important;}
@media(max-width:760px){
 .stApp .st-key-home_filter_row {overflow-x:auto!important;}
 .stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] {min-width:710px!important;}
 .stApp .st-key-home_filter_row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  min-width:155px!important;flex:1 1 155px!important;width:auto!important;
 }
}

/* Genel bakış açıklaması üst başlıkla birleşir; harita ilk ekranda görünür. */
.atlas-brand{margin-bottom:5px!important;}
.atlas-inline-intro {font-size:12.5px;line-height:1.45;color:#c7d9e8;
 margin:-1px 0 8px;max-width:1150px;}
.atlas-inline-intro strong{color:#f3f8ff;font-weight:750;}
@media(max-width:700px){.atlas-inline-intro{font-size:11.5px;line-height:1.35;margin-bottom:6px;}}
</style>""",unsafe_allow_html=True)

# ---------- v4.3: yerleşik hamburger ile açılan menü + katlanabilir analizler ----------
MODULES=['Genel Bakış','Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel','Siz Sorun','Yardım','Veri ve Yöntem','Hakkımızda','Yönetici Girişi']
if 'secilen_il' not in st.session_state:
    st.session_state['secilen_il']='Ankara'
if st.session_state.get('v34_bolum') not in MODULES:
    st.session_state['v34_bolum']='Genel Bakış'
module=st.session_state['v34_bolum']


def git_modul(target: str) -> None:
    st.session_state['v34_bolum']=target
    st.rerun()



# Masaüstünde yatay navigasyon; küçük ekranda yerleşik hamburger menü.
st.markdown(
    '<div class="atlas-brand"><span class="atlas-brand-dot">◉</span> AFET <b>ATLAS</b>'
    '<small> TÜRKİYE BÖLGESEL ANALİZ PLATFORMU</small></div>'
    + ('<div class="atlas-inline-intro"><strong>Türkiye’nin haritasından fazlası.</strong> '
       'Nerede yaşamak isterdin? Hangi bölgede yeni bir iş kurardın? '
       'Doğal afetler hangi illerde öne çıkıyor? Türkiye’yi yaşam, ticaret ve afet '
       'perspektiflerinden keşfet; ilçelerin hikâyesini verilerle karşılaştır.</div>'
       if module == 'Genel Bakış' else ''),
    unsafe_allow_html=True,
)
with st.container(key='atlas_desktop_nav'):
    nav_items = ['Genel Bakış','Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel',
                 'Siz Sorun','Yardım','Veri ve Yöntem','Hakkımızda']
    nav_cols=st.columns([1.05,1.1,1.18,1.35,.83,.75,1.28,.96],gap='small')
    for index, target in enumerate(nav_items):
        with nav_cols[index]:
            if st.button(target,key='top_nav_'+str(index),
                         type='primary' if module==target else 'secondary',
                         use_container_width=True):
                git_modul(target)


with st.sidebar:
    st.markdown('<div class="overline"><span class="dot"></span> BBY261 · İLERİ PROGRAMLAMA</div>'
                '<div class="sidebar-head">AFET ATLAS</div>'
                '<div class="sidebar-small">☰ Menü · Bölümler</div>',unsafe_allow_html=True)
    if st.button('⌂  Genel Bakış',key='nav_home',type='primary' if module=='Genel Bakış' else 'secondary',use_container_width=True):
        git_modul('Genel Bakış')
    with st.expander('▾  Analizler',expanded=module in ('Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel')):
        for caption,target in [('🌦️ Afet Analizi','Afet Analizi'),('🏡 Yaşam Kalitesi','Yaşam Kalitesi'),('🏪 Ticari Potansiyel','Ticari Potansiyel')]:
            if st.button(caption,key='nav_'+target,type='primary' if module==target else 'secondary',use_container_width=True):
                git_modul(target)
    # v4.6: v4.5'te yanlışlıkla görünmez hâle gelen üç sayfa bağlantısı geri getirildi.
    # Veri ve Yöntem ve Yardım sayfalarının kendisi zaten mevcut; menü düğmeleri eksikti.
    for caption,target in [('✦  Siz Sorun','Siz Sorun'),('ⓘ  Yardım','Yardım'),
                           ('▤  Veri ve Yöntem','Veri ve Yöntem')]:
        if st.button(caption,key='nav_'+target,
                     type='primary' if module==target else 'secondary',
                     use_container_width=True):
            git_modul(target)
    if st.button('ⓘ  Hakkımızda',key='nav_about',use_container_width=True):
        git_modul('Hakkımızda')
    st.caption('Seçili il: '+st.session_state.get('secilen_il','Ankara'))
    # Afet türü ve deprem filtreleri v4.5'teki gibi haritanın yakınında kalır.

# BaseWeb selectbox, acilir yardim ve Gemini butonlari: koyu tema ortak kontrol stili.
st.markdown(ortak_kontrol_css(),unsafe_allow_html=True)
kaydirma_butonu()


def deprem_kapsami() -> tuple[int,int,float,int]:
    """Deprem filtresi için varsayılan ve sayfalar arası güvenli değerler."""
    return (int(st.session_state.get('_atlas_y0', 2025)),
            int(st.session_state.get('_atlas_y1', 2025)),
            float(st.session_state.get('_atlas_m', 4.5)),
            int(st.session_state.get('_atlas_mesafe', 0)))


def deprem_filtreleri() -> tuple[int,int,float,int]:
    """USGS/ArcGIS örneklerindeki gibi haritanın üstünde kompakt filtre şeridi."""
    years=list(range(2015,date.today().year+1))
    fallback_y0, fallback_y1, fallback_m, fallback_d=deprem_kapsami()
    # Yıl değişince bitiş yılı otomatik olarak geçerli aralıkta tutulur.
    banner,reset=st.columns([4.6,1],gap='small',vertical_alignment='center')
    with banner:
        st.markdown('<div class="filter-strip-title">◉ HARİTA FİLTRELERİ <span>Yıl, büyüklük ve yakınlık</span></div>',unsafe_allow_html=True)
    with reset:
        if st.button('↺ Sıfırla',key='v45_reset_deprem',help='2025 yılı ve M ≥ 4.5 başlangıç filtrelerine dön.',use_container_width=True):
            for key in ('v45_year_start','v45_year_end','v45_min_m','v45_distance'):
                st.session_state.pop(key,None)
            st.session_state.update(_atlas_y0=2025,_atlas_y1=2025,_atlas_m=4.5,_atlas_mesafe=0)
            st.rerun()
    a,b,c,d=st.columns([1,1,1,1],gap='small')
    with a:
        y0=st.selectbox('Başlangıç yılı', years,
                        index=years.index(fallback_y0) if fallback_y0 in years else years.index(2025),
                        key='v45_year_start',filter_mode=None)
    with b:
        valid=[v for v in years if v>=y0]
        last=fallback_y1 if fallback_y1 in valid else max(y0,2025)
        y1=st.selectbox('Bitiş yılı',valid,index=valid.index(last),key='v45_year_end',filter_mode=None)
    with c:
        magnitudes=[4.5,5.0]
        m=st.selectbox('Minimum büyüklük',magnitudes,
                       index=magnitudes.index(fallback_m) if fallback_m in magnitudes else 0,
                       key='v45_min_m',filter_mode=None)
    with d:
        distances=[0,50,75,100,150]
        distance=st.selectbox('İl sınırına yakınlık (km)',distances,
                              index=distances.index(fallback_d) if fallback_d in distances else 0,
                              key='v45_distance',filter_mode=None)
    st.session_state.update(_atlas_y0=y0,_atlas_y1=y1,_atlas_m=m,_atlas_mesafe=distance)
    return y0,y1,m,distance



def heading(section: str, text: str, description: str, overview: bool=False):
    """Sabit büyük radar yerine her çözünürlükte kısa, anlaşılır sayfa başlığı."""
    title='Türkiye’yi keşfet.' if overview else text
    st.markdown(
        '<section class="compact-hero">'
        f'<div class="overline">{escape(section)}</div>'
        f'<h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></section>',
        unsafe_allow_html=True,
    )


def yardim_ipucu(konu: str) -> None:
    metinler={
        'Genel Bakış': 'Yaşam, Ticaret veya Afet seç. Göstergenin değişmesi haritayı günceller. Bir ilin renkli alanına tıklayarak kısa özetini aç, ardından Ayrıntıya Git ile devam et.',
        'Afet Analizi': 'Afet Analizi sayfasının başındaki Afet türü alanından konuyu seç. Deprem için başlangıç ve bitiş yılı, minimum büyüklük ve il sınırı yakınlığı filtreleri haritanın hemen üstünde bulunur. Haritada bir ile tıkla, kayıtlarını aşağıda incele.',
        'Yaşam Kalitesi': 'Şehri ve yaşam tercihini seç. Seçilen il için Neden Bu İlçe Birinci? açıklaması sağdadır. Aşağı kaydırıp Türkiye genelindeki veya il içindeki enleri ve İki ilçeyi karşılaştır bölümünü aç; önce il, ardından ilçe seç. Çubukların üzerine gelerek puanları incele.',
        'Ticari Potansiyel': 'İl ve sektör seç. Harita göstergesinde sektörel fırsat puanını, nüfusu, gelişmişliği veya OSM kayıtlarını inceleyebilirsin. Neden Bu İlçe Birinci? açıklaması sağdadır. Aşağı kaydırıp İki ilçeyi karşılaştır bölümünde önce il, ardından ilçe seç. İşletme sayılarını açılır bölümde görebilirsin.',
        'Siz Sorun': 'Örnek soru seç veya kendi sorunu yaz. Soruyu Gönder düğmesiyle Afet Atlas asistanından cevap al.',
        'Veri ve Yöntem': 'Veri kaynaklarını ve puanlamanın nasıl yapıldığını bu bölümde inceleyebilirsin.',
    }
    # Sabit CSS anahtari: acilir yardim dugmesi her iki temada kirmizi kalir.
    with st.container(key='atlas_help_trigger'):
        with st.popover('ⓘ Nasıl kullanılır?',use_container_width=False):
            st.write(metinler.get(konu,'Bu sayfadaki göstergeleri seçerek karşılaştırma yapabilirsin.'))
            if st.button('Yardım sayfasını aç',key='help_from_'+konu):
                git_modul('Yardım')


def deprem_bul(y0:int,y1:int,m:float,d:int):
    sinirlar,depremler=verileri_yukle(y0,y1,m)
    iller,eslesenler=hesapla(depremler,sinirlar,d)
    return sinirlar,depremler,iller,eslesenler


def dis_dashboard(geo,depremler,illers,eslesenler,overview=False):
    """Harita, seçilen ilin gerçek deprem kayıtları ve ikincil ülke karşılaştırması."""
    st.markdown('<div class="quick-facts">'
                f'<span>{len(depremler)} deprem kaydı</span><span>81 il</span>'
                f'<span>En büyük M {depremler.mag.max():.1f}</span>'
                f'<span>{len(eslesenler)} il-olay eşleşmesi</span></div>',unsafe_allow_html=True)
    display=illers[['İl','Toplam puan','Deprem sayısı','Karşılaştırma endeksi']].copy()
    selected=il_secimi(sorted(display.İl),'overview' if overview else 'disaster',label='Haritada incelenecek il')
    map_column, info_column=st.columns([2.1,1],gap='medium')
    with map_column:
        ortak_harita(geo,display,'Toplam puan','Olay puanı','overview' if overview else 'disaster')
    selected=st.session_state.get('secilen_il',selected)
    with info_column:
      with st.container(border=True):
        province=display.set_index('İl').loc[selected]
        st.markdown('### 📍 '+escape(selected))
        a,b=st.columns(2)
        a.metric('Olay puanı',int(province['Toplam puan']))
        b.metric('Eşleşen deprem',int(province['Deprem sayısı']))
        st.write(f"{selected} için seçilen zaman ve yakınlık filtrelerinde "
                 f"{int(province['Deprem sayısı'])} eşleşen deprem bulunuyor.")
        st.markdown('#### '+selected+' · Deprem kayıtları')
        recent=secilen_il_kayitlari(eslesenler,selected)
        if recent.empty:
            st.info('Seçilen filtrelerde bu il için kayıt bulunmadı.')
        else:
            st.dataframe(recent.head(8),hide_index=True,use_container_width=True,
                         height=min(350,80+35*min(len(recent),8)))
            if len(recent)>8:
                with st.expander(f'Tüm {len(recent)} kaydı görüntüle'):
                    st.dataframe(recent,hide_index=True,use_container_width=True)
        gemini_yorum_butonu({
            'konu':'Deprem hareketliliği il profili', 'il':selected,
            'veri_yillari':[int(y0),int(y1)], 'minimum_buyukluk':float(m),
            'il_sinir_mesafesi_km':int(distance),
            'il_gostergeleri':{'deprem_sayisi':int(province['Deprem sayısı']),
                              'olay_puani':float(province['Toplam puan'])},
            'ulke_karsilastirma':display.sort_values('Toplam puan',ascending=False).head(5).to_dict('records'),
            'not':'Bu puan tarihsel deprem hareketliliğidir; güvenlik olasılığı değildir.',
        },key='deprem_'+selected)
        il_paneli_gecisleri('Afet Analizi',key='deprem')
    if not overview:
        t1,t2=st.tabs(['İl sıralaması','Hareketliliği en yüksek 5 il'])
        with t1:
            positive=illers[illers['Deprem sayısı']>0]
            st.dataframe(positive[['Sıra','İl','Deprem sayısı','En büyük deprem','Toplam puan','Karşılaştırma endeksi']],
                         hide_index=True,use_container_width=True)
            with st.expander('Eşleşen depremi olmayan iller'):
                st.dataframe(illers.loc[illers['Deprem sayısı']==0,['İl','Deprem sayısı']],hide_index=True,use_container_width=True)
        with t2:
            st.dataframe(hareketliligi_yuksek_bes_il(display),hide_index=True,use_container_width=True)


if module=='Genel Bakış':
    yardim_ipucu('Genel Bakış')
    try:
        with st.spinner('Türkiye atlası hazırlanıyor...'):
            raw, overview_status=veri_yukle()
            if raw is None:
                st.stop()
            geo=il_sinirlari()
            districts,provinces=prepare_provinces(raw,geo)
        # Genel Bakış filtreleri tek satırda, soldan sağa aynı hizada kalır.
        # Dar ekranlarda yatay kaydırılır; diğer ekranların sütunları etkilenmez.
        with st.container(key='home_filter_row'):
            topic_column,filter_column,city_column,district_column=st.columns([1.08,1.08,0.93,1.11],gap='small')
            with topic_column:
                topic=st.selectbox('Keşif alanı',OVERVIEW_TOPICS,key='home_v40_topic',filter_mode=None)
            labels=available_layers(provinces,topic)
            if labels:
                with filter_column:
                    layer=st.selectbox('Harita göstergesi',labels,key='home_v40_layer_'+topic,
                                       help='Haritada renklendirilecek veriyi seç.',filter_mode=None)
                with city_column:
                    city=il_secimi(sorted(provinces['İl'].tolist()),'home_v40',label='Şehir ara / seç')
                with district_column:
                    ilce_arama(districts,'home_v40',label='İlçe ile il bul')
        if not labels:
            st.caption('Bu keşif alanına ait harita verisi bulunamadı.')
        else:
            layer_data,layer_col,layer_text=layer_frame(provinces,topic,layer)
            map_column, info_column=st.columns([2.2,1],gap='medium')
            with map_column:
                ortak_harita(geo,layer_data,layer_col,layer_text,'home_v40')
            city=st.session_state.get('secilen_il',city)
            details=city_summary(districts,provinces,city,topic,layer,
                                 safety_snapshot=layer_data if topic=='Doğal afetler' else None)
            population_text=f'{details["nufus"]:,}'.replace(',','.')
            words=str(details['text']).split('. ')
            short='.'.join([]) if not words else '. '.join(words[:2]).rstrip('.')+'.'
            with info_column:
                with st.container(border=True):
                    st.markdown(f'### 📍 {escape(city)}')
                    st.markdown(f'<div class="quick-facts"><span>{population_text} nüfus</span><span>{details["ilce"]} ilçe</span></div>',unsafe_allow_html=True)
                    fact_col, learn_col = st.columns([1.1, 1.25], gap='small', vertical_alignment='center')
                    with fact_col:
                        st.markdown(f'<div class="quick-facts"><span>{escape(str(details["key_label"]))}: {escape(str(details["key_value"]))}</span></div>',unsafe_allow_html=True)
                    with learn_col:
                        extra_text = genel_bakis_detay_kontrolu(
                            il_baglam(districts,provinces,city,topic,layer,details),
                            key='home_city',
                        )
                    # Ayrıntı, kısa açıklamanın yerini alır; yanına veya altına
                    # ikinci kez yazılmaz. Kapatınca Python açıklaması geri gelir.
                    st.write(extra_text if extra_text else short)
                    st.markdown('**Bu ili analiz et**')
                    for idx,target in enumerate(('Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel')):
                        if st.button(target+' →',key='home_city_nav_'+str(idx),use_container_width=True, type='primary'):
                            git_modul(target)
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Genel Bakış haritası oluşturulamadı')
        st.caption('Harita verileri yüklenemedi. Sayfayı yeniden açmayı dene.')

elif module=='Yaşam Kalitesi':
    yardim_ipucu('Yaşam Kalitesi')
    yasam_ticaret_sayfasi('yasam')

elif module=='Ticari Potansiyel':
    yardim_ipucu('Ticari Potansiyel')
    yasam_ticaret_sayfasi('ticaret')

elif module=='Afet Analizi':
    yardim_ipucu('Afet Analizi')
    disaster=st.selectbox(
        'Afet türü', ['Deprem','Orman yangını','Sel / taşkın','Heyelan','Çığ','Fırtına','Kuraklık'],
        key='v36_disaster',help='Haritadaki afet verisi türünü seç.',filter_mode=None)
    if disaster!='Deprem':
        diger_afet_sayfasi(disaster)
    else:
        st.markdown('#### Türkiye haritası · Deprem hareketliliği')
        y0,y1,m,distance=deprem_filtreleri()
        try:
            with st.spinner('USGS deprem analizi yapılıyor...'):
                geo,depremler,illers,eslesenler=deprem_bul(y0,y1,m,distance)
            dis_dashboard(geo,depremler,illers,eslesenler)
        except Exception as exc:st.error('Deprem verisi yüklenemedi.');st.code(str(exc))

elif module=='Siz Sorun':
    y0,y1,m,distance=deprem_kapsami()
    yardim_ipucu('Siz Sorun')
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
        '2024 yağışları hangi coğrafi bölgelerde normale göre azdı?'],
        key='adk_example_question',filter_mode=None)
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

elif module=='Yönetici Girişi':
    from atlas_yonetim_ui import admin_page
    admin_page(_atlas_data_settings)

elif module=='Hakkımızda':
    st.markdown("""
    <style>
    .atlas-about {color:#dbe8f4;}
    .atlas-about .about-intro {
        background:linear-gradient(115deg,#15243a 0%,#102133 70%,#182638 100%);
        border:1px solid #34475b;border-radius:22px;padding:24px 28px 23px;
        margin:2px 0 17px;
    }
    .atlas-about .about-eyebrow {color:#ff8192;font-size:11px;letter-spacing:.17em;
        font-weight:800;text-transform:uppercase;margin:0 0 9px;}
    .atlas-about .about-title {font-size:clamp(23px,3vw,34px);font-weight:800;
        line-height:1.16;letter-spacing:-.045em;color:#f5f9ff;margin:0 0 10px;}
    .atlas-about .about-intro p {color:#bacbda;line-height:1.65;max-width:920px;
        font-size:14px;margin:0;}
    .atlas-about .about-stats {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
        gap:12px;margin:0 0 20px;}
    .atlas-about .about-stat {background:linear-gradient(145deg,#271a2b,#171e31 80%);
        border:1px solid #853d53;border-radius:17px;padding:17px 19px;
        box-shadow:inset 3px 0 0 #f04e66;min-height:109px;}
    .atlas-about .stat-number {display:block;color:#ff647a;font:800 clamp(29px,4vw,43px)/1.05 'Space Grotesk',sans-serif;
        letter-spacing:-.05em;margin-bottom:8px;}
    .atlas-about .stat-label {font-size:13px;font-weight:750;color:#f6e2e8;}
    .atlas-about .about-section-title {color:#eef6ff;font-size:17px;
        font-weight:800;margin:7px 0 13px;letter-spacing:-.025em;}
    .atlas-about .about-modules {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:18px;}
    .atlas-about .about-module {background:#101e30;border:1px solid #304258;
        border-radius:16px;padding:17px 18px;min-height:154px;}
    .atlas-about .about-module .index {font-size:11px;font-weight:800;
        color:#ff8292;letter-spacing:.13em;margin-bottom:11px;}
    .atlas-about .about-module h4 {font-size:16px;font-weight:800;color:#f0f7ff;margin:0 0 9px;}
    .atlas-about .about-module p {font-size:13px;line-height:1.58;color:#b7cad9;margin:0;}
    .atlas-about .about-footer {display:grid;grid-template-columns:1fr 1fr;
        gap:12px;margin:4px 0 12px;}
    .atlas-about .about-small {background:#101e30;border:1px solid #304258;
        border-radius:15px;padding:17px 19px;}
    .atlas-about .about-small strong {display:block;color:#f0f7ff;font-size:14px;margin-bottom:7px;}
    .atlas-about .about-small p {color:#b7cad9;font-size:13px;line-height:1.6;margin:0;}
    .atlas-about .about-warning {background:#261b2b;border-color:#95465b;}
    .atlas-about .about-warning strong {color:#ff9aab;}
    @media(max-width:850px){
        .atlas-about .about-stats{grid-template-columns:repeat(2,minmax(0,1fr));}
        .atlas-about .about-modules{grid-template-columns:1fr;}
        .atlas-about .about-footer{grid-template-columns:1fr;}
    }
    @media(max-width:500px){
        .atlas-about .about-intro{padding:20px 18px;}
        .atlas-about .about-stat{padding:14px;min-height:94px;}
    }
    </style>
    <div class="atlas-about">
      <div class="about-intro">
        <div class="about-eyebrow">Afet Atlas · Proje hakkında</div>
        <div class="about-title">Türkiye'yi verilerle keşfet.</div>
        <p>Afet Atlas; doğal afet göstergelerini, yaşam koşullarını ve ticari potansiyeli
        Türkiye haritası üzerinde bir araya getiren karşılaştırmalı analiz platformudur.
        İllerden ilçelere uzanan verileri inceleyebilir, farklı bölgeleri karşılaştırabilir
        ve yapay zekâ destekli açıklamalardan yararlanabilirsin.</p>
      </div>
      <div class="about-stats">
        <div class="about-stat"><span class="stat-number">81</span><span class="stat-label">İl</span></div>
        <div class="about-stat"><span class="stat-number">973</span><span class="stat-label">İlçe</span></div>
        <div class="about-stat"><span class="stat-number">7</span><span class="stat-label">Afet türü</span></div>
        <div class="about-stat"><span class="stat-number">4</span><span class="stat-label">Ticari sektör</span></div>
      </div>
      <div class="about-section-title">Platformda neler var?</div>
      <div class="about-modules">
        <div class="about-module"><div class="index">01 / AFET</div>
          <h4>Afet Analizi</h4>
          <p>81 il için tarihsel deprem hareketliliği ve kaynaklı doğal afet göstergelerini
          harita üzerinde incele.</p></div>
        <div class="about-module"><div class="index">02 / YAŞAM</div>
          <h4>Yaşam Kalitesi</h4>
          <p>İlçe nüfusu, sosyoekonomik göstergeler ve yaşam tercihleri üzerinden
          yerleşim bölgelerini karşılaştır.</p></div>
        <div class="about-module"><div class="index">03 / TİCARET</div>
          <h4>Ticari Potansiyel</h4>
          <p>Dört sektörde ilçe bazlı fırsat puanlarını ve mevcut veri kapsamındaki
          ticari göstergeleri keşfet.</p></div>
      </div>
      <div class="about-footer">
        <div class="about-small"><strong>Yapay zekâ destekli keşif</strong>
          <p>Siz Sorun bölümünden doğal dilde sorular sorabilir ve mevcut verilere
          dayalı açıklamaları inceleyebilirsin.</p></div>
        <div class="about-small about-warning"><strong>Verileri nasıl yorumlamalı?</strong>
          <p>Afet skorları bilimsel güvenlik olasılığı, ticari puanlar ise yatırım
          garantisi veya gerçek müşteri talebi tahmini değildir. Kaynaklar ve model
          sınırlılıkları Veri ve Yöntem bölümünde açıklanır.</p></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button('↗ GitHub kaynak kodunu görüntüle','https://github.com/utkuerekinci/afet-atlas')

elif module=='Yardım':
    st.markdown('#### Başlamak için')
    st.write('Masaüstünde üst menüyü; mobilde sol üstteki menü simgesini kullanarak bölümleri açabilirsin.')
    steps=[
        ('1 · Haritayı keşfet','Genel Bakış sayfasında Yaşam, Ticaret veya Afet seç. Yaşam göstergelerini değiştirebilir, Ticaret haritasında dört sektörün ortalama puanını ve Afet bölümünde illerin güvenlik skorlarını karşılaştırabilirsin. Bir ilin renkli alanına tıkla; harita sürüklenmez.'),
        ('2 · İl ayrıntılarına geç','Kısa il özetinin altındaki Ayrıntıya Git düğmesine bas. Aynı il ilgili analiz sayfasında korunur.'),
        ('3 · Afetleri incele','Menüden Analizler → Afet Analizi bölümünü seç. Açılan sayfada Afet türünü belirle. Deprem için yıl, büyüklük ve yakınlık filtrelerini haritanın üstünden ayarla. Seçtiğin ilin deprem kayıtları haritanın hemen altında görünür.'),
        ('4 · Yaşam koşullarını karşılaştır','Yaşam Kalitesi bölümünde şehir ve yaşam tercihini seç. Birincilik açıklaması tercihin yanında gösterilir. Aşağı kaydırıp Türkiye veya il içi sıralamalardaki İki ilçeyi karşılaştır alanında önce il, ardından ilçe seç.'),
        ('5 · Ticari potansiyeli keşfet','Ticari Potansiyel bölümünde sektörünü seç. Harita göstergelerinden fırsat puanı, nüfus, SEGE veya OSM kayıtlarını incele. Aşağı kaydırarak İki ilçeyi karşılaştır bölümünde önce il, sonra ilçe seç; işletme sayılarını açılır bölümden incele.'),
        ('6 · Sonuçları yorumla','Yaşam ve ticarette seçili ilin birincilik açıklaması tercih veya sektör seçiminin yanında görünür. Aşağı kaydırarak İki ilçeyi karşılaştır bölümüne geç. Daha fazla bilgi için Gemini düğmesine bas.'),
        ('7 · Asistana soru sor','Siz Sorun bölümünde örnek sorulardan birini seç veya kendi sorunu yaz. Soruyu Gönder düğmesini kullan.'),
    ]
    for title,text in steps:
        with st.expander(title,expanded=title.startswith('1')):
            st.write(text)
    st.markdown('#### Sık sorulan sorular')
    with st.expander('Harita neden sürüklenmiyor?'):
        st.write('Harita seçimi kolaylaştırmak için sabit tutulur. Bir ilin herhangi bir renkli alanına tıklayabilir veya şehir seçim kutusunu kullanabilirsin.')
    with st.expander('İlçe sıralamaları nerede?'):
        st.write('Yaşam Kalitesi ve Ticari Potansiyel sayfalarında aşağı kaydır; Türkiye geneli ve Seçilen ildeki enler sekmelerini incele. İki ilçeyi karşılaştır bölümünde önce il, sonra ilçe seç.')
    with st.expander('Gemini yorumu nasıl çalışır?'):
        st.write('Yalnızca Gemini ile daha fazla bilgi düğmesine basınca çalışır. İstersen mevcut Python açıklamalarını da okuyabilirsin.')
    with st.expander('Yönetici paneli herkese açık mı?'):
        st.write('Yönetici giriş sayfasına herkes ulaşabilir, ancak veri ekleme, güncelleme, yayından kaldırma ve geri alma işlemleri yalnızca yetkili yönetici hesabının kullanıcı adı ve şifresiyle giriş yapıldığında kullanılabilir.')
    st.markdown('#### Proje ve kaynak kod')
    st.write('Afet Atlas\'ın geliştirme dosyalarını, proje açıklamalarını ve sürüm geçmişini GitHub üzerinden inceleyebilirsin.')
    repo_link = github_kod_deposu_baglantisi()
    if repo_link:
        st.link_button('↗ GitHub’da kaynak kodu görüntüle', repo_link, use_container_width=True)
    else:
        st.caption('Kaynak kod bağlantısı, proje GitHub adresi tanımlandığında burada görünecek.')
    if st.button('Haritaya dön',type='primary',key='v43_back_home'):
        git_modul('Genel Bakış')

else:
    yardim_ipucu('Veri ve Yöntem')
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
- **Afet güvenlik skoru:** 81 il için deprem %30, orman yangını %20, sel %12, heyelan %10, çığ %6, fırtına %10 ve kuraklık %12 ağırlıklarıyla oluşturulur. USGS 2025 deprem kayıtları, 2024–2025 yangın kayıtları ve MGM 2024 afet/yağış raporları kullanılır. Raporlarda adı geçmeyen illerde olay sayısı sıfır varsayılmaz.
- **“Neden Bu İlçe Birinci?”** sıralama, ağırlık ve katkılardan otomatik hesaplanır.
""")

# Yönetici girişi yalnızca ana sayfanın en altındaki küçük kilitte görünür.
# Buton gerçek bir Streamlit widget'ıdır: session_state üzerinden yönetici ekranını açar.
if module == 'Genel Bakış':
    st.markdown('<div class="atlas-footer-rule"></div>', unsafe_allow_html=True)
    footer_left, footer_lock, footer_right = st.columns(
        [3.5, 0.35, 3.2], gap='small', vertical_alignment='center'
    )
    with footer_left:
        st.markdown('<div class="atlas-footer-text">◉ AFET ATLAS · TÜRKİYE BÖLGESEL ANALİZ</div>',
                    unsafe_allow_html=True)
    with footer_lock:
        with st.container(key='atlas_footer_lock'):
            if st.button('🔒', key='footer_admin', type='tertiary',
                         help='Yönetici girişi'):
                git_modul('Yönetici Girişi')
    with footer_right:
        st.markdown('<div class="atlas-footer-text atlas-footer-text-right">BBY261 · Python · Google ADK · Gemini · v4.12</div>',
                    unsafe_allow_html=True)
else:
    st.markdown('<div class="footer-brand"><span>◉ AFET ATLAS · TÜRKİYE BÖLGESEL ANALİZ</span><span>BBY261 · Python · Google ADK · Gemini · v4.12</span></div>',
                unsafe_allow_html=True)
