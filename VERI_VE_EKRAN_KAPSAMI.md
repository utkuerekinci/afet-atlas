> **v3.5.4 güncellemesi:** Önceki sürümlerdeki nüfus–SEGE eşleşme eksikliği çözüldü. 973/973 ilçe ve 81 il tam eşleşiyor. Paket gerçek nüfus, SEGE ve birleşik CSV dosyalarını içeriyor. Ayrıntılar için `ESLESME_DUZELTMESI.md` belgesine bakın. Aşağıdaki eski sürüm notları tarihsel bilgi olarak korunmuştur.

# Afet Atlas v3.4 — onaylanan veri ve ekran kapsamı

## Mimari kararları

- **Tek ortak il haritası:** `atlas_harita.py` ile bütün analiz bölümlerinde Türkiye'nin 81 il poligonu; ekrandaki katmana göre renk/değer değişimi. İl seçimi `st.session_state['secilen_il']` ile paylaşılır. **Haritada il işaretçisine tıklanabilir.**
- **Afetler il düzeyinde:** Deprem, orman yangını, sel/taşkın, heyelan, çığ, fırtına, kuraklık hedef listesi. Erozyon kapsam dışıdır. Bu sürümde sayısal entegrasyonu doğrulanmış afet **yalnızca depremdir**.
- **Yaşam ve ticaret ilçe düzeyinde:** Türkiye genelinde 973 ilçe hedefi, ayrıca seçilen il içindeki karşılaştırmalar. Verilerin geldiği yıl ve kapsam açıkça gösterilir.
- **Sektörler:** Yeme-içme, market/perakende, hizmetler ve lojistik/depolama. Nüfus ve yoğunluk tabanlı puanlar gerçek kârlılık/rekabet/gelir ölçümü yerine geçmez.
- **“Neden Bu İlçe Birinci?”** hem ulusal hem il içi karşılaştırmada birinci/ikinci puan farkı, kullanılan gösterge ağırlıkları, mevcut katkı puanları ve en önemli fark etkeni ile açıklanır.
- **Google ADK + Gemini:** 13 deprem + 3 veri kapsam/metodoloji aracı koşulsuz; doğrulanmış ilçe nüfusu yüklenirse 13 bölgesel araç daha etkinleşir. Ayrı bir ikinci yapay zekâ modeli yoktur.

## Gerçek veri kapsamı

| Veri alanı | Kaynak | Dönem | Bu ZIP'in içinde mi? | Uygulama durumu |
|---|---|---|---|---|
| Deprem | USGS ComCat | 2025 örnek kayıtları | **Evet:** 159 deprem | 81 il için yeniden hesaplanır |
| İl sınırı | geoBoundaries TUR ADM1 | kullanılan sürüm | **Evet:** 81 il GeoJSON | Ortak haritada çalışır |
| İlçe nüfusu | turkiyeharitasi.site; esas kaynak TÜİK ADNKS | 2025 | Hayır; uygulama çevrim içi indirir | 973 kayıt / 81 il / Türkiye toplamı 86.092.168 kontrolü |
| İlçe yoğunluğu | 2025 nüfus kaynağında sınır alanından türetilmiş | 2025 | Hayır | Varsa modelde kullanılır |
| İlçe SEGE | Sanayi ve Teknoloji Bakanlığı | 2022 | **Evet, 973/973 PDF çapraz doğrulandı** | Uygulama için CSV dahil; yerel nüfusla isim eşleşmesi ayrıca kontrol edilir |
| İşletme konum ve sayıları | Henüz entegre edilmedi | — | Hayır | Kesin işletme sayısı, ciro veya yaya akışı gösterilmez |
| Diğer altı afet | OGM, MGM, AFAD ve diğer resmî kaynaklar | Kaynağa göre | Hayır | Kaynak araştırması sürüyor, haritada puan üretilmez |

## Ekranların işlevi

1. **Genel Bakış:** Gerçek 2025 USGS verisinden il haritası, il seçimi ve modüllere giriş.
2. **Afet Analizi:** 0/50/75/100/150 km, M4.5/M5+, yıl filtreleri, 81 il puanları, il kayıtları. Diğer afet seçenekleri etkin sonuç diye gösterilmez.
3. **Yaşam Kalitesi:** 81 il için nüfus veya ilçe sayısı harita katmanı; Türkiye geneli ve seçilen il içinde yaşam tercihi puanı sıralaması, birincilik açıklaması. SEGE tablosu doğrulanırsa eklenir.
4. **Ticari Potansiyel:** Aynı haritada nüfus/ilçe sayısı katmanları; sektör seçimi, Türkiye geneli ve il içi fırsat ön puanı sıralamaları, ilk sıradaki ilçenin nedenleri ve ağırlıklar.
5. **Siz Sorun:** ADK Runner; araç çağrısı geçmişi. Deprem ve mevcutsa nüfus/ilçe/sıralama araçları.
6. **Veri ve Yöntem:** Kaynaklar, kapsam, model ağırlıkları, göstergelerin ne anlama geldiği.

### Kritik metodoloji ayrımı

- 0–100 puan **olasılık, resmî güvenlik derecesi veya beklenen işletme kazancı** değildir.
- Ulusal sıralama ve il içi sıralama farklı karşılaştırma evrenlerinde normalize edilir; puanları doğrudan birbirine eşitlemeyin.
- Eksik gösterge 0 olarak eklenmez; kalan model ağırlıkları yeniden ölçeklenir. İstendiğinde kullanılan ağırlıklar açıklama panelinde görünür.
- Gerçek veri kaynağı indirilmezse uygulama hayalî ilçe istatistikleriyle devam etmez.

## Canlı bağlantı kontrol listesi

- Streamlit'te Yaşam Kalitesi ekranının 81 il ve nüfus katmanını çizdiğini doğrula.
- Haritadaki Ankara işaretçisine tıkla; seçilen il değeri ve ilçe sıralaması değişmeli. Sonra Ticari Potansiyel'e geç; Ankara seçimi korunmalı.
- Kafe yerine Lojistik seçildiğinde ağırlık ve puan sıralamasının değiştiğini kontrol et. Yoğunluk verisi yoksa sonuç yalnızca nüfusa dayanabilir.
- Türkiye geneli ve il içi en yüksek 10 listeye bak. Birincilik açıklamasındaki ağırlıkların %100 ettiğini ve katkı toplamlarının nihai puanla uyumlu olduğunu denetle.
- Google ADK'ye 'Ankara'da yeme-içme için neden bu ilçe birinci?' sor; `neden_bu_ilce_birinci` çağrısı olup olmadığına bak.
- Kayıt bulunmadığında veya bağlantı başarısızsa gerçek veri varmış gibi yüzde oluşmamalı.

**Bu ortamda dış veri kaynaklarının canlı indirilmesi, Streamlit tarayıcı çizimi ve Google Gemini canlı yanıtı uçtan uca doğrulanamadı.** Bunlar yayımlamadan önce bilgisayarında kontrol edilecek.
