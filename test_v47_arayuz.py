"""v4.7: menü, karşılaştırma, tek birincilik yorumu ve ticaret haritası."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest
import pandas as pd

ROOT=Path(__file__).parent
ATLAS=(ROOT/'atlas_ui.py').read_text(encoding='utf-8')
APP=(ROOT/'app.py').read_text(encoding='utf-8')


def extract(*funcs,ns=None):
    nodes=[n for n in ast.parse(ATLAS).body
           if (isinstance(n,ast.FunctionDef) and n.name in funcs)
           or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_TR_SORT' for t in n.targets))]
    assert sum(isinstance(n,ast.FunctionDef) for n in nodes)==len(funcs)
    namespace=ns or {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),
                 str(ROOT/'atlas_ui.py'),'exec'),namespace)
    return namespace


class Context:
    def __enter__(self):return self
    def __exit__(self,*args):return False


class FakeUI:
    def __init__(self):
        self.options={}
        self.tables=[]
        self.infos=[]
        self.captions=[]
    def expander(self,*args,**kwargs):return Context()
    def columns(self,*args,**kwargs):return [Context(),Context()]
    def selectbox(self,label,options,index=0,**kwargs):
        self.options[label]=list(options)
        if label=='İkinci il' and kwargs.get('disabled'):assert options==['Ankara']
        return options[index]
    def dataframe(self,frame,**kwargs):self.tables.append(frame.copy())
    def info(self,msg):self.infos.append(msg)
    def caption(self,msg):self.captions.append(msg)


class V47Tests(unittest.TestCase):
    def test_menu_renkleri(self):
        for value in ['background:#204b76','background:#193d62','background:#572f3c',
                      'font-size:15px!important','font-size:14px!important']:
            self.assertIn(value,APP)
        for section in ['Genel Bakış','Afet Analizi','Yaşam Kalitesi','Ticari Potansiyel',
                        'Siz Sorun','Yardım','Veri ve Yöntem']:
            self.assertIn(section,APP)

    def test_tek_yorum_her_modda(self):
        self.assertEqual(ATLAS.count('aciklama_alani(local_rank,local_meta)'),1)
        part=ATLAS.split('def siralama_alani(')[1].split('def yasam_ticaret_sayfasi(')[0]
        self.assertNotIn('aciklama_alani(',part)
        self.assertIn('_iki_ilce_karsilastir(',part)
        self.assertIn('sayisal_ayrintilar_alani(',part)
        self.assertLess(part.index('_iki_ilce_karsilastir('),part.index('sayisal_ayrintilar_alani('))

    def test_sehir_ve_ilce_alfabetik(self):
        ns=extract('turkce_sirala',ns={'__name__':'test'})
        f=ns['turkce_sirala']
        self.assertEqual(sorted(['İzmir','Iğdır','Çankırı','Ankara'],key=f),
                         ['Ankara','Çankırı','Iğdır','İzmir'])
        self.assertEqual(sorted(['Üsküdar','Çankaya','Şişli','Avcılar'],key=f),
                         ['Avcılar','Çankaya','Şişli','Üsküdar'])

    def test_osm_sayisal_alani_kapali(self):
        self.assertIn("with st.expander(f'İşletme ve ulaşım sayıları · {city}', expanded=False)",ATLAS)
        self.assertIn('Sektörel fırsat puanı',ATLAS)
        self.assertIn('Ortalama ilçe SEGE sırası',ATLAS)
        self.assertIn('İki ilçeyi karşılaştır',APP)
        self.assertIn('önce il, ardından ilçe',APP)

    def test_karsilastirma_yonetimi(self):
        mock=FakeUI()
        records=pd.DataFrame([
            {'il':'İzmir','ilce':'Konak','nufus':22,'score':71},
            {'il':'Ankara','ilce':'Çankaya','nufus':10,'score':82},
            {'il':'Ankara','ilce':'Akyurt','nufus':12,'score':69},
            {'il':'İzmir','ilce':'Bornova','nufus':17,'score':65},
        ])
        ns=extract('turkce_sirala','_iki_ilce_karsilastir',ns={'pd':pd,'st':mock})
        ns['_iki_ilce_karsilastir'](records,'ticaret','Türkiye geneli','Ankara','score')
        self.assertEqual(mock.options['Birinci il'],['Ankara','İzmir'])
        self.assertEqual(mock.options['Birinci ilçe'],['Bornova','Konak'])
        self.assertEqual(mock.options['İkinci ilçe'],['Akyurt','Çankaya'])
        self.assertEqual(len(mock.tables),1)
        self.assertEqual(len(mock.tables[0]),2)
        self.assertTrue(mock.captions)

    def test_gercek_973_ilce_ulusal_il_katmani(self):
        from ilce_veri import fetch_population,read_sege_csv,combine
        from ticaret_veri import zenginlestir_ilceler
        from atlas_analiz import sirala_ilceler
        districts,_=combine(fetch_population(),read_sege_csv())
        districts,status=zenginlestir_ilceler(districts)
        self.assertEqual(len(districts),973)
        self.assertTrue(status['osm_aktif'])
        ns=extract('ticari_firsat_il_katmani',ns={'pd':pd,'sirala_ilceler':sirala_ilceler})
        for sector in ['Yeme-içme','Market / perakende','Hizmetler','Lojistik / depolama']:
            agg=ns['ticari_firsat_il_katmani'](districts,sector)
            self.assertEqual(len(agg),81)
            self.assertTrue(agg['Sektörel fırsat puanı'].between(0,100).all())
            self.assertFalse(agg['Sektörel fırsat puanı'].isna().any())

if __name__=='__main__':unittest.main()
