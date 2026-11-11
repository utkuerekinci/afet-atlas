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

st.set_page_config(
    page_title="Afet Atlas | Türkiye Doğal Afet Analiz Platformu",
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


# ---------- Kontrol merkezi ----------
with st.sidebar:
    st.markdown('<div class="overline"><span class="dot"></span> BBY261 · DEPREM MODÜLÜ</div>'
                '<div class="sidebar-head">AFET ATLAS</div>'
                '<div class="sidebar-small">Türkiye Doğal Afet Analiz Platformu</div>'
                '<div class="sidebar-label">ANALİZ AYARLARI</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">01 / ZAMAN ARALIĞI</div>', unsafe_allow_html=True)
    guncel_yil = date.today().year
    yillar = list(range(2015, guncel_yil + 1))
    varsayilan_yil = 2025 if 2025 in yillar else yillar[-1]
    baslangic = st.selectbox("Başlangıç yılı", yillar, index=yillar.index(varsayilan_yil))
    bitis_yillari = [y for y in yillar if y >= baslangic]
    bitis_default = max(varsayilan_yil, baslangic)
    bitis = st.selectbox("Bitiş yılı", bitis_yillari, index=bitis_yillari.index(bitis_default))

    st.markdown('<div class="sidebar-label">02 / OLAY FİLTRELERİ</div>', unsafe_allow_html=True)
    minimum = st.selectbox("Minimum deprem büyüklüğü", [4.5, 5.0], index=0)
    mesafe = st.select_slider(
        "İl sınırına yakınlık",
        options=[0, 50, 75, 100, 150],
        value=0,
        format_func=lambda km: f"{km} km",
        help="0 km yalnızca merkez üssü ilin sınırları içinde kalan depremleri sayar.",
    )
    st.caption(f"Seçili yakınlık: **{mesafe} km**. 0 km, yalnızca il sınırı içini kapsar.")

    st.markdown('<div class="sidebar-label">03 / OLAY AĞIRLIKLARI</div>'
                '<div class="sidebar-scale">'
                '<div class="sidebar-scale-row"><span>M 4.5 – 4.9</span><span class="scale-num">+1 puan</span></div>'
                '<div class="sidebar-scale-row"><span>M 5.0 – 5.9</span><span class="scale-num">+3 puan</span></div>'
                '<div class="sidebar-scale-row"><span>M 6.0 – 6.9</span><span class="scale-num">+5 puan</span></div>'
                '<div class="sidebar-scale-row"><span>M 7.0 ve üzeri</span><span class="scale-num">+7 puan</span></div>'
                '</div>', unsafe_allow_html=True)
    st.caption("Ağırlıklar öğrenci projesine özel; resmî deprem risk puanı değildir.")
    st.divider()
    st.caption("Kaynaklar: USGS Earthquake Catalog · geoBoundaries ADM1")


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def verileri_yukle(baslangic_yili: int, bitis_yili: int, min_buyukluk: float):
    sinirlar = il_sinirlarini_getir()
    olaylar = depremleri_getir(baslangic_yili, bitis_yili, min_buyukluk)
    return sinirlar, olaylar


@st.cache_data(show_spinner=False)
def hesapla(depremler: pd.DataFrame, sinirlar: dict, mesafe: int):
    return puanlari_hesapla(depremler, sinirlar, mesafe)


st.markdown("""
<div class="hero">
  <div class="hero-text">
    <div class="overline"><span class="dot"></span> TÜRKİYE DOĞAL AFET ANALİZ PLATFORMU <span style="color:#9ab8c8">/ BETA 02</span></div>
    <h1>AFET <em>ATLAS.</em></h1>
    <div class="module-title">Deprem hareketliliğine göre en güvenli iller</div>
    <p>Geçmiş deprem kayıtlarına göre 81 ili karşılaştır. Bu sıralama yalnızca seçtiğin dönem ve mesafedeki hareketliliği gösterir; gerçek deprem güvenliğini ölçmez.</p>
    <div class="hero-tags"><span class="hero-tag">◉ Deprem modülü aktif</span><span class="hero-tag">◈ 81 il</span><span class="hero-tag">▤ Gerçek açık veri</span></div>
  </div>
  <div class="radar" aria-hidden="true">
    <div class="radar-line-h"></div><div class="radar-line-v"></div>
    <div class="radar-core"></div><div class="radar-ping"></div><div class="radar-ping2"></div>
    <div class="radar-label">SİSMİK GÖZLEM</div>
  </div>
</div>
""", unsafe_allow_html=True)

try:
    with st.spinner("Gerçek USGS verileri ve il sınırları yükleniyor..."):
        sinirlar, depremler = verileri_yukle(baslangic, bitis, minimum)
    with st.spinner("İl sınırları ve olay ağırlıkları hesaplanıyor..."):
        sonuc, eslesenler = hesapla(depremler, sinirlar, mesafe)
except Exception as hata:
    st.error("Veri kaynaklarına erişilemedi. Uygulama sahte verilerle devam etmiyor.")
    st.code(str(hata))
    st.markdown("[USGS kataloğu](https://earthquake.usgs.gov/earthquakes/search/) · "
                "[geoBoundaries](https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/)")
    st.stop()

if depremler.empty:
    st.warning("Seçilen tarih ve büyüklük aralığına uygun deprem kaydı yok.")
    st.stop()

eslesen_tekil = eslesenler['USGS Olay ID'].nunique() if not eslesenler.empty else 0
aktif_il = int((sonuc['Deprem sayısı'] > 0).sum())

st.markdown('<div class="metrics">'
            + metric("USGS OLAYI", f"{len(depremler):,}".replace(',', '.'), f"{baslangic}–{bitis} · M ≥ {minimum}")
            + metric("TARANAN İL", "81", "Türkiye il sınırları", "#89a8ff")
            + metric("EN BÜYÜK DEPREM", f"{depremler['mag'].max():.1f}", "Kayıtlı en yüksek büyüklük", "#f1ad7d")
            + metric("İL EŞLEŞMESİ", f"{len(eslesenler):,}".replace(',', '.'), f"{eslesen_tekil} farklı olay · {mesafe} km", "#87d9ac")
            + '</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="warning-note"><strong>Yorumlama notu:</strong> Bu panel geçmiş deprem kayıtlarına göre '
    'hareketlilik karşılaştırması yapar. Deprem riski, beklenen sarsıntı şiddeti, bina güvenliği veya '
    'gerçek yaşam güvenliği sıralaması değildir. “En güvenli” ifadesi yalnızca seçili tarih, büyüklük ve mesafe kapsamındaki gözlenen hareketliliğe dayanır.</div>', unsafe_allow_html=True
)

sekme_harita, sekme_siralama, sekme_detay, sekme_yontem, sekme_ajan = st.tabs([
    "◉  Genel görünüm", "▤  İl sıralaması", "⌕  İl incelemesi", "ⓘ  Veri & yöntem", "✧  Siz Sorun"
])

# ---------- Genel görünüm ----------
with sekme_harita:
    bolum("Deprem hareketliliği haritası", f"{baslangic}–{bitis}  ·  M ≥ {minimum}  ·  {mesafe} km yakınlık", "COĞRAFİ GÖRÜNÜM")
    sol, sag = st.columns([1.75, 1], gap="large")
    with sol:
        # Harita artık Plotly Geo alt sistemine veya dış harita servisine bağlı değil.
        harita = turkiye_haritasi(sinirlar, sonuc)
        st.plotly_chart(harita, use_container_width=True, config={"displaylogo": False, "responsive": True})
        st.markdown('<div class="caption-note">Haritadaki sıcak renkler daha yüksek toplam <strong>olay puanını</strong> gösterir. '
                    '0 puan, seçili dönemde ve mesafede eşleşen olay olmadığı anlamına gelir; düşük risk garantisi değildir.</div>',
                    unsafe_allow_html=True)
    with sag:
        panel_baslik("Hareketliliği yüksek 5 il", "Seçtiğin tarih, büyüklük ve mesafeye göre")
        ilk_bes = sonuc.sort_values(['Toplam puan', 'Deprem sayısı'], ascending=False).head(5)
        en_buyuk_puan = max(int(sonuc['Toplam puan'].max()), 1)
        bars = []
        for _, s in ilk_bes.iterrows():
            pct = max(0, min(100, int(100 * int(s['Toplam puan']) / en_buyuk_puan)))
            bars.append(f'<div><div class="rank-top"><strong>{escape(str(s["İl"]))}</strong>'
                        f'<span>{int(s["Toplam puan"])} puan · {int(s["Deprem sayısı"])} olay</span></div>'
                        f'<div class="rank-track"><div class="rank-fill" style="width:{pct}%"></div></div></div>')
        st.markdown('<div class="card"><div class="ranking-list">' + ''.join(bars)
                    + '</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="two-stat">'
                    f'<div class="mini-stat"><div class="mini-stat-label">Eşleşme olan il</div><div class="mini-stat-value">{aktif_il}<span style="font-size:12px;color:#8da6bb"> / 81</span></div></div>'
                    f'<div class="mini-stat"><div class="mini-stat-label">Farklı deprem</div><div class="mini-stat-value">{eslesen_tekil}</div></div>'
                    '</div>', unsafe_allow_html=True)
        st.markdown('<div class="caption-note">Bir deprem birden fazla ilin yakınlık alanına girebilir. '
                    'Bu yüzden il eşleşmesi ile farklı olay sayısı aynı olmak zorunda değildir.</div>', unsafe_allow_html=True)

# ---------- Sıralama ve karşılaştırma ----------
with sekme_siralama:
    bolum("Deprem hareketliliğine göre en güvenli iller", "Seçilen kapsamda deprem eşleşmesi bulunan iller · azdan çoğa olay puanı", "İL KARŞILAŞTIRMASI")
    st.caption("Bu başlık gerçek can, bina veya afet güvenliği sıralaması değildir. Sadece seçili kayıtlar için hareketliliği karşılaştırır.")
    kayitli_iller = sonuc[sonuc['Deprem sayısı'] > 0].copy()
    sifir_eslesen_iller = sonuc[sonuc['Deprem sayısı'] == 0].copy()
    st.dataframe(
        kayitli_iller[['Sıra', 'İl', 'Deprem sayısı', 'En büyük deprem', 'Toplam puan', 'Karşılaştırma endeksi']],
        use_container_width=True, hide_index=True, height=360,
        column_config={"Karşılaştırma endeksi": st.column_config.ProgressColumn(
            "Göreli endeks / 100", min_value=0, max_value=100, format="%.1f"),
            "En büyük deprem": st.column_config.NumberColumn("En büyük deprem", format="%.1f")},
    )
    with st.expander(f"Seçilen kapsamda deprem eşleşmeyen iller ({len(sifir_eslesen_iller)})"):
        st.caption("Bu illerde deprem olmayacağı sonucu çıkarılamaz. Kayıt yokluğu, güvenlik yüzdesi değildir ve bu illere 100/100 endeks verilmez.")
        st.dataframe(sifir_eslesen_iller[['İl', 'Deprem sayısı', 'Toplam puan', 'Gözlem durumu']],
                     use_container_width=True, hide_index=True, height=230)
    a, b = st.columns([1, 1], gap="large")
    with a:
        panel_baslik("En yüksek puanlı 10 il", "Kümülatif olay ağırlıklarının karşılaştırması")
        ilk_on = sonuc.nlargest(10, 'Toplam puan').sort_values('Toplam puan')
        bars = go.Figure(go.Bar(
            x=ilk_on['Toplam puan'], y=ilk_on['İl'], orientation='h',
            marker=dict(color='#ee926f', line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>%{x} puan<extra></extra>",
        ))
        bars.update_layout(
            height=375, margin=dict(l=0,r=16,t=8,b=30),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cddce9', family='DM Sans'),
            xaxis=dict(title='Toplam olay puanı', showgrid=True, gridcolor='#26364b', zeroline=False),
            yaxis=dict(title=''),
        )
        st.plotly_chart(bars, use_container_width=True, config={'displaylogo':False})
    with b:
        panel_baslik("İki ili yan yana incele", "Aynı kurallarla hesaplanan iki ili seç")
        iller_listesi = sorted(sonuc['İl'].tolist())
        ilk = st.selectbox("Birinci il", iller_listesi, index=iller_listesi.index('Ankara') if 'Ankara' in iller_listesi else 0)
        ikinci = st.selectbox("İkinci il", iller_listesi, index=iller_listesi.index('İstanbul') if 'İstanbul' in iller_listesi else 1)
        if ilk == ikinci:
            st.info("Karşılaştırma için farklı iki il seçebilirsin.")
        else:
            i1 = sonuc.loc[sonuc['İl'] == ilk].iloc[0]
            i2 = sonuc.loc[sonuc['İl'] == ikinci].iloc[0]
            st.markdown('<div class="two-stat">'
                        f'<div class="mini-stat"><div class="mini-stat-label">{escape(ilk)}</div><div class="mini-stat-value">{int(i1["Toplam puan"])} <span style="font-size:12px;color:#8da6bb">puan</span></div><div class="card-note">{int(i1["Deprem sayısı"])} olay</div></div>'
                        f'<div class="mini-stat"><div class="mini-stat-label">{escape(ikinci)}</div><div class="mini-stat-value">{int(i2["Toplam puan"])} <span style="font-size:12px;color:#8da6bb">puan</span></div><div class="card-note">{int(i2["Deprem sayısı"])} olay</div></div>'
                        '</div>', unsafe_allow_html=True)
            kars = go.Figure(go.Bar(x=[ilk, ikinci], y=[int(i1['Toplam puan']), int(i2['Toplam puan'])],
                                     marker_color=['#5fe0d3', '#f4a27a'],
                                     text=[f"{int(i1['Toplam puan'])} puan", f"{int(i2['Toplam puan'])} puan"],
                                     textposition='outside', cliponaxis=False))
            kars.update_layout(height=240, showlegend=False, margin=dict(l=0,r=4,t=28,b=7),
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='#cddce9'),
                               yaxis=dict(showgrid=True, gridcolor='#26364b', zeroline=False),
                               xaxis=dict(showgrid=False))
            st.plotly_chart(kars, use_container_width=True, config={'displaylogo':False})
    st.download_button("↓ 81 ilin sonuçlarını CSV indir", sonuc.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f"afet_atlas_iller_{baslangic}_{bitis}_{mesafe}km.csv", mime='text/csv')

# ---------- İl inceleme ----------
with sekme_detay:
    bolum("Bir ilin deprem geçmişi", "Büyüklük, tarih ve eşleşen olayları incele", "DETAYLI İNCELEME")
    secim = st.selectbox("İncelemek istediğin il", sorted(sonuc['İl'].tolist()), key='detay_il')
    il_verisi = sonuc.loc[sonuc['İl'] == secim].iloc[0]
    il_olaylari = eslesenler.loc[eslesenler['İl'] == secim].copy()
    st.markdown('<div class="two-stat">'
                f'<div class="mini-stat"><div class="mini-stat-label">{escape(secim)} · Toplam olay puanı</div><div class="mini-stat-value">{int(il_verisi["Toplam puan"])}</div></div>'
                f'<div class="mini-stat"><div class="mini-stat-label">Eşleşen deprem sayısı</div><div class="mini-stat-value">{int(il_verisi["Deprem sayısı"])}</div></div>'
                '</div>', unsafe_allow_html=True)
    if il_olaylari.empty:
        st.info(f"{secim} için seçili dönem ve {mesafe} km kapsamında M ≥ {minimum} deprem eşleşmesi yok. Bu, ilin deprem açısından güvenli olduğu anlamına gelmez.")
    else:
        il_olaylari['Tarih'] = pd.to_datetime(il_olaylari['Tarih'], utc=True)
        bolum("Olay zaman çizelgesi", "İşaretlerin yeri deprem büyüklüğünü gösterir")
        fig_zaman = go.Figure(go.Scatter(
            x=il_olaylari['Tarih'], y=il_olaylari['Büyüklük'],
            mode='markers',
            marker=dict(size=il_olaylari['Puan'] * 3.0 + 10, color=il_olaylari['Puan'],
                        colorscale=[[0,'#56d7cb'], [.45,'#e7be79'],[1,'#f17e6c']],
                        line=dict(width=1, color='#0b182a'), opacity=.86, showscale=False),
            customdata=il_olaylari[['Puan', 'Yer', 'İl sınırına uzaklık (km)']].to_numpy(),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Büyüklük: %{y}<br>Puan: %{customdata[0]}<br>Yer: %{customdata[1]}<br>İl sınırına: %{customdata[2]} km<extra></extra>',
        ))
        fig_zaman.update_layout(height=345, margin=dict(l=0,r=15,t=8,b=25),
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='#cddce9', family='DM Sans'),
                               xaxis=dict(showgrid=True, gridcolor='#26364b'),
                               yaxis=dict(title='Büyüklük (M)', showgrid=True, gridcolor='#26364b'))
        st.plotly_chart(fig_zaman, use_container_width=True, config={'displaylogo':False})
        panel_baslik("Deprem kayıtları", "USGS olay kimlikleri üzerinden kontrol edilebilir")
        st.dataframe(il_olaylari.sort_values('Tarih', ascending=False),
                     hide_index=True, use_container_width=True)
    st.download_button("↓ Bu ilin eşleşen deprem kayıtlarını indir",
                       il_olaylari.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f"{secim.lower()}_depremleri_{baslangic}_{bitis}_{mesafe}km.csv", mime='text/csv')

