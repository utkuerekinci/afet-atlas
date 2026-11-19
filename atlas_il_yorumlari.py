"""Ana haritada 81 il için aynı ezber paragrafı yerine veri profili yorumları."""
from __future__ import annotations
import pandas as pd


def _metric(series, value):
    s=pd.to_numeric(series,errors='coerce').dropna()
    if not len(s):return 0.0
    return float((s <= float(value)).mean())


def _count(v):
    return f'{int(v):,}'.replace(',','.')


def yasam_il_yorumu(local:pd.DataFrame, provinces:pd.DataFrame, city:str, label:str) -> str:
    local=local.sort_values(['nufus','ilce'],ascending=[False,True])
    top=local.iloc[0]
    second=local.iloc[1] if len(local)>1 else None
    total=float(local.nufus.sum())
    share=float(top.nufus)/total if total else 0
    parts=[]
    if share>.40:
        parts.append(f'{city} nüfusunun büyük bölümü {top.ilce} çevresinde toplanıyor; bu merkezî yapı, hizmet ve ulaşım tercihlerinde tek bir ilçeyi önemli hâle getiriyor.')
    elif share<.18:
        parts.append(f'{city} nüfusu tek bir ilçeye yığılmaktan çok farklı yerleşimlere dağılıyor. En kalabalık ilçe {top.ilce} olsa da şehrin yaşam seçeneklerini yalnızca bu merkezle sınırlamamak gerekir.')
    else:
        parts.append(f'{city} içinde {top.ilce} nüfus açısından başı çekiyor. Bununla birlikte şehrin yerleşim yapısı, tek merkezli bir karar yerine farklı ilçeleri karşılaştırmayı anlamlı kılıyor.')
    if second is not None:
        if float(top.nufus)>float(second.nufus)*1.6:
            parts.append(f'{second.ilce} ile arasındaki nüfus farkı belirgin; günlük hizmetlerin talebi bakımından {top.ilce} öne çıksa da bu tek başına yaşam tercihini belirlememeli.')
        else:
            parts.append(f'{second.ilce} nüfus bakımından yakın bir alternatif. Bu iki ilçeyi ayırmak için gelişmişlik ve ulaşım profilini birlikte değerlendirmek daha yararlı.')
    if 'sege_sira' in local and local.sege_sira.notna().all():
        developed=local.sort_values('sege_sira').iloc[0]
        if developed.ilce==top.ilce:
            parts.append(f'{top.ilce}, hem nüfus büyüklüğünde hem SEGE gelişmişlik sırasında ilin öne çıkan ilçesi; merkez etkisiyle sosyal ve ekonomik seçenekler aynı yerde buluşuyor.')
        else:
            parts.append(f'En kalabalık ilçe {top.ilce} iken SEGE sıralamasında {developed.ilce} daha avantajlı. Bu ayrım, en büyük yerleşimin her zaman en gelişmiş seçenek olmadığını gösteriyor.')
    if 'osm_ulasim' in local and pd.to_numeric(local.osm_ulasim,errors='coerce').notna().all():
        transit=local.sort_values('osm_ulasim',ascending=False).iloc[0]
        if transit.ilce!=top.ilce:
            parts.append(f'Ulaşım duraklarının en yoğun kaydedildiği ilçe ise {transit.ilce}; günlük hareketlilikte nüfus merkezi dışındaki seçenekleri de incelemek değerli.')
        else:
            parts.append(f'Ulaşım kayıtları da {top.ilce} çevresinde yoğunlaşıyor; nüfus ve erişimin aynı ilçede buluşması, konum seçiminin mahalle ölçeğinde yapılmasını önemli kılıyor.')
    if label=='Sosyoekonomik gelişmişlik':
        parts.append('Yaşam için ilk araştıracağım iki adres, nüfus odağı ile gelişmişlikte başı çeken ilçe olurdu.')
    else:
        parts.append('Yaşam tercihini nüfus büyüklüğüne göre değil, bu merkezler arasındaki gündelik erişim ve gelişmişlik farkına göre şekillendirmek daha mantıklı.')
    return ' '.join(parts)


