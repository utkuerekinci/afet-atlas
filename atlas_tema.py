"""Afet Atlas arayuz temalari ve ortak kontrol stilleri.

Gece modu varsayilan olarak .streamlit/config.toml'da kalir.
Gunduz CSS'i sadece kullanici acik modu sectiginde uygulanir.
Kontrol CSS'i her iki temadan sonra uygulanir; secim kutulari, yardim ve
Gemini butonlari ayni belirgin kirmiziyi kullanir.
"""

GUNDUZ_CSS = r"""<style>
/* AFET ATLAS · GUNDUZ | tek palet, gercek aydinlik yuzeyler */
:root {
 color-scheme: light!important;
 --background-color:#f4f7fc;
 --secondary-background-color:#ffffff;
 --text-color:#203249;
 --primary-color:#f04e66;
 --atlas-day-bg:#f4f7fc;
 --atlas-day-panel:#ffffff;
 --atlas-day-muted:#536a83;
 --atlas-day-ink:#203249;
 --atlas-day-ink-soft:#21344b;
 --atlas-day-stroke:#cdddea;
}
html,body,[data-testid="stAppViewContainer"],.stApp,[data-testid="stMain"] {
 color:#203249!important;
 background-color:#f4f7fc!important;
}
.stApp {
 background:radial-gradient(ellipse 50% 30% at 90% 0%,rgba(54,150,178,.10),transparent 82%),
 linear-gradient(180deg,#f8fbff 0%,#f4f7fc 52%,#edf3fa 100%)!important;
}
[data-testid="stHeader"] {background:transparent!important;}
[data-testid="stSidebar"] {
 background:linear-gradient(180deg,#eef4fa,#e6eef7)!important;
 border-right:1px solid #c8d8e7!important;
}
[data-testid="stSidebar"] p:not(button p):not(summary p),
[data-testid="stSidebar"] label:not([role="radio"]),
[data-testid="stSidebar"] .sidebar-small {color:#425c77!important;}
[data-testid="stSidebar"] hr {border-color:#cbd9e7!important;}
[data-testid="stSidebar"] .sidebar-head {color:#16314d!important;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"] span,
[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {
 color:#344e68!important;
}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,
[data-testid="stMain"] h3,[data-testid="stMain"] h4,
[data-testid="stMain"] h5 {color:#1c324d!important;}
[data-testid="stMain"] a {color:#087c86!important;}
/* Kutular ve yerlesik icerik */
[data-testid="stMain"] [data-testid="stMetric"],
[data-testid="stMain"] [data-testid="stExpander"],
[data-testid="stMain"] [data-testid="stDataFrame"] {
 background:#fff!important;
 border-color:#cbdcea!important;
 box-shadow:0 4px 18px rgba(34,76,115,.045)!important;
}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p {color:#566b83!important;}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] * {color:#193450!important;}
[data-testid="stExpander"] summary {background:#fff!important;color:#20384f!important;}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {color:#28425d!important;fill:currentColor!important;}
[data-testid="stAlert"] {border-radius:14px!important;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,[data-testid="stDateInput"] input,
[data-testid="stFileUploader"] section {
 background:#fff!important;color:#203249!important;
 border-color:#c7d9e8!important;
}
[data-testid="stFileUploader"] section p {color:#344e68!important;}
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {color:#21344b!important;}
[data-testid="stToggle"] label p,[data-testid="stCheckbox"] label p {color:#304a65!important;}
[data-testid="stToggle"] [role="switch"] {border-color:#a4bacd!important;}
/* Sekmeler karanlik paleti miras almasin */
button[data-baseweb="tab"] {color:#4c6580!important;}
button[data-baseweb="tab"][aria-selected="true"] {color:#087d87!important;}
[data-baseweb="tab-highlight"] {background-color:#08858e!important;}
[data-baseweb="tab-border"] {background-color:#d4e1ec!important;}
/* Sade buton, islem vurgulari ortak kontrol CSS'i tarafindan gelecektir */
[data-testid="stMain"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
 background:#fff!important;border-color:#c4d6e6!important;color:#294760!important;
}
[data-testid="stMain"] [data-testid="stButton"] button[kind="secondary"]:hover,
[data-testid="stMain"] [data-testid="stBaseButton-secondary"]:hover {
 background:#e6f2fa!important;border-color:#81b1cd!important;
}
[data-testid="stDownloadButton"] button {
 background:#e8f3f8!important;border-color:#a4cbd5!important;color:#126a76!important;
}
[data-testid="stDownloadButton"] button:hover {background:#d4edf5!important;}
/* Ozel HTML bloklar: ayni yumuşak mavi, beyaz ve koyu lacivert dili */
.hero,.hero-return,.compact-hero {
 background:linear-gradient(110deg,#e0f1f8 0%,#f7fbff 58%,#e2eef9 100%)!important;
 border-color:#bad5e4!important;
 box-shadow:0 12px 36px rgba(32,81,115,.065)!important;
}
.hero:before {opacity:.34!important;}
.hero h1,.hero h2,.hero-return h1,.hero-return h2,.compact-hero h1,
.hero .module-title {color:#16344f!important;}
.hero h1 em,.hero-return h1 em {color:#087d89!important;}
.hero p,.hero-return p,.compact-hero p {color:#496781!important;}
.overline,.kicker,.filter-strip-title,.overview-pane .eyebrow {color:#087d87!important;}
.filter-strip-title span {color:#527389!important;}
.dot {background:#0d9a95!important;box-shadow:0 0 10px rgba(13,154,149,.20)!important;}
.hero-tag,.quick-facts span {
 background:#e8f3f9!important;border-color:#b8d5e3!important;color:#275a6a!important;
}
.metric,.card,.overview-pane,.compact-summary,.atlas-selection-summary,.mini-stat {
 background:linear-gradient(135deg,#ffffff,#f1f7fb)!important;
 border-color:#cddfeb!important;
 box-shadow:0 5px 18px rgba(32,74,100,.04)!important;
}
.metric-label,.metric-foot,.mini-stat-label {color:#567087!important;}
.metric-value,.card-title,.atlas-action strong,.overview-pane h3,
.overview-chip b,.compact-summary h3,.compact-summary strong,
.atlas-selection-summary .winner,.mini-stat-value {color:#193650!important;}
.card-note,.overview-pane p,.compact-summary p,.atlas-selection-summary .detail,
.atlas-selection-summary .hint,.subheading p,.overview-meta p,.overview-lead {
 color:#526f85!important;
}
.atlas-action {
 background:linear-gradient(125deg,#fff,#e9f4fa)!important;
 border-color:#c9dce8!important;
 box-shadow:0 5px 18px rgba(30,70,110,.04)!important;
}
.atlas-action p,.overview-chip span {color:#58738a!important;}
.overview-chip {background:#edf6fb!important;border-color:#cbdde9!important;}
.overview-thought {color:#087d87!important;}
.rank-top strong {color:#243b55!important;}
.rank-top span {color:#ac4d41!important;}
.rank-track {background:#dce8f0!important;}
.caption-note {color:#617d90!important;}
.warning-note {background:#fff5eb!important;border-color:#dfbfa7!important;color:#6b503c!important;}
.warning-note strong {color:#944c32!important;}
.footer-brand {border-color:#ccdae6!important;color:#5a738a!important;}
.sidebar-scale {border-color:#d0dfea!important;}
.sidebar-scale-row {border-color:#d3e1ea!important;color:#3d5870!important;}
.scale-num {color:#087b84!important;}
/* Anasayfadaki TR / Yaşam / Ticaret / Afet illüstrasyonu */
.atlas-orbit .orbit-ring {border-color:#95c2cf!important;}
.atlas-orbit .orbit-center {
 background:linear-gradient(145deg,#d2edf2,#f1faff)!important;
 border-color:#70b8c4!important;box-shadow:0 0 24px rgba(50,143,156,.12)!important;
}
.orbit-center strong {color:#185466!important;}
.orbit-center span {color:#477a86!important;}
.orbit-node.life {background:#d7f3ed!important;color:#246758!important;border-color:#83c5b3!important;}
.orbit-node.trade {background:#fff0dd!important;color:#83552c!important;border-color:#d7b892!important;}
.orbit-node.disaster {background:#e2eafb!important;color:#405b87!important;border-color:#aebedd!important;}
/* Mavi Analizler menu ailesi kalir; diger menuler canli kirmizi kalir. */
[data-testid="stSidebar"] [data-testid="stExpander"] {
 background:transparent!important;border-color:#ccdde9!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
 color:#fff!important;fill:currentColor!important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button {color:#fff!important;}
/* Radio ve checkbox etiketleri aydinlik modda okunakli */
[data-testid="stMain"] [data-testid="stRadio"] [role="radiogroup"] label,
[data-testid="stMain"] [data-testid="stCheckbox"] label {color:#223c57!important;}
</style>"""


