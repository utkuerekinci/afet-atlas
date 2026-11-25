"""Afet Atlas koyu tema etkileşimli kontrol stilleri.

Gündüz teması kaldırıldı. Tek renk paleti koyu temadır.
"""

ORTAK_KONTROL_CSS = r"""<style>
/* AFET ATLAS · etkilesimli kontroller — koyu tema, tutarli kirmizi */
:root {--atlas-red:#f04e66;--atlas-red-hover:#ff647a;--atlas-red-dark:#cf3652;}
/* 1. Streamlit selectbox / multiselect: BaseWeb'in GERCEK gorunen ic katmanini boya. */
:root { --atlas-select-red:#f04e66; }
/* Ana kontroller; BaseWeb farkli Streamlit surumlerinde ara wrapper ekleyebilir. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] div,
.stApp [data-testid="stSelectbox"] [data-baseweb="base-input"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="base-input"],
.stApp [data-testid="stSelectbox"] [data-baseweb="input"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="input"],
.stApp [data-testid="stSelectbox"] [role="combobox"],
.stApp [data-testid="stMultiSelect"] [role="combobox"] {
 background-color:#f04e66!important;
 background-image:none!important;
 color:#fff!important;
 border-color:#f04e66!important;
}
/* Sadece gorunen tiklanabilir kabuga radius/border/min-height ver. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child,
.stApp [data-testid="stSelectbox"] [role="combobox"],
.stApp [data-testid="stMultiSelect"] [role="combobox"] {
 min-height:48px!important;
 border:1px solid #f04e66!important;
 border-radius:12px!important;
 box-shadow:0 3px 12px rgba(220,49,82,.18)!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child:hover,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child:hover {
 background-color:#ff647a!important;border-color:#ff647a!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
 outline:2px solid #ffb5c1!important;outline-offset:2px!important;
}
/* Metin/ok beyaz; etiketleri (Harita gostergesi vb.) bu kurala DAHIL ETME. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] span,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] span,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] input,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] input,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] svg,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
 color:#fff!important;
 fill:currentColor!important;
 -webkit-text-fill-color:#fff!important;
 font-size:15px!important;font-weight:700!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder {
 color:#ffe7eb!important;-webkit-text-fill-color:#ffe7eb!important;opacity:1!important;
}
/* Aci lan menudeki secenekler koyu zemin uzerinde okunabilir. */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] [role="listbox"],
[data-baseweb="select"] [role="listbox"] {
 background:#162337!important;border:1px solid #f04e66!important;
 box-shadow:0 12px 30px rgba(0,0,0,.35)!important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"] {
 background:#162337!important;color:#f2f6ff!important;font-weight:650!important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"][aria-selected="true"] {
 background:#7d2b43!important;color:#fff!important;
}
/* 2. Nasıl kullanılır? = st.popover düğmesi. */
.stApp .st-key-atlas_help_trigger button,
.stApp .st-key-atlas_help_trigger [data-testid^="stBaseButton"],
.stApp [data-testid="stPopover"] button,
.stApp [data-testid="stPopover"] > button,
.stApp [data-testid="stPopover"] [data-testid^="stBaseButton"] {
 background:#f04e66!important;border:1px solid #ff9baa!important;
 border-radius:12px!important;color:#fff!important;
 padding:9px 16px!important;min-height:43px!important;
 box-shadow:0 3px 12px rgba(220,49,82,.16)!important;
}
.stApp .st-key-atlas_help_trigger button:hover,
.stApp [data-testid="stPopover"] button:hover,
.stApp [data-testid="stPopover"] [data-testid^="stBaseButton"]:hover {
 background:#ff647a!important;border-color:#ffc1cb!important;
}
.stApp .st-key-atlas_help_trigger button p,
.stApp [data-testid="stPopover"] button p,
.stApp [data-testid="stPopover"] button span,
.stApp [data-testid="stPopover"] button svg {
 color:#fff!important;fill:currentColor!important;
 font-size:15px!important;font-weight:750!important;
}
/* 3. Gemini ile daha fazla bilgi: type='primary' + anahtara bagli guvence. */
.stApp [class*="st-key-gemini_btn_"] button,
.stApp [class*="st-key-gemini_btn_"] [data-testid^="stBaseButton"],
.stApp [data-testid="stMain"] [data-testid="stButton"] button[kind="primary"],
.stApp [data-testid="stMain"] [data-testid="stBaseButton-primary"] {
 background:#f04e66!important;border:1px solid #ff9baa!important;
 color:#fff!important;border-radius:12px!important;
 min-height:44px!important;box-shadow:0 3px 12px rgba(220,49,82,.15)!important;
}
.stApp [class*="st-key-gemini_btn_"] button:hover,
.stApp [data-testid="stMain"] [data-testid="stButton"] button[kind="primary"]:hover,
.stApp [data-testid="stMain"] [data-testid="stBaseButton-primary"]:hover {
 background:#ff647a!important;border-color:#ffc1cb!important;
}
.stApp [class*="st-key-gemini_btn_"] button p,
.stApp [data-testid="stMain"] [data-testid="stButton"] button[kind="primary"] p,
.stApp [data-testid="stMain"] [data-testid="stBaseButton-primary"] p {
 color:#fff!important;font-weight:750!important;font-size:15px!important;
}
/* 4. Yasam tercihi: Dengeli / Daha sakin / Daha hareketli daha buyuk ve tiklanabilir. */
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] {
 gap:11px!important;
}
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label {
 display:flex!important;align-items:center!important;
 min-height:52px!important;padding:12px 14px!important;
 border-radius:13px!important;
 border:1px solid #446077!important;
 background:#172b43!important;
 cursor:pointer!important;
}
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label:hover {
 border-color:#ff9baa!important;
}
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
 background:#783247!important;border-color:#f04e66!important;
}
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label p,
.stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label span {
 color:#fff!important;font-size:17px!important;font-weight:750!important;
}
/* Koyu temada kontrol etiketleri yeterince okunakli */
.stApp [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stRadio"] [data-testid="stWidgetLabel"] p {
 font-size:14px!important;font-weight:700!important;
}
@media(max-width:680px){
 .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {min-height:42px!important;}
 .stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label {min-height:48px!important;padding:9px 11px!important;}
}

/* v4.15: SADECE istenen harita/afet filtreleri, Analizler menusunun mavisi.
   Yalnizca widget key siniflari hedeflenir. Gemini, Yardim, ilce karsilastirma,
   yonetici paneli ve navigasyon dugmeleri bu mavi kurala dahil DEGILDIR. */
:root {
 --atlas-filter-blue:#204b76;
 --atlas-filter-blue-hover:#2b608f;
 --atlas-filter-blue-border:#438bc1;
}
/* Kapsam:
   Harita gostergesi (ana sayfa, yasam, ticaret, yangin),
   Sehir ara/sec + Haritada incelenecek il (il_secimi fonksiyonunun tum anahtarlari),
   Analiz edilecek sektor, afet turu, deprem yil/buyukluk/yakinlik. */
.stApp :is(
 [class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance
) [data-baseweb="select"],
.stApp :is(
 [class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance
) [data-baseweb="select"] :is(div,input,[role="combobox"],[data-baseweb="base-input"],[data-baseweb="input"]) {
 background:var(--atlas-filter-blue)!important;
 background-color:var(--atlas-filter-blue)!important;
 background-image:none!important;
 border-color:var(--atlas-filter-blue-border)!important;
 color:#ffffff!important;
}
/* Tek cizgi, duzgun radius ve min yukseklik yalnizca dis gorunen kabukta. */
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"] > div:first-child {
 border:1px solid var(--atlas-filter-blue-border)!important;
 border-radius:12px!important;
 min-height:48px!important;
 box-shadow:0 3px 12px rgba(17,62,103,.24)!important;
}
/* BaseWeb'in dis kabugunun :hover kuralina ozellikle ustun gelir;
   onceki kirmizi CSS bu kabugu mouse uzerindeyken kirmizi birakiyordu. */
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"] > div:first-child:hover,
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"]:hover > div:first-child {
 background:var(--atlas-filter-blue-hover)!important;
 background-color:var(--atlas-filter-blue-hover)!important;
 border-color:#73b9ee!important;
}
/* Hover, hangi BaseWeb ic katmaninin arka plani boyanmis olursa olsun mavi. */
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"]:hover,
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"]:hover :is(div,input,[role="combobox"]) {
 background:var(--atlas-filter-blue-hover)!important;
 background-color:var(--atlas-filter-blue-hover)!important;
 border-color:#73b9ee!important;
}
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"]:focus-within {
 outline:2px solid #87c7f1!important;
 outline-offset:2px!important;
}
/* Metin/ok beyaz; dis widget etiketi degismez. */
.stApp :is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [data-baseweb="select"] :is(span,input,svg) {
 color:#fff!important;
 fill:currentColor!important;
 -webkit-text-fill-color:#fff!important;
}
/* Secim listesi portal olarak body altinda acilir; mavi filtre acikken
   liste sinirinda da ayni mavi kullanilir. Diger listeler etkilenmez. */
body:has(:is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [aria-expanded="true"]) [data-baseweb="popover"] [role="listbox"] {
 border-color:#438bc1!important;
}
body:has(:is(
 [class*="st-key-home_v40_layer_"],.st-key-yasam_layer,.st-key-ticaret_layer,
 .st-key-v36_fire_metric,[class*="st-key-il_select_"],.st-key-v34_sektor,
 .st-key-v36_disaster,.st-key-v45_year_start,.st-key-v45_year_end,
 .st-key-v45_min_m,.st-key-v45_distance
) [aria-expanded="true"]) [data-baseweb="popover"] [role="option"]:is(:hover,[aria-selected="true"]) {
 background:#2b608f!important;
}

</style>"""


def ortak_kontrol_css() -> str:
    return ORTAK_KONTROL_CSS