def ticaret_il_yorumu(local:pd.DataFrame, city:str, label:str, district_col:str) -> str:
    mapping={'Yeme-içme':'yeme-içme','Perakende':'perakende','Hizmetler':'hizmet','Lojistik':'lojistik ve depolama','Ulaşım bağlantıları':'ulaşım'}
    sector=mapping[label]
    local=local.sort_values([district_col,'ilce'],ascending=[False,True])
    a=local.iloc[0]
    b=local.iloc[1] if len(local)>1 else None
    cnt=float(a[district_col])
    total=float(pd.to_numeric(local[district_col],errors='coerce').sum())
    share=cnt/total if total else 0
    population=local.sort_values('nufus',ascending=False).iloc[0]
    parts=[]
    if not total:
        return (f'{city} içinde {sector} için belirgin bir kayıtlı merkez görünmüyor. '
                f'Bu durumda {population.ilce} gibi nüfus çekirdeği güçlü ilçeler başlangıç karşılaştırması sunar; '
                'fırsat seçimini tek sektör haritası yerine yerleşim ve erişimle birlikte kurmak gerekir.')
    if share>.60:
        parts.append(f'{city} içindeki {sector} faaliyetleri {a.ilce} ilçesinde güçlü biçimde toplanmış. Böyle bir kümelenme, sektörde belirgin bir merkez oluştururken işletmelerin birbirinden ayrışmasını da kritik hâle getiriyor.')
    elif share>.30:
        parts.append(f'{city} için {sector} haritasının ağırlık noktası {a.ilce}. Bu ilçe, iş fikrini var olan faaliyetlerle yan yana konumlandırma fırsatı verirken rekabetin niteliğini de önemli kılıyor.')
    else:
        parts.append(f'{city} içinde {sector} tek bir merkeze sıkışmamış; {a.ilce} en çok kaydı taşısa da faaliyetler başka ilçelere de yayılıyor. Bu desen, tek bir ana cadde yerine farklı müşteri çevrelerini düşünmeyi gerektiriyor.')
    if b is not None:
        if float(a[district_col])>float(b[district_col])*1.8 and cnt-float(b[district_col])>=3:
            parts.append(f'{b.ilce} ile arasındaki fark büyük. Yeni bir işletmenin bu odakta görünür olması için fiyat veya üründen öte, net bir hedef kitle belirlemesi daha anlamlı.')
        elif float(b[district_col])>0:
            parts.append(f'{b.ilce} de aynı faaliyetlerde dikkat çeken bir alternatif; iki merkez arasında yalnızca kayıt toplamını değil müşteriyle kurulacak ilişkiyi karşılaştırmak gerekir.')
    if a.ilce==population.ilce:
        parts.append(f'{a.ilce} aynı zamanda ilin en kalabalık ilçesi. Bu birliktelik, yerleşik nüfusla ticari merkez arasındaki bağın araştırılmasını değerli kılıyor.')
    else:
        parts.append(f'İlin en kalabalık ilçesi {population.ilce} olmasına rağmen bu alanda {a.ilce} öne çıkıyor. Demek ki nüfus büyüklüğü tek başına faaliyetlerin nerede kümelendiğini açıklamıyor.')
    if label=='Yeme-içme':
        parts.append('Kafe ve restoran açmak için en ilginç soru, mevcut kümelenmenin parçası olmak mı yoksa nüfusa yakın yeni bir yerel odak yaratmak mı olduğudur.')
    elif label=='Perakende':
        parts.append('Günlük ihtiyaç mağazası ile uzmanlaşmış ürün mağazasını farklı yer seçimleri olarak karşılaştırmak, bu ticari dokudan daha iyi yararlanabilir.')
    elif label=='Hizmetler':
        parts.append('Düzenli ziyaret gerektiren kişisel bakım, eğitim desteği veya bakım-onarım gibi hizmetleri, müşteri çevresine yakınlık üzerinden önceliklendirirdim.')
    elif label=='Lojistik':
        parts.append('Lojistik yatırımlarında sonraki karar, kayıt sayısına göre değil bağlantı yolları, teslimat mesafesi ve işletmeye uygun parsel üzerinden verilmelidir.')
    else:
        parts.append('Ulaşım odağına yakın iş modelleriyle konut çevresine yaslanan işletmelerin avantajları farklıdır; hangisinin daha uygun olduğunu sektör belirler.')
    return ' '.join(parts)


