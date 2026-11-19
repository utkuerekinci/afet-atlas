> **v3.8 notu:** Bu ZIP paketinde işlenmiş 973 ilçe OSM CSV ve manifest zaten var; PBF indirme ve işleme adımlarını tekrar yapman gerekmiyor. Bu rehber yalnızca gelecekte yeni OSM verisi hazırlamak içindir.

# Afet Atlas v3.7 — ticari analiz modülü

**Uygulandı:** v3.6 Streamlit uygulaması, mevcut deprem/orman yangını/MGM katmanları ve Google ADK ajanı korunarak ticaret analiz motoruna OSM katmanını kullanabilen doğrulayıcı, sektör ağırlıkları, rekabet baskısı ve ilçe açıklaması eklendi. Mevcut 2025 nüfus ve 2022 SEGE veri dosyaları değiştirilmedi.

## 1. Önce mevcut ZIP'i açıp uygulamayı başlat

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**İlk açılışta işletme ve ulaşım sayıları gösterilmez:** Bu pakette OSM 623 MB ham kesitinin işlenmiş 973 ilçelik sayım dosyası bulunmuyor. Verilerin yokluğunda sistem nüfus + yoğunluk + SEGE temel analizini kullanır, OSM olmayan ilçelere rakip sayısı sıfır atamaz. Uydurma veri içermez.

## 2. Türkiye'nin 973 ilçesi için gerçek OSM işletme ve durak sayılarını yükleme

Bu işlem **bir kez geliştirici bilgisayarında**, internet üzerinden yapılır; Streamlit sunucusu her açılışta büyük dosyayı indirmeye çalışmaz.

1. `https://download.geofabrik.de/europe/turkey.html` adresinden `turkey-latest.osm.pbf` dosyasını indir. İndirme boyutu Kasım 2026'da yaklaşık **623 MB**. OSM verisi bir işletme sicili değildir. 
2. `https://rodostoteknoloji.com/online-tools/turkey-boundaries.html` sitesinden **973 ilçe** sınırlarını GeoJSON olarak indir. Dosyayı `ilce_sinir_osm.geojson` adıyla proje dizinine koy.
3. İki indirilen dosyayı proje klasörüne koy. `python -m pip install -r requirements-osm.txt` komutunu çalıştır.
4. Ardından proje klasörünün terminalinde:

```powershell
python ticaret_osm_hazirla.py --pbf turkey-latest.osm.pbf --geojson ilce_sinir_osm.geojson
```

Bu komut `indirilen_veriler/ticaret_osm_ilce.csv` ve `indirilen_veriler/ticaret_osm_manifest.json` üretir. 973 tekil ilçe, nüfus eşleşmesi ve 81 ilde en az bir kayıt kontrolü geçmeden çıktı oluşturmaz. OSM kayıtları gerçek OSM ögeleridir ancak **tüm faal işletmeleri veya benzersiz rakipleri saydığı iddia edilmez**. Tek bir işletme birden fazla OSM öğesinde veya kategoride kayıtlı olabilir. Toplu taşıma öğeleri gerçekte sayılan yolcu/yaya değildir. OSM'de 0 kayıt bir ilçede gerçekten 0 işletme olduğu anlamına gelmez.

Sadece üretilen **iki küçük özet dosyayı** GitHub'a/Vercel'e koy. 623 MB PBF ve büyük GeoJSON dosyasını yükleme. Canlı sitede yeni dosyalarla yeniden dağıtım yapılması gerekir.

## 3. Kiralık işyeri m² verisi (opsiyonel)

Tapusor'un API'sinde işyeri (`category=2`) ve kiralık (`status=2`) türleri vardır. Ancak proje için API anahtarı, ücret/kredi, ilan örneklemi, kaynak koşulları ve kullanım izni **doğrulanmadı**. Bunlar olmadan Tapusor'dan fiyat çekildiği iddia edilmez. Yetkili, kaynağı belgelenmiş ilçe medyan kira verisi alınırsa `ticaret_kira_sablon.csv` sütunlarına göre `indirilen_veriler/ticaret_kira_ilce.csv` oluştur.

