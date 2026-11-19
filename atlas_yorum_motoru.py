"""Afet Atlas v4.1 — veriye dayalı, API gerektirmeyen bağlamsal yorum üretimi.

Tek bir ortak paragraf yerine ilçenin profilini, model katkılarını, aynı
kapsamdaki alternatiflerini ve sektör/yaşam tercihini birlikte yorumlar.
Sözlük/şablon birleştirmesi deterministiktir; hiçbir yeni olay, kurum,
işletme, müşteri, gelir veya ilçe özelliği uydurulmaz.
"""
from __future__ import annotations
import math
import pandas as pd


def num(r, col):
    try:
        v = float(r.get(col, float('nan')))
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _percentile(series: pd.Series, value: float | None, lower_better=False):
    if value is None: return None
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty: return None
    # Genel profil; seçilen kapsamda bulunan gerçek satırlar kullanılır.
    return float((s.ge(value) if lower_better else s.le(value)).mean())


def _level(p, high=.75, low=.33):
    return 'yüksek' if p is not None and p >= high else 'düşük' if p is not None and p <= low else 'orta'


def _relation(a, b, col, threshold=.10):
    av=num(a,col)
    bv=num(b,col) if b is not None else None
    if av is None or bv is None: return 'bilinmiyor'
    margin=max(abs(bv)*threshold,1 if col.startswith('osm_') else .01)
    if av > bv + margin: return 'fazla'
    if av < bv - margin: return 'az'
    return 'yakın'


def _cluster_band(row, col):
    count=num(row,col)
    pop=num(row,'nufus')
    if count is None or pop is None or pop<=0:return None
    return count / pop * 10000


def _scope(meta, a):
    return 'Türkiye genelindeki' if meta['kapsam']=='Türkiye geneli' else f'{a.il} içindeki'


def _factor_summary(factors, runner):
    if runner is None:return None, None
    valid=[f for f in factors if f.get('katki_farki') is not None]
    plus=sorted((f for f in valid if f['katki_farki']>.05),key=lambda f:f['katki_farki'],reverse=True)
    minus=sorted((f for f in valid if f['katki_farki']<-.05),key=lambda f:f['katki_farki'])
    return (plus[0] if plus else None), (minus[0] if minus else None)


_QUEUES={
    'Yeme-içme': ('yeme-içme','kafe ve restoran','osm_yeme_icme'),
    'Market / perakende': ('perakende','market ve mağaza','osm_market_perakende'),
    'Hizmetler': ('hizmet sektörü','hizmet işletmesi','osm_hizmetler'),
    'Lojistik / depolama': ('lojistik ve depolama','lojistik tesisi','osm_lojistik'),
}


def _trade_business(sector, a, b, ranked):
    tag, noun, col=_QUEUES[sector]
    current=num(a,col)
    if current is None:return ('Yerleşik talebin büyüklüğü ve yerleşim yapısı bu tercih için başlangıç noktası oluyor.', 'verisiz')
    other=num(b,col) if b is not None else None
    ratio=_cluster_band(a,col)
    rr=_cluster_band(b,col) if b is not None else None
    if current == 0:
        # 0 OSM sayımını sıfır rekabet / hiç işletme yok anlamına çevirmeyin.
        return (f'{tag.capitalize()} için kayıtlı bir yoğunlaşma öne çıkmıyor; bu ilçe hakkında belirleyici sinyal, mevcut nüfus ve erişim deseni.', 'belirsiz')
    if other is not None and current > other*1.5 and current-other>=3:
        return (f'{noun.capitalize()} kayıtları {b.ilce} karşısında belirgin biçimde kümelenmiş. Bu bir ticari çekim odağı yaratabilir; aynı zamanda sıradan bir işletmenin görünür olmasını zorlaştıran rekabeti de beraberinde getirir.', 'kume')
    if other is not None and current < other*.67:
        return (f'{b.ilce} ile kıyaslandığında {noun} kümelenmesi daha sınırlı. Burası mevcut ticaretin gölgesinde büyümekten çok, konut dokusuna ve yerel ihtiyaca uyarlanmış bir modelle farklılaşma ihtimali sunuyor.', 'yerel')
    if ratio is not None and rr is not None and rr>0 and ratio<rr*.75:
        return (f'{noun.capitalize()} kayıtları nüfusa oranlandığında {b.ilce} kadar sık değil. Pazarın büyüklüğü kadar yerleşimlere doğru yayılma olasılığını değerlendirmek burada daha faydalı.', 'yayin')
    if ratio is not None and rr is not None and ratio>rr*1.3:
        return (f'Nüfus başına {noun} kümelenmesi {b.ilce} ilçesinden daha sık. Hazır bir ticari çevreye katılmak isteyen işletmeler için avantaj olabilir; markanın özgünlüğü kritik.', 'rekabet')
    return (f'{noun.capitalize()} faaliyetleri ile yerleşik nüfusun ölçeği birlikte değerlendirildiğinde, bu ilçe {b.ilce if b is not None else "diğer seçenekler"} kadar tek bir göstergenin değil farklı koşulların birleşimiyle öne çıkıyor.', 'karma')