def yangin_il_yorumu(city:str, year:int, col:str, year_df:pd.DataFrame, previous:pd.DataFrame|None=None) -> str:
    r=year_df[year_df['İl']==city]
    if len(r)!=1:raise ValueError('Yangın tablosunda il eksik')
    a=r.iloc[0]
    if pd.isna(a[col]):return f'{city} için seçilen yangın göstergesinin il düzeyinde sayısal değeri bulunmuyor.'
    ranked=year_df.dropna(subset=[col]).sort_values([col,'İl'],ascending=[False,True]).reset_index(drop=True)
    position=int(ranked.index[ranked['İl'].eq(city)][0])+1
    if col=='Yangın sayısı':
        if position<=10:
            lead=f'{city}, {year} yangın sayısında Türkiye sıralamasının ön kısmında. Çok sayıda olay, önleme ve hızlı müdahale kapasitesini bu ilde özellikle önemli kılıyor.'
        elif position>=65:
            lead=f'{city}, {year} yangın sayısında daha alt sıralarda. Bu profil, yerel önceliği olay yoğunluğundan ziyade hazırlık ve erken müdahale düzenine kaydırıyor.'
        else:
            lead=f'{city}, {year} yangın sayısında orta sıralarda yer alıyor. Burada olay adediyle müdahale kapasitesini birlikte düşünmek daha anlamlı.'
    else:
        if position<=10:
            lead=f"{city}, {year} yılında yanan alan bakımından Türkiye'nin öne çıkan illerinden. Büyük alan kaybı, afetin yalnızca kaç kez yaşandığına değil sonuçlarının ağırlığına da bakmayı gerektiriyor."
        else:
            lead=f'{city} için {year} yanan alan profili, yangın sayısıyla birlikte değerlendirildiğinde daha anlamlı hâle geliyor.'
    parts=[lead]
    count=a.get('Yangın sayısı'); area=a.get('Yanan alan (ha)')
    if pd.notna(count) and pd.notna(area) and float(count)>0:
        ratio=float(area)/float(count)
        country=year_df.dropna(subset=['Yangın sayısı','Yanan alan (ha)'])
        av=float(country['Yanan alan (ha)'].sum())/float(country['Yangın sayısı'].sum())
        if ratio>av*1.75:
            parts.append('Yangın başına düşen yanan alan Türkiye ortalamasından belirgin biçimde daha yüksek; bu, olay sonuçlarını azaltmaya yönelik hazırlığın ayrı ele alınmasını gerektiriyor.')
        elif ratio<av*.5:
            parts.append('Yangın başına düşen yanan alan Türkiye ortalamasından düşük; sayı ile etkilenmiş alanın aynı tabloyu anlatmadığı burada görülebiliyor.')
        else:
            parts.append('Yangın başına etkilenen alan Türkiye ortalamasına yakın; olay sayısı ile alan kaybı birlikte okunmalı.')
    if previous is not None:
        prior=previous[previous['İl']==city]
        if len(prior)==1 and pd.notna(prior.iloc[0][col]):
            earlier=float(prior.iloc[0][col]); current=float(a[col])
            if earlier>0 and current>earlier*1.25:
                parts.append(f'Önceki yıla göre {col.lower()} artmış; {city} için yakın dönem değişimi, hazırlık önceliklerini belirlemede dikkate alınabilir.')
            elif earlier>0 and current<earlier*.75:
                parts.append(f'Önceki yıla göre {col.lower()} azalmış; buna rağmen yıllar arasındaki fark tek başına kalıcı bir eğilim sayılmaz.')
            else:
                parts.append(f'Önceki yıl ile {col.lower()} düzeyi birbirine yakın. Bölgenin hazırlık ihtiyacını tek yıllık değişime bağlamamak daha doğru olur.')
    return ' '.join(parts)


def yangin_lider_yorumu(rank:pd.DataFrame,year:int,col:str,previous:pd.DataFrame|None=None)->str:
    a=rank.iloc[0]; b=rank.iloc[1] if len(rank)>1 else None
    city=str(a['İl'])
    main=yangin_il_yorumu(city,year,col,rank,previous)
    if b is None:return main
    lead=float(a[col]); other=float(b[col]); gap=lead-other
    if other>0 and lead>other*1.8:
        detail=f'{b["İl"]} ile arasındaki belirgin fark, bu yılın en yoğun etki gösteren ilinin {city} olduğunu vurguluyor.'
    elif gap>=0:
        detail=f'{b["İl"]} değeri de yakın; iki ilin sonuçları birbirine yaklaşırken önleme kapasitesi her ikisinde de önem kazanıyor.'
    else:detail=''
    return main+' '+detail