# ---------- Veri ve metodoloji ----------
with sekme_yontem:
    bolum("Veri, hesaplama ve sınırlamalar", "Yöntem şeffaflığı · Akademik proje prototipi", "KAYNAKLAR")
    st.markdown(f"""
**Veri kaynakları**

- [USGS Earthquake Catalog](https://earthquake.usgs.gov/earthquakes/search/): {baslangic}–{bitis} döneminde M ≥ {minimum}, Türkiye ve çevresi için enlem 34–43.5 ve boylam 24–46 aralığındaki kayıtlar. USGS olay kimlikleri kullanılır.
- [geoBoundaries – Türkiye ADM1](https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/): 81 il poligonunu içeren GeoJSON sınır verisi.

**Uygulanan ağırlıklar**

| Deprem büyüklüğü | Tek olay puanı |
|:--|--:|
| 4.5–4.9 | 1 |
| 5.0–5.9 | 3 |
| 6.0–6.9 | 5 |
| 7.0 ve üzeri | 7 |

**İl puanı nasıl hesaplanıyor?** Seçilen **{mesafe} km** yakınlık içinde merkez üssü bulunan her olayın ağırlığı toplanır. 0 km seçildiğinde yalnızca il poligonunun içine düşen merkez üsleri eşleşir. Bir olay, yakınlık alanlarına bağlı olarak birden fazla ilde sayılabilir.

**Göreli karşılaştırma endeksi:** Pozitif puanlı iller için `100 × [1 − ln(1 + il_puanı) / ln(1 + en_yüksek_il_puanı)]` kullanılır. Bu bir olasılık veya gerçek güvenlik yüzdesi değildir. **Sıfır eşleşmesi olan illerin endeksi hesaplanmaz**, çünkü seçili tarihte M ≥ {minimum} büyüklüğünde kayıt bulunmaması deprem tehlikesinin yokluğunu göstermez.

**Bilimsel sınır:** Bu puanlar deprem tehlike haritası, beklenen sarsıntı, nüfus riski veya yapı güvenliği ölçüsü değildir. Yalnızca seçilen veri ve kurallarla geçmiş olay hareketliliğini ifade eder. USGS küçük magnitüdlü depremleri Türkiye'de eksik kaydedebilir. “Deprem hareketliliğine göre en güvenli iller” başlığı yalnızca geçmiş kayıtlara göre bir karşılaştırmadır. Eşleşmesi olmayan iller ayrı listelenir; gerçek tehlike değerlendirmesi için AFAD/GEM sismik tehlike modelleri gerekir.

**Atıf:** U.S. Geological Survey ANSS Comprehensive Catalog (ComCat), DOI: 10.5066/F7MS3QZH; geoBoundaries, TUR ADM1. Kullanılan verilerin lisans ve kaynak koşulları ilgili sayfalarda yer alır.
""")
    st.download_button("↓ Bütün il–deprem eşleşmelerini CSV indir",
                       eslesenler.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f"afet_atlas_eslesmeler_{baslangic}_{bitis}_{mesafe}km.csv", mime='text/csv')