def _commerce_scenario(sector, pop_band, transit_band, sege_band, business_type, density_band):
    """İlçe profiline göre uygulanabilir fikir; bulunmayan olayları ima etmez."""
    if sector=='Yeme-içme':
        if business_type in ('kume','rekabet') and transit_band=='yüksek':
            return 'Bu nedenle güçlü bir vitrin ve ulaşımı kolay bir noktada, belirli bir kitleye seslenen imza ürünlü kafe ya da hızlı servis konseptini önceliklendirirdim.'
        if pop_band=='yüksek' and business_type in ('yerel','yayin','belirsiz'):
            return 'Benim tercihim, yoğun konut çevrelerinde tekrar ziyaret ve paket servise yaslanan mahalle restoranı olurdu; yalnızca kalabalık caddelere odaklanmak zorunda değil.'
        if sege_band=='yüksek':
            return 'Daha seçici bir müşteri deneyimi sunan küçük ölçekli kafe veya uzmanlaşmış restoran fikri, bu gelişmişlik profiliyle birlikte değerlendirmeye değer.'
        if transit_band=='düşük':
            return 'Burada dışarıdan gelen yoğun ziyaretçiye bel bağlamak yerine çevre sakinlerini düzenli müşteriye dönüştüren mütevazı bir yeme-içme işletmesini öneririm.'
        return 'Mahalleye dönük bir kafe ile erişimi yüksek küçük formatlı bir yeme-içme işletmesini iki ayrı konum senaryosu olarak değerlendirirdim.'
    if sector=='Market / perakende':
        if pop_band=='yüksek' and density_band=='yüksek':
            return 'İlk önerim, hızlı günlük alışverişe uygun kompakt bir market veya temel ihtiyaç mağazası; amaç yakın çevreden sık ziyaret alabilecek bir yer seçmek.'
        if transit_band=='yüksek':
            return 'Toplu taşıma çevresindeki kısa ziyaretleri hedefleyen pratik ürün seçkili bir mağaza, geniş ama dağınık bir perakende alanına göre daha mantıklı olabilir.'
        if business_type in ('kume','rekabet'):
            return 'Mevcut mağazalara benzeyen bir işletme açmak yerine tek kategoride uzmanlaşan, ürün ve hizmet bütünlüğüyle ayrışan bir mağazaya öncelik verirdim.'
        return 'Konut çevresine uyumlu günlük ihtiyaç marketi veya belirli bir ürün grubuna odaklı mağaza, ilk test edeceğim iki format olurdu.'
    if sector=='Hizmetler':
        if sege_band=='yüksek' and transit_band=='yüksek':
            return 'Ben olsam randevulu uzmanlık hizmeti, eğitim desteği veya kişisel bakım gibi düzenli ziyaret gerektiren bir modeli, erişimi güçlü bir konumda denerdim.'
        if pop_band=='yüksek' and business_type in ('yerel','yayin'):
            return 'Geniş yerleşik pazar ve daha seyrek hizmet kaydı, mahalleye yakın kişisel bakım veya bakım-onarım işlerini araştırmak için uygun bir bileşim sunuyor.'
        if business_type in ('kume','rekabet'):
            return 'Hazır hizmet kümelenmesi içinde genel hizmet sunmak yerine uzmanlık, randevu disiplini ve müşteri sadakatiyle ayrışan bir işletme daha yerinde.'
        return 'İlk aşamada mahalle sakinlerinin düzenli ihtiyaçlarını karşılayan bakım, onarım veya eğitim destek hizmetlerine ağırlık verirdim.'
    # Lojistik için seyrek OSM alt kategorisini yatırım olanağı olarak okumuyoruz.
    if density_band=='düşük' and transit_band=='yüksek':
        return 'Daha seyrek yerleşim ile ulaşım kayıtları bir aradaysa küçük dağıtım merkezi senaryosu araştırılabilir; yer seçimini yol bağlantısı ve kullanılabilir parsel üzerinden yapmak gerekir.'
    if density_band=='yüksek':
        return 'Yerleşim yoğunluğu nedeniyle büyük depo yerine son kilometre dağıtımı veya küçük aktarma noktası, daha tutarlı bir başlangıç senaryosu.'
    if pop_band=='yüksek':
        return 'Geniş nüfusa yakın küçük depolama ve yerel dağıtım noktası fikrini, uzak mesafeli büyük depodan önce değerlendirirdim.'
    return 'Bu ilçede önce küçük ölçekli depolama ve dağıtım modellerini karşılaştırır; ulaşım bağlantılarıyla mevcut yerleşim dokusunu birlikte ele alırdım.'


