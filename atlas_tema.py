"""Afet Atlas v4.10: oturum bazlı açık tema.

Koyu tasarım app.py'deki orijinal stil olarak kalır. Kullanıcı gündüz
modunu seçtiğinde yalnızca görsel CSS eklenir; analiz ve veri değişmez.
"""

GUNDUZ_CSS = r"""<style>
/* Afet Atlas — GÜNDÜZ MODU. v4.9 karanlık tasarımın okunaklı açık eşleniği. */
:root {
  color-scheme: light !important;
  --background-color: #f4f7fc;
  --secondary-background-color: #ffffff;
  --text-color: #21344b;
  --primary-color: #e43f59;
}
html, body, [data-testid="stAppViewContainer"] {color:#23374f!important;background:#f4f7fc!important;}
.stApp {
  color:#21344b!important;
  background:radial-gradient(ellipse 48% 36% at 83% 0%,rgba(93,172,196,.13),transparent 82%),
    radial-gradient(ellipse 52% 38% at 7% 32%,rgba(122,164,214,.10),transparent 80%),#f4f7fc!important;
}
[data-testid="stHeader"] {background:transparent!important;}
[data-testid="stSidebar"] {background:#eaf1f9!important;border-right:1px solid #cbd9e7!important;}
[data-testid="stSidebar"] p:not(button p) {color:#334b64!important;}
[data-testid="stSidebar"] label {color:#24405d!important;}
[data-testid="stSidebar"] hr {border-color:#cfdae8!important;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] label, [data-testid="stMain"] [data-testid="stCaptionContainer"] {
  color:#334b64;
}
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] h4 {color:#1b3049!important;}
[data-testid="stMain"] a {color:#087b87!important;}
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"] span {color:#29435e!important;}
/* Streamlit bileşen yüzeyleri */
[data-testid="stExpander"], [data-testid="stMetric"], [data-testid="stDataFrame"],
[data-testid="stVerticalBlockBorderWrapper"] > div {
  background:#ffffff!important;border-color:#d4e0ec!important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
  color:#1f3d55!important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {color:#526a83!important;}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {color:#172e4a!important;}
[data-testid="stDataFrame"] {border:1px solid #d2e0ed!important;}
[data-testid="stAlert"] {border-radius:14px;}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input,
[data-testid="stFileUploader"] section {
  background:#fff!important;color:#223851!important;border-color:#bdcee0!important;
}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label,
[data-testid="stToggle"] label {color:#294259!important;}
[data-testid="stToggle"] label p {color:#294259!important;}
[data-testid="stToggle"] [role="switch"] {border-color:#6c879d!important;}
button[data-baseweb="tab"] {color:#51677f!important;}
button[data-baseweb="tab"][aria-selected="true"] {color:#087a88!important;}
[data-baseweb="tab-highlight"] {background-color:#087a88!important;}
[data-baseweb="tab-border"] {background-color:#d5e0eb!important;}
[data-testid="stDownloadButton"] button {background:#e5f2f6!important;border-color:#a1c9ce!important;color:#086b72!important;}
[data-testid="stDownloadButton"] button:hover {background:#d5ecf0!important;}
/* Önceden hazırlanmış HTML tasarım blokları */
.hero, .hero-return, .compact-hero {
  background:linear-gradient(112deg,#e8f4f9 0%,#f4f8fe 59%,#d9edf2 100%)!important;
  border-color:#b9d5df!important;box-shadow:0 13px 35px rgba(35,74,105,.07)!important;
}
.hero:before {opacity:.42;}
.hero h1, .hero-return h1, .compact-hero h1, .hero h2,
.hero-return h2 {color:#193752!important;}
.hero h1 em, .hero-return h1 em {color:#087a85!important;}
.hero p,.hero-return p,.compact-hero p,.hero .module-title {color:#445e77!important;}
.overline,.kicker,.filter-strip-title,.overview-pane .eyebrow {color:#087a81!important;}
.dot {background:#0da8a0!important;box-shadow:0 0 10px rgba(13,168,160,.24)!important;}
.hero-tag,.quick-facts span {
  background:#eaf6f8!important;border-color:#bfd9dc!important;color:#24576b!important;
}
.metric {background:linear-gradient(135deg,#fff,#f0f6fb)!important;border-color:#d1dfeb!important;}
.metric-label {color:#536c84!important;}
.metric-value {color:#18344e!important;}
.metric-foot {color:#607a91!important;}
.subheading p,.overview-meta p,.overview-lead {color:#59738a!important;}
.card,.overview-pane,.compact-summary,.atlas-selection-summary,.mini-stat {
  background:linear-gradient(130deg,#fff,#f0f6fa)!important;border-color:#cedfea!important;
}
.card-title,.atlas-action strong,.overview-pane h3,.overview-chip b,
.compact-summary h3,.compact-summary strong,.atlas-selection-summary .winner,
.mini-stat-value {color:#1d3852!important;}
.card-note,.overview-pane p,.compact-summary p,.atlas-selection-summary .detail,
.atlas-selection-summary .hint,.mini-stat-label {color:#4d687f!important;}
.atlas-action {background:linear-gradient(125deg,#e9f4f9,#f8fbfd)!important;border-color:#c8dde6!important;}
.atlas-action p,.overview-chip span {color:#58758c!important;}
.overview-chip {background:#f2f8fc!important;border-color:#d1e1eb!important;}
.overview-thought {color:#167780!important;}
.sidebar-head {color:#183a59!important;}
.sidebar-small,.sidebar-label {color:#55728a!important;}
.sidebar-scale {border-color:#cbdbe8!important;}
.sidebar-scale-row {border-color:#d3e1eb!important;color:#36556d!important;}
.scale-num {color:#087c87!important;}
.rank-top strong {color:#253c56!important;}
.rank-top span {color:#c05349!important;}
.rank-track {background:#dce7f0!important;}
.caption-note {color:#607990!important;}
.warning-note {background:#fff3e9!important;border-color:#e6c9ab!important;color:#684c34!important;}
.warning-note strong {color:#8b412a!important;}
.footer-brand {border-color:#c9d9e6!important;color:#627b91!important;}
.overview-meta h2 {color:#1c3953!important;}
/* Yaşam / Ticaret / Afet yörünge çizimi gündüz modunda da seçilebilir */
.atlas-orbit .orbit-ring {border-color:#92bec8!important;}
.atlas-orbit .orbit-center {background:linear-gradient(145deg,#d2ecee,#e6f4f9)!important;border-color:#69b1b7!important;box-shadow:0 0 24px rgba(71,145,154,.13)!important;}
.orbit-center strong {color:#175668!important;}
.orbit-center span {color:#4b8992!important;}
.orbit-node.life {background:#d3f2ec!important;color:#236b62!important;border-color:#7fbaab!important;}
.orbit-node.trade {background:#fff0d9!important;color:#795129!important;border-color:#cbae87!important;}
.orbit-node.disaster {background:#e2e9fc!important;color:#455a85!important;border-color:#a6b8d9!important;}
/* Harita renkleri aynı verileri temsil eder; yalnızca çevreleyen paneller açık. */
[data-testid="stSidebar"] [data-testid="stButton"] button {color:#fff!important;}
[data-testid="stSidebar"] [data-testid="stExpander"] {background:transparent!important;border-color:#c9dceb!important;}
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {color:#fff!important;}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stButton"] button {color:#fff!important;}
[data-testid="stSidebar"] [role="radiogroup"] label {background:#e5eff8!important;border-color:#bfd2e3!important;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {border-color:#438cc4!important;}
/* Kırmızı seçim kutularını iki temada da koru. */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div {background:#df4059!important;color:#fff!important;border-color:#fb7284!important;}
[data-baseweb="popover"] [role="listbox"] {background:#fff!important;border:1px solid #e89eab!important;}
[data-baseweb="popover"] [role="option"] {color:#1e3249!important;}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {background:#fce2e8!important;color:#7b1f38!important;}
</style>"""


def gunduz_tema_css() -> str:
    """Yalnızca açık tema seçildiğinde yerleştirilecek CSS."""
    return GUNDUZ_CSS