# ---------- Google Agent Development Kit veri ajanı ----------
with sekme_ajan:
    bolum("Siz Sorun", "Google ADK destekli deprem veri asistanı", "YAPAY ZEKÂ MODÜLÜ")
    st.markdown('''<div class="card"><div class="card-title">Deprem verilerine soru sor</div>
    <div class="card-note">Bu modül doğrudan Gemini SDK değil, <strong>Google ADK</strong> kullanır.
    ADK ajanı, uygulamanın zaten hesapladığı gerçek USGS sonuçlarını Python araçlarıyla sorgular.
    Örnek: “Ankara ile İstanbul'u karşılaştır.”</div></div>''', unsafe_allow_html=True)
    st.caption(f"Aktif filtreler: **{baslangic}–{bitis}** · **M ≥ {minimum}** · **{mesafe} km**")
    st.caption("Bu sonuçlar geçmiş deprem hareketliliğidir; gerçek güvenlik veya afet riski yüzdesi değildir.")

    # ADK, Google AI Studio anahtarını sunucu tarafındaki GOOGLE_API_KEY değişkeninden okur.
    # API anahtarını kullanıcıya açık olan Python kaynak koduna yazmayın.
    if not os.environ.get("GOOGLE_API_KEY"):
        try:
            if st.secrets.get("GOOGLE_API_KEY"):
                os.environ["GOOGLE_API_KEY"] = str(st.secrets["GOOGLE_API_KEY"])
        except Exception:
            # Streamlit secrets dosyası yapılandırılmamış olabilir.
            pass
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
    anahtar_var = bool(os.environ.get("GOOGLE_API_KEY"))
    if not anahtar_var:
        st.info("ADK ajanını çalıştırmak için Google AI Studio'dan API anahtarı oluşturup "
                "GOOGLE_API_KEY ortam değişkenine ekle. Diğer ekranlar anahtarsız çalışır.")

    secili_soru = st.selectbox("Örnek sorular", [
        "Kendi sorumu yazacağım",
        "Ankara ile İstanbul'un deprem hareketliliğini karşılaştır.",
        "Deprem hareketliliği en yüksek beş il hangisi?",
        "Balıkesir'deki en büyük üç depremin büyüklüğü ve tarihi nedir?",
        "Sıfır deprem eşleşmesi bulunan iller neden güvenli sayılmaz?",
        "Bu analiz kaç USGS kaydına dayanıyor?",
    ])
    ornek = "" if secili_soru == "Kendi sorumu yazacağım" else secili_soru
    girilen_soru = st.text_area("Sorunuz", value=ornek, height=95,
                               placeholder="Örn. 2025 yılında Balıkesir'deki toplam olay puanı kaç?",
                               key=f"adk_soru_{secili_soru}")
    if st.button("✦ Soruyu gönder", type="primary", disabled=not anahtar_var,
                 use_container_width=True):
        if not girilen_soru.strip():
            st.warning("Önce bir soru yaz.")
        else:
            try:
                with st.spinner("ADK Runner ve Python veri araçları çalışıyor..."):
                    sonuc_ajan = ajana_sor_ayrintili(girilen_soru, sonuc, depremler, eslesenler,
                                                      baslangic, bitis, minimum, mesafe)
                st.session_state["adk_son_yanit"] = {
                    "soru": girilen_soru, **sonuc_ajan,
                    "kapsam": (baslangic, bitis, minimum, mesafe),
                }
            except ImportError:
                st.error("Google ADK kurulu değil. Terminalde: python -m pip install -r requirements.txt")
            except Exception as hata:
                st.error("ADK/Gemini bağlantısı tamamlanamadı. API anahtarını, internet bağlantını ve kotanı kontrol et.")
                with st.expander("Teknik hata ayrıntısı"):
                    st.code(str(hata))
    yanit = st.session_state.get("adk_son_yanit")
    if yanit and yanit["kapsam"] == (baslangic, bitis, minimum, mesafe):
        st.markdown("#### ADK ajanının yanıtı")
        st.markdown(yanit["cevap"])
        kullanilan_araclar = yanit.get("arac_cagrilari", [])
        if kullanilan_araclar:
            st.success(f"ADK {len(kullanilan_araclar)} Python araç çağrısı yaptı: "
                       + ", ".join(c["arac"] for c in kullanilan_araclar))
            with st.expander("ADK işlem geçmişi — hangi araçları çağırdı?"):
                for sira, cagri in enumerate(kullanilan_araclar, start=1):
                    st.write(f"{sira}. {cagri['arac']}")
                    st.json(cagri["parametreler"])
        else:
            st.warning("Bu yanıtta ADK veri aracı çağrısı görülmedi. Sayısal iddiaları ayrıca kontrol et.")
        st.caption("Kaynak: USGS × geoBoundaries; hesaplama.py üzerinden doğrulanabilir Python veri araçları.")
    with st.expander("ADK ajanını nasıl test ederim? Örnek sorular ve beklenen sonuçlar"):
        st.markdown("""**Test için filtreleri 2025–2025, M ≥ 4.5, yakınlık 0 km seç.**

1. **'2025'te toplam kaç USGS deprem kaydı var?'** → **159** (`veri_kapsami`).
2. **'Balıkesir'de kaç deprem var, toplam puan kaç?'** → **18 deprem, 30 puan** (`il_ozeti`).
3. **'Ankara ile İstanbul'u karşılaştır.'** → **Ankara 2 olay/4 puan, İstanbul 0 eşleşme/0 puan**; sıfırın güvenli anlamına gelmediğini söylemeli (`il_karsilastir`).
4. **'Önümüzdeki ay kesin nerede deprem olacak?'** → Bir deprem tahmini **uydurmamalı**.

Yanıtın ardından **ADK işlem geçmişi** bölümünü aç. Kaç araç çağrıldığını ve hangi parametrelerin kullanıldığını burada görebilirsin. Bu ekran modelin tek tek doğru verileri kullanıp kullanmadığını test eder; tek başına bütün cevapların doğru olduğunu garanti etmez.

*Not: Streamlit'te her soru yeni ADK oturumu açar. Önceki soruyu hatırlaması henüz desteklenmiyor.*""")
    st.markdown("[Google AI Studio API anahtarı](https://aistudio.google.com/apikey) · "
                "[Google ADK Python dokümantasyonu](https://adk.dev/get-started/python/)")

st.markdown('<div class="footer-brand"><span>◉ AFET ATLAS · TÜRKİYE DOĞAL AFET ANALİZ PLATFORMU</span>'
            '<span>BBY261 · Deprem modülü · USGS × geoBoundaries · Prototip v2.6 ADK</span></div>',
            unsafe_allow_html=True)