def ticaret_yorumu(ranked, meta, factors):
    a=ranked.iloc[0]
    b=ranked.iloc[1] if len(ranked)>1 else None
    sector=meta.get('sektor','Yeme-içme')
    category, noun, col=_QUEUES[sector]
    pop=_level(_percentile(ranked.nufus,num(a,'nufus')))
    density=_level(_percentile(ranked.nufus_yogunlugu_km2,num(a,'nufus_yogunlugu_km2'))) if 'nufus_yogunlugu_km2' in ranked else 'orta'
    transit=_level(_percentile(ranked.osm_ulasim,num(a,'osm_ulasim'))) if 'osm_ulasim' in ranked else 'orta'
    sege=_level(_percentile(ranked.sege_sira,num(a,'sege_sira'),lower_better=True)) if 'sege_sira' in ranked else 'orta'
    best,weak=_factor_summary(factors,b)
    context=_scope(meta,a)
    labels={'yüksek':'geniş','orta':'orta ölçekli','düşük':'daha küçük'}
    profiles={
        ('yüksek','yüksek'):'büyük yerleşik pazar ile gelişmişlik profilinin birlikte güçlendirdiği',
        ('yüksek','orta'):'geniş nüfusu ve ölçülü gelişmişlik düzeyini birleştiren',
        ('yüksek','düşük'):'yüksek nüfusuna rağmen gelişmişlik açısından daha karmaşık bir tablo sunan',
        ('orta','yüksek'):'orta ölçekli yerleşim ile güçlü sosyoekonomik profili buluşturan',
        ('düşük','yüksek'):'küçük yerleşim ölçeğine karşın gelişmişlik yönüyle dikkat çeken',
    }
    profile=profiles.get((pop,sege), f'{labels[pop]} nüfusu ve yerleşim koşullarını birlikte değerlendirmeyi gerektiren')
    if sector=='Lojistik / depolama':
        intro=f'{a.il} / {a.ilce}, {context} lojistik ve depolama sıralamasında {profile} bir aday. Depoda belirleyici olan, yalnızca nüfus değil dağıtım ihtiyacıyla yerleşim dokusunun uyumudur.'
    else:
        intro=f'{a.il} / {a.ilce}, {context} {category} sıralamasında {profile} bir aday. Buradaki fırsatı tek bir rakama değil, pazarın ölçeğiyle işletme çevresinin etkileşimine bağlı görüyorum.'
    parts=[intro]
    if pop=='yüksek' and transit=='yüksek':
        parts.append('Büyük yerleşik talep ile güçlü durak ağı birleştiğinde hem mahalle içinden hem farklı noktalardan erişilebilen bir yer seçimi öne çıkıyor.')
    elif pop=='yüksek' and transit=='düşük':
        parts.append('Nüfus avantajı güçlü, ancak ulaşım kayıtları aynı hızda öne çıkmıyor; sokak ve mahalle seçimini yerel müşteriyi elde tutma fikri etrafında kurmak daha uygun.')
    elif pop=='düşük' and transit=='yüksek':
        parts.append('Yerleşik nüfus görece sınırlı olsa da durakların göreli yoğunluğu, erişime dayalı daha küçük ve hedefli bir iş modelini gündeme getiriyor.')
    elif density=='yüksek':
        parts.append('Yerleşim yoğunluğu, müşteriye yakın konumların değerini artırabilecek bir unsur; buna karşılık aynı alanı kullanan işletmelerin de birbirine yaklaşması beklenebilir.')
    elif density=='düşük':
        parts.append('Daha seyrek yerleşim, merkez odaklı tek bir iş yerine doğru alt bölgeyi seçmeyi önemli hâle getiriyor.')
    else:
        parts.append('Nüfusun büyüklüğü ile ilçenin yerleşim karakteri birbirini tamamlıyor; yalnızca en kalabalık noktayı aramak yerine erişim ve hizmet çeşitliliğini birlikte düşünmek gerekir.')
    business,kind=_trade_business(sector,a,b,ranked)
    if sector!='Lojistik / depolama':parts.append(business)
    else:
        if 'osm_lojistik' in ranked and num(a,'osm_lojistik') and num(a,'osm_lojistik')>0:
            parts.append('OSM üzerinde lojistik faaliyet izleri bulunması, depo konumlarını araştırmak için başlangıç sağlayabilir; asıl yer seçimi dağıtım akışına dayanmalı.')
        else:
            parts.append('Lojistikte yerleşim yoğunluğu ve erişim birlikte okunuyor; görünür depo etiketi sayısından çok hangi dağıtım modelinin bu çevreye uyduğu önemli.')
    if b is not None:
        factor_names={
            'nufus':'daha geniş bir yerleşik müşteri tabanı',
            'yogunluk':'daha yoğun bir yerleşim dokusu',
            'dusuk_yogunluk':'daha seyrek yerleşimin sunduğu alan esnekliği',
            'sege':'gelişmişlik göstergelerinin güçlü bileşimi',
            'isletme_kumesi':'sektörel işletme kümelenmesi',
            'rekabet_baskisi':'nüfusa oranlı rekabet dengesi',
            'ulasim':'ulaşım bağlantılarının göreli avantajı',
            'kira':'ilan verisine dayalı işyeri maliyeti',
        }
        if best:
            parts.append(f'{b.ilce} ile doğrudan karşılaştırmada {a.ilce} lehine farkı en çok {factor_names.get(best["anahtar"],"gösterge bileşimi")} yaratıyor; modelde ilk sıraya çıkmasını açıklayan ana ilişki bu.')
        else:
            parts.append(f'{b.ilce} ile kıyaslandığında belirleyici tek bir üstünlükten çok birkaç göstergenin aynı yönde çalışması, {a.ilce} ilçesini ilk sıraya taşıyor.')
        if weak:
            parts.append(f'Bununla birlikte {b.ilce}, {factor_names.get(weak["anahtar"],"bazı özellikler")} açısından daha güçlü; burada önerilen iş modeli bu ödünleşmeye göre seçilmeli.')
        scorecol=meta['puan_sutunu']
        if num(a,scorecol) is not None and num(b,scorecol) is not None and abs(num(a,scorecol)-num(b,scorecol))<.5:
            parts.append(f'Sıralama {b.ilce} ile başa baş; küçük bir konum tercihi bile uygulama aşamasında iki seçeneğin ağırlığını değiştirebilir.')
    else:
        parts.append('Bu kapsam tek ilçe içerdiği için yorumun ağırlığı ilçenin kendi yerleşim ve ticaret profilinde.')
    parts.append(_commerce_scenario(sector,pop,transit,sege,kind,density))
    return ' '.join(parts)