Şema: `il,ilce,kira_m2_tl,kaynak,tarih,ilan_adedi` (örnek fiyat satırı verilmedi). Fiyat **TL/m²/ay** cinsinden medyan *ilan* bedeli olarak kaydedilmeli. `ilan_adedi` o ilçedeki ilgili kiralık işyeri örneklemini göstermeli. Hem kaynak adı hem çekim tarihi zorunludur. Kısmi kira verisi yalnız **ayrı yerel analiz** tablosunda gösterilir; ulusal sıralamaya katılmaz. Ulusal endeks için 973 ilçenin tamamında en az beş ilanlı kayıt koşulu eklenmiştir. Kira bilgisi kesin sözleşme bedeli değildir.

## 4. Puanlama mantığı

Dört sektörün önceden belirlenmiş ağırlıkları `bolge_puanlari.py` içindeki `SEKTOR_AGIRLIKLARI` sözlüğündedir. Gösterge eksikse onun ağırlığı kalanlara yeniden paylaştırılır. Kullanılanlar: nüfus, nüfus yoğunluğu veya düşük yoğunluk, SEGE sırası, OSM sektörel kümelenme (log sayım sırası), 50 bin nüfus tabanıyla yumuşatılmış nüfusa göre rakip yoğunluğunun tersi, OSM durak/istasyon sayımı, tam ülke kira medyanı (varsa). Lojistik için durak sayısı yol/liman erişimi kabul edilmez ve kullanılmaz. Bunlar kalibre edilmiş ekonomik olasılık ya da getiri ölçüleri değildir.

Ülke geneli ile il içi karşılaştırmada **normalizasyon evreni farklıdır**. İl içindeki 80 puan, ulusal 80 puanla aynı anlamda değildir.

"**Neden Bu İlçe Birinci?**" açıklaması seçilen sektör ve kapsam için gerçek gösterge sütunlarına, ilk iki ilçenin puan farkına, OSM kayıtlarına, nüfusa ve SEGE'ye göre değişir. Uygulama ve ADK aracı aynı Python fonksiyonunu kullanır.

## 5. Veri kaynaklarının rolü

- [OpenStreetMap / Geofabrik](https://download.geofabrik.de/europe/turkey.html): gerçek etiketli işletme ve ulaşım kaydı; eksik ve bölgeler arasında farklı temsil olabilir.
- [Alternatif ilçe sınırları](https://rodostoteknoloji.com/online-tools/turkey-boundaries.html): 973 ilçe poligonu, resmî kadastro değil.
- [TÜİK nüfusu / Topografya aktarımı](https://github.com/topografya/veri): pakette 2025 nüfus kaydı hazır.
- [Resmî İlçe SEGE 2022 raporu](https://www.sanayi.gov.tr/assets/pdf/birimler/2022-ilce-sege.pdf): pakette 973/973 doğrulanmış aktarım.
- [Tapusor API](https://www.ai.tapusor.com/public/api/): ancak erişim sağlandığında kısmi/gelişmiş ticari kira analizi için aday.
- [Google Places Insights](https://developers.google.com/maps/documentation/placesinsights/reference/supported-locations): Türkiye BigQuery veri seti mevcuttur; şu anda Afet Atlas'a entegre edilmedi ve ücretsiz sınırsız veri varsayılmadı.

**Lisans:** © OpenStreetMap katkıcıları — Open Database License (ODbL 1.0). OSM kaynaklı türetilmiş veri kullanılırken atıf ve türetilmiş veri paylaşım yükümlülüklerine uy. Bu dosyalarla paylaşım yapmadan önce ODbL şartlarını incele.

## 6. Kontroller

```powershell
python -m unittest discover -v
```

`test_ticaret_osm_v37.py` sentetik test kayıtlarında geometri ataması, kapsam eksikliği ve ağırlıklarla açıklamanın tutarlılığını sınar. Testlerdeki sentetik sayılar yayımlanan 973 ilçe verilerine karıştırılmaz.

## Mevcut durum ve bilinçli olarak yapılmayanlar

**Kod entegrasyonu tamamlandı.** Büyük OSM kaynağı bu çalışma ortamından indirilemediği için Türkiye geneli gerçek işletme/durak sayımlarının canlı kaydı henüz **üretilmiş değil**. Geofabrik dosyasını kişisel bilgisayarında işleyip iki küçük çıktı dosyasını projeye koyman gerekiyor. Tapusor API'sine erişim anahtarı bulunmadığından gerçek ticari kiralar da **yüklenmedi**. Yaya trafiği, günlük müşteri sayısı, ciro, kira sözleşmesi, otomobil/lojistik yol erişimi ayrıca ölçülmüyor.