ORTAK_KONTROL_CSS = r"""<style>
/* AFET ATLAS · etkilesimli kontroller — gece/gunduz ortak, tutarli kirmizi */
:root {--atlas-red:#f04e66;--atlas-red-hover:#ff647a;--atlas-red-dark:#cf3652;}
/* 1. Tum Streamlit selectbox ve multiselect: gercek BaseWeb kok, tetikleyici, metin ve ok. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
.stApp .stSelectbox [data-baseweb="select"] > div,
.stApp [data-baseweb="select"] [aria-haspopup="listbox"] {
 background:#f04e66!important;
 background-color:#f04e66!important;
 border-color:#ff9baa!important;
 border-radius:12px!important;
 color:#fff!important;
 min-height:44px!important;
 box-shadow:0 3px 12px rgba(220,49,82,.15)!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover,
.stApp [data-baseweb="select"] [aria-haspopup="listbox"]:hover {
 background:#ff647a!important;background-color:#ff647a!important;
 border-color:#ffc1cb!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
 outline:2px solid #ffb5c1!important;outline-offset:2px!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] *,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] *,
.stApp [data-testid="stSelectbox"] [role="combobox"] *,
.stApp [data-testid="stMultiSelect"] [role="combobox"] * {
 color:#fff!important;
 font-size:15px!important;
 font-weight:700!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] input,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] input {
 color:#fff!important;caret-color:#fff!important;
 -webkit-text-fill-color:#fff!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder {
 color:#ffe7eb!important;opacity:1!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] svg,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
 color:#fff!important;fill:currentColor!important;
}
/* BaseWeb secenek listeleri portal uzerinde, kutunun disinda render edilir. */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] [role="listbox"],
[data-baseweb="select"] [role="listbox"] {
 background:#fff!important;border:1px solid #f0a9b5!important;
 box-shadow:0 12px 32px rgba(17,32,60,.19)!important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"] {
 background:#fff!important;color:#203249!important;font-weight:600!important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"][aria-selected="true"] {
 background:#ffdae1!important;color:#8a2339!important;
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
/* Her iki temada da kontrol etiketleri yeterince okunakli */
.stApp [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stRadio"] [data-testid="stWidgetLabel"] p {
 font-size:14px!important;font-weight:700!important;
}
/* GUNDUZ: tercih seceneklerinin arka planini acik renklere cevir. */
.stApp:has([data-atlas-day="true"]) .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label {
 background:#fff!important;border-color:#cbdbe7!important;
}
.stApp:has([data-atlas-day="true"]) .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
 background:#ffe0e6!important;border-color:#f04e66!important;
}
.stApp:has([data-atlas-day="true"]) .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label p,
.stApp:has([data-atlas-day="true"]) .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label span {
 color:#213d58!important;
}
@media(max-width:680px){
 .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {min-height:42px!important;}
 .stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label {min-height:48px!important;padding:9px 11px!important;}
}
</style>"""


def gunduz_tema_css() -> str:
    return GUNDUZ_CSS


def ortak_kontrol_css() -> str:
    return ORTAK_KONTROL_CSS
