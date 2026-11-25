"""v4.6: eski ana sayfa görseli, menü ve yaşam açıklaması yerleşimi regresyonları."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest
import pandas as pd

ROOT=Path(__file__).parent
APP=(ROOT/'app.py').read_text(encoding='utf-8')
ATLAS=(ROOT/'atlas_ui.py').read_text(encoding='utf-8')


class _Ctx:
    def __init__(self, st, name=None):self.st,self.name=st,name
    def __enter__(self):
        if self.name:
            self.st.scope=self.name
        return self
    def __exit__(self,exc_type,exc,tb):return False
    def selectbox(self,*args,**kwargs):return self.st.selectbox(*args,**kwargs)


class _FakeSt:
    def __init__(self):self.events=[];self.scope=None
    def tabs(self,names):return [_Ctx(self,'Türkiye geneli'),_Ctx(self,'İl içi')]
    def columns(self,*args,**kwargs):return (_Ctx(self),_Ctx(self))
    def markdown(self,*args,**kwargs):pass
    def caption(self,*args,**kwargs):pass
    def dataframe(self,*args,**kwargs):pass
    def expander(self,label,*args,**kwargs):
        if label=='İki ilçeyi karşılaştır':self.events.append((self.scope,'karşılaştır'))
        return _Ctx(self)
    def selectbox(self,label,choices,*args,**kwargs):return 0 if label=='Birinci ilçe' else 1
    def download_button(self,*args,**kwargs):pass


def _siralamayi_calistir(mode):
    source_ast=ast.parse(ATLAS)
    only=next(node for node in source_ast.body if isinstance(node,ast.FunctionDef) and node.name=='siralama_alani')
    mod=ast.fix_missing_locations(ast.Module(body=[only],type_ignores=[]))
    fake=_FakeSt()
    ranking=pd.DataFrame([{'Sıra':1,'il':'Ankara','ilce':'Çankaya','nufus':100,'score':83.2,
                           'sege_sira':1,'osm_yeme':12,'osm_ulasim':11},
                          {'Sıra':2,'il':'Ankara','ilce':'Gölbaşı','nufus':80,'score':80.4,
                           'sege_sira':2,'osm_yeme':9,'osm_ulasim':8}])
    def sirala_ilceler(*args):
        return ranking,{'puan_sutunu':'score','model':'Deneme', 'mod':mode,
                       'kapsam':args[2]}
    def explanation(*args):fake.events.append((fake.scope,'yorum'))
    def numeric(*args):fake.events.append((fake.scope,'sayısal'))
    ns={'pd':pd,'st':fake,'sirala_ilceler':sirala_ilceler,
        'aciklama_alani':explanation,'sayisal_ayrintilar_alani':numeric,
        'SEKTOR_SUTUNLARI':{'Yeme-içme':'osm_yeme'},'_bar':lambda *a:None,
        '_iki_ilce_karsilastir':lambda *args: fake.events.append((fake.scope,'karşılaştır'))}
    exec(compile(mod,str(ROOT/'atlas_ui.py'),'exec'),ns)
    ns['siralama_alani'](ranking,mode,'Ankara','Yeme-içme','Dengeli')
    return fake.events


class V46Regresyon(unittest.TestCase):
    def test_anasayfa_yorunge_eski_etiketlerle_geri_dondu(self):
        for tag in ('<strong>TR</strong><span>KEŞFET</span>',
                    '<div class="orbit-node life">YAŞAM</div>',
                    '<div class="orbit-node trade">TİCARET</div>',
                    '<div class="orbit-node disaster">AFET</div>'):
            self.assertIn(tag,APP)
        self.assertIn('.hero-return .atlas-orbit',APP)
        self.assertIn(' .hero-return .atlas-orbit {display:flex;',APP)

    def test_menu_tum_kilit_bolumleri_acar(self):
        for label,name in (('✦  Siz Sorun','Siz Sorun'),('ⓘ  Yardım','Yardım'),
                           ('▤  Veri ve Yöntem','Veri ve Yöntem')):
            self.assertIn(f"'{label}','{name}'", APP)
        for name in ('Siz Sorun','Yardım'):
            self.assertIn(f"elif module=='{name}':",APP)
        self.assertIn("heading('VERİ & YÖNTEM'",APP)
        self.assertIn("with st.expander('▾  Analizler'",APP)
        self.assertIn('def deprem_filtreleri()',APP)

    def test_yasamda_ustte_tek_yorum_alt_sekmelerde_karsilastirma(self):
        self.assertEqual(_siralamayi_calistir('yasam'),[
            ('Türkiye geneli','karşılaştır'),('Türkiye geneli','sayısal'),
            ('İl içi','karşılaştır'),('İl içi','sayısal')])
        self.assertIn('aciklama_alani(local_rank,local_meta)',ATLAS)

    def test_ticarette_ustte_tek_yorum_alt_sekmelerde_karsilastirma(self):
        self.assertEqual(_siralamayi_calistir('ticaret'),[
            ('Türkiye geneli','karşılaştır'),('Türkiye geneli','sayısal'),
            ('İl içi','karşılaştır'),('İl içi','sayısal')])
        self.assertNotIn('SEÇİLİ İLDE ÖNE ÇIKAN',ATLAS)


if __name__=='__main__':unittest.main()
