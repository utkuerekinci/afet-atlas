"""Afet Atlas - only dark-mode controls; selected map/analysis filters in blue.

The actual Streamlit 1.59+ selectbox trigger is a react-aria Group, not BaseWeb.
"""

ORTAK_KONTROL_CSS = r"""<style>
/* Afet Atlas 4.16: only the nine requested filter families are blue. 
   Streamlit 1.59+ moved st.selectbox from BaseWeb to React Aria Group+Input.
   Target the actual painted Group, not the deleted data-baseweb=select element.
   Preserve fallback for older Streamlit. */
:root {
  --atlas-filter-blue: #204b76;
  --atlas-filter-blue-hover: #2b608f;
  --atlas-filter-stroke: #438bc1;
}
/* Every filter is identified by its widget key, never the label or column index.
   st-key-il_select_ covers every city/location picker in all modules. */
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group),
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) [data-baseweb="select"] > div:first-child {
  background: var(--atlas-filter-blue) !important;
  background-color: var(--atlas-filter-blue) !important;
  background-image: none !important;
  color: #ffffff !important;
  border: 1px solid var(--atlas-filter-stroke) !important;
  border-radius: 11px !important;
  min-height: 43px !important;
  box-shadow: 0 3px 12px rgba(8,25,52,.20) !important;
}
/* React Aria: input and chevron are children of StyledGroup. */
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group) input,
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) [data-baseweb="select"] input {
  background: transparent !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  /* filter_mode=None zaten klavye girisini kapatir. Gorunur yazi imlecini de gizle. */
  caret-color: transparent !important;
  cursor: pointer !important;
  user-select: none !important;
  -webkit-user-select: none !important;
  font-weight: 700 !important;
  font-size: 15px !important;
}
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group) input::placeholder {
  color: #dcecff !important;
  -webkit-text-fill-color: #dcecff !important;
}
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group) button,
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) [data-baseweb="select"] svg {
  background: transparent !important;
  color: #ffffff !important;
  fill: currentColor !important;
}
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group) svg {
  color: #ffffff !important;
  fill: currentColor !important;
}
/* Hover or focused state: same blue family. */
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group):is(:hover,[data-hovered]),
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) :is([role="group"], .react-aria-Group):is(:focus-within,[data-focus-within]),
.stApp :is([class*="st-key-home_v40_layer_"],
 .st-key-yasam_layer,
 .st-key-ticaret_layer,
 .st-key-v36_fire_metric,
 [class*="st-key-il_select_"],
 .st-key-v34_sektor,
 .st-key-v34_preference,
 [class*="st-key-district_search_"],
 .st-key-v36_disaster,
 .st-key-v45_year_start,
 .st-key-v45_year_end,
 .st-key-v45_min_m,
 .st-key-v45_distance) [data-baseweb="select"] > div:first-child:hover {
  background: var(--atlas-filter-blue-hover) !important;
  background-color: var(--atlas-filter-blue-hover) !important;
  border-color: #73b9ee !important;
}
/* Siz Sorun > Ornek soru: secim listesi acilir, ancak yazma imleci gorunmez.
   filter_mode=None yazma/arama islevini kapatir. Bu CSS sadece o kutuya aittir.
   "Sorunuz" text_area ise tamamen duzenlenebilir kalir. */
.stApp .st-key-adk_example_question input,
.stApp .st-key-adk_example_question input[role="combobox"],
.stApp .st-key-adk_example_question .react-aria-Input {
  caret-color: transparent !important;
  cursor: pointer !important;
  user-select: none !important;
  -webkit-user-select: none !important;
}
/* Do not recolor dropdowns belonging to district comparisons or admin. */
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

/* Haritanın üzerinde görünen kontrol. transform görsel konumu değiştirir,
   ancak ardından gelen sıra tablosunun yerleşimini yukarı çekmez. */
.stApp [class*="st-key-map_reset_"] {
 position:relative!important;
 transform:translate(13px,-565px)!important;
 z-index:30!important;
 width:max-content!important;
 max-width:calc(100% - 24px)!important;
}
.stApp [class*="st-key-map_reset_"] button,
.stApp [class*="st-key-map_reset_"] [data-testid^="stBaseButton"] {
 background:rgba(9,19,33,.92)!important;
 border:1px solid #54728a!important;
 color:#f7fbff!important;
 border-radius:999px!important;
 min-height:36px!important;
 padding:6px 12px!important;
 box-shadow:0 8px 20px rgba(0,0,0,.26)!important;
}
.stApp [class*="st-key-map_reset_"] button:hover,
.stApp [class*="st-key-map_reset_"] [data-testid^="stBaseButton"]:hover {
 background:rgba(22,38,58,.97)!important;
 border-color:#8eb6d4!important;
}
.stApp [class*="st-key-map_reset_"] button p,
.stApp [class*="st-key-map_reset_"] [data-testid^="stBaseButton"] p {
 color:#f7fbff!important;font-size:13px!important;font-weight:700!important;
}
@media(max-width:680px){
 .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {min-height:42px!important;}
 .stApp .st-key-yasam_tercih_grubu [data-testid="stRadio"] [role="radiogroup"] label {min-height:48px!important;padding:9px 11px!important;}
 .stApp [class*="st-key-map_reset_"] {transform:translate(7px,-565px)!important;}
}

</style>"""


def ortak_kontrol_css() -> str:
    return ORTAK_KONTROL_CSS