def yasam_yorumu(ranked,meta,factors):
    a=ranked.iloc[0]
    b=ranked.iloc[1] if len(ranked)>1 else None
    pref=meta.get('tercih','Dengeli')
    scope=_scope(meta,a)
    pop=_level(_percentile(ranked.nufus,num(a,'nufus')))
    density=_level(_percentile(ranked.nufus_yogunlugu_km2,num(a,'nufus_yogunlugu_km2'))) if 'nufus_yogunlugu_km2' in ranked else 'orta'
    sege=_level(_percentile(ranked.sege_sira,num(a,'sege_sira'),lower_better=True)) if 'sege_sira' in ranked else 'orta'
    transit=_level(_percentile(ranked.osm_ulasim,num(a,'osm_ulasim'))) if 'osm_ulasim' in ranked else 'orta'
    best,weak=_factor_summary(factors,b)
    prefaces={
        'Daha sakin':f'{a.il} / {a.ilce}, {scope} daha sakin bir yaşam arayanlar için ilk sırada. Bu tercih, nüfus ölçeği ve yerleşim ritminin daha dingin bir düzenle nasıl uyuştuğuna dayanıyor.',
        'Daha hareketli':f'{a.il} / {a.ilce}, {scope} hareketli yaşam için öne çıkıyor. Burada canlılığı, yerleşik nüfusun ölçeği ve erişim seçeneklerinin bir araya gelişinde aramak daha anlamlı.',
        'Dengeli':f'{a.il} / {a.ilce}, {scope} dengeli yaşam için öne çıkıyor. Ne yalnızca hareketliliği ne yalnızca sakinliği ödüllendiriyor; yerleşim ölçeğiyle diğer imkânların birlikteliğini ön plana alıyor.',
    }
    parts=[prefaces[pref]]
    if pop=='düşük' and sege=='yüksek':
        parts.append('Görece küçük yerleşim ölçeğine rağmen güçlü SEGE profili, sakinlik arayanlar için sosyal ve ekonomik olanaklardan bütünüyle uzaklaşmadan yaşama fikrini destekliyor.')
    elif pop=='yüksek' and sege=='yüksek':
        parts.append('Nüfus ölçeği yüksekken gelişmişlik sıralamasında da iyi konumda olması, çeşitlenen günlük ihtiyaçları karşılamaya dönük güçlü bir yerleşim çerçevesi oluşturuyor.')
    elif pop=='yüksek' and sege=='düşük':
        parts.append('Nüfusun büyüklüğü hareketlilik işareti verse de gelişmişlik profili aynı ölçüde güçlü değil; bu nedenle tercihin asıl dayanağı canlılık ve yerleşim ölçeği.')
    elif sege=='yüksek':
        parts.append('SEGE göstergelerinin güçlü konumu, eğitim, sağlık, istihdam ve yaşam olanaklarının birlikte ele alındığı gelişmişlik çerçevesinde ilçeye ek ağırlık kazandırıyor.')
    elif sege=='düşük':
        parts.append('Gelişmişlik göstergelerinde üst sıralarda olmaması, bu bölgeyi özellikle sakinlik ve gündelik yaşam ölçeğiyle değerlendirmeyi daha anlamlı kılıyor.')
    else:
        parts.append('Orta gelişmişlik profili ile yerleşim düzeni, aşırı bir uç yerine yaşam ritmini belirli bir düzeyde tutmaya çalışanlara hitap ediyor.')
    if transit=='yüksek' and density=='düşük':
        parts.append('Görece seyrek yerleşimle ulaşım noktalarının güçlü birlikteliği, sakin çevre ile bağlantı arayanlar açısından ilginç bir denge sunuyor.')
    elif transit=='yüksek':
        parts.append('Toplu taşıma kayıtlarının kapsam içindeki güçlü konumu, ilçeyi yalnızca ev çevresiyle değil günlük hareket imkânlarıyla da değerlendirmeyi sağlıyor.')
    elif transit=='düşük' and pref=='Daha sakin':
        parts.append('Ulaşım noktaları seyrek görünürken küçük ölçekli yerleşim düzeni ön plana çıkıyor; bu, özellikle yakın çevreyle sınırlı bir gündelik tempo arayanlara daha uygun olabilir.')
    elif transit=='düşük':
        parts.append('Ulaşım kayıtlarının düşük olması, yer seçiminde merkez ile ilçenin diğer mahalleleri arasındaki farkların önemini artırıyor.')
    elif density=='yüksek':
        parts.append('Yoğun yerleşim, gündelik ihtiyaçların daha yakın bir çevrede kümelenmesi ihtimaliyle birlikte düşünülmeli; bu hareketli yaşam arzusuna göre avantaj ya da ödünleşme olabilir.')
    else:
        parts.append('Yerleşim ölçeği ile ulaşım profili birbirini tamamlıyor; karar tek bir göstergeden değil yaşamın gündelik akışından çıkıyor.')
    if b is not None:
        reasons={'yasam_ritmi':'seçilen yaşam ritmine uyumu', 'sege':'gelişmişlik profili','ulasim':'ulaşım kayıtları'}
        if best:
            parts.append(f'{b.ilce} ile karşılaştırmada {a.ilce} için en belirgin üstünlük {reasons.get(best["anahtar"],"gösterge dengesi")}; sıralamadaki farkı yaratan ana unsur bu.')
        else:
            parts.append(f'{b.ilce} ile çok yakın bir profil görülüyor; {a.ilce} küçük gösterge farklarının toplamıyla ilk sırada kalıyor.')
        if weak:
            parts.append(f'Öte yandan {b.ilce} {reasons.get(weak["anahtar"],"bazı göstergeler")} yönünden daha iyi; bu yüzden iki ilçe farklı öncelikleri olan kişiler için çekici olabilir.')
        if abs(num(a,'Tercih uyumu')-num(b,'Tercih uyumu'))<.05:
            parts.append(f'{b.ilce} ile yakın bir profil oluşuyor; ikisi arasında seçimde hangi yaşam ritmine öncelik verildiği belirleyici olur.')
    else:
        parts.append('Bu karşılaştırmada yalnızca tek ilçe var; değerlendirmenin odağı ilçenin yerleşim profilidir.')
    if pref=='Daha sakin':
        advice=('Benim önerim, dingin bir gündelik düzen isteyenlerin bu ilçeyi öncelikli yerleşim seçeneği olarak incelemesi.' if sege=='yüksek' else
                'Benim önerim, sakinlik öncelikliysen bu ilçeyi ilk seçeneklere alıp yerleşim ritmi ile ulaşım beklentini birlikte düşünmen.')
    elif pref=='Daha hareketli':
        advice=('Benim önerim, sosyal ve gündelik hareketlilik arayanların ulaşım ağına yakın mahalleleri öncelikle karşılaştırması.' if transit=='yüksek' else
                'Benim önerim, hareketli hayat beklentisine uygun merkezleri ve gündelik yolculuk düzenini birlikte değerlendirmen.')
    else:
        advice=('Benim önerim, hem gelişmişlik hem gündelik erişim istiyorsan ilçenin farklı mahallelerinde bu dengeyi araman.' if sege=='yüksek' and transit=='yüksek' else
                'Benim önerim, ev çevresinde sakinlik ile günlük ihtiyaçlara erişim arasında kendi dengenin hangi mahallede oluştuğunu araştırman.')
    parts.append(advice)
    return ' '.join(parts)


def yorum_uret(ranked: pd.DataFrame, meta: dict, factors: list[dict]) -> str:
    if ranked.empty:return ''
    if meta.get('mod')=='ticaret':return ticaret_yorumu(ranked,meta,factors)
    if meta.get('mod')=='yasam':return yasam_yorumu(ranked,meta,factors)
    raise ValueError('Yorum modu tanınmıyor')
