# AFET ATLAS v2.6 — Siz Sorun

BBY261 İleri Programlama – **Afet Atlas: Türkiye Doğal Afet Analiz Platformu**.

Bu sürümde **gerçek Google Agent Development Kit (ADK)** entegre edildi. Önceki `Gemini API` SDK çağrısı yerine ADK `Agent`, `App`, `Runner`, `InMemorySessionService` ve **6 Python aracı** kullanılıyor. **Harita, gerçek deprem verileri, 1-3-5-7 puanlama, 0/50/75/100/150 km filtreleri ve il eşleştirmeleri değiştirilmedi.**

## 1. VS Code'da çalıştırma (Windows PowerShell)

ZIP'i ayıkla, `app.py` içeren klasörü aç ve terminale şunları sırayla yaz:

```powershell
python -m pip install -r requirements.txt
```

Google AI Studio üzerinden https://aistudio.google.com/apikey adresinde bir API anahtarı oluştur. **Anahtarı başkalarıyla paylaşma; GitHub'a ekleme.** PowerShell terminalinde yalnızca kendi cihazında:

```powershell
$env:GOOGLE_API_KEY = "BURAYA_KENDI_ANAHTARIN"
$env:GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
python -m streamlit run app.py
```

Tarayıcıda terminalin yazdığı `http://localhost:8501` adresini aç. **Siz Sorun** sekmesinde "Ankara ile İstanbul'un deprem hareketliliğini karşılaştır" sorusunu dene. Çalıştırdığın aynı PowerShell penceresinde API anahtarı kayıtlı kalır; terminali kapatırsan yeni terminalde yeniden tanımlaman gerekir. Ödemeler/kotalar Google hesabındaki API ayarlarına bağlıdır.

### Alternatif API anahtarı (dosyaya yazmak istersen)

Yerel `.streamlit/secrets.toml` dosyasına `GOOGLE_API_KEY = "..."` ekleyebilirsin; bu dosya `.gitignore` kapsamındadır. `.env.example` yalnızca örnek biçimi gösterir; anahtar içermez.

## 2. Hocaya gerçek ADK'yi ayrı göstermek

Aynı proje klasöründe, yukarıdaki API anahtarı tanımlanmış terminalden:

```powershell
adk web .
```

Komut çıktı olarak `localhost:8000` adresini gösterebilir. Açılan ADK geliştirici ekranında `afet_atlas_adk` ajanını seç. Bu ajan ZIP'e dahil olan **2025 / M >= 4.5 / 0 km** gerçek test verileriyle çalışır. Burada ADK'nin araç çağrılarını ve ajan adımlarını inceleyebilirsin. Geliştirici arayüzü üretim ortamı için değildir. **Streamlit ekranındaki tarih/mesafe filtreleri ise Streamlit'in kendi ADK ajanına aktarılır; iki arayüz bağımsızdır.**

### ADK dosyaları

- `afet_atlas_adk/agent.py`: ADK `root_agent`, ajan talimatları, model ve dinamik ajan yapısı.
- `afet_atlas_adk/veri_araclari.py`: Ajanın erişebildiği 6 salt okunur veri aracı.
- `afet_atlas_adk/calistir.py`: Streamlit üzerinden ADK `App` ve `Runner` ile çalışma.
- `app.py`: yeni ADK sekmesi, soru arayüzü (anahtarın başarı bildirimi kullanıcıdan gizlendi).

**Ajanın araçları:** `il_ozeti`, `il_karsilastir`, `hareketliligi_en_yuksek_iller`, `hareketliligi_en_dusuk_kayitli_iller`, `veri_kapsami`, `ilin_en_buyuk_depremleri`.

ADK model varsayılanı `gemini-flash-latest`. İstersen `.env`/ortam ayarı `AFET_ATLAS_MODEL` ile Google hesabında erişimin bulunan başka bir modeli seçebilirsin.

## 3. Doğrulama

```powershell
python -m unittest test_adk_araclari.py -v
python test_hesaplama.py
```

API anahtarı olmadan ilk test ADK'nin kullanacağı Python araçlarını **gerçek 2025 USGS** verisiyle doğrular. İkinci test deprem hesaplamasını doğrular. Bunlar Gemini modelinin dış serviste canlı olarak yanıt verdiğini kanıtlamaz; bunun için Google API anahtarıyla uygulamada gerçek bir sorgu yapman gerekir.

## 4. Bilimsel ve güvenlik sınırları

- USGS olay ve geoBoundaries il sınırları gerçek veri. Önceki CSV ve hesaplama kodu korunur.
- Deprem hareketliliği puanları afet riski olasılığı veya güvenlik yüzdesi değildir.
- `0 km` seçilince denizde/komşu ilde bulunan depremler il içine dahil edilmez. 50/75/100/150 km farklı eşleşmeler verir.
- ADK bir dil modeli kullandığından, cevapları her zaman veri tablosundaki olay kimlikleri ve sayılarla kontrol et.
- Yerel Streamlit entegrasyonu her soruya kısa ömürlü **yeni bir ADK oturumu** açar; çok turlu konuşma belleği henüz eklenmedi. ADK geliştirici arayüzü konuşmayı sürdürebilir.
- API anahtarı ve internet olmadan ADK cevap üretemez, ancak diğer ekranlar çalışır.
- İleride farklı afetlere (orman yangını, sel, heyelan) yeni araçlar ve bağımsız ajanlar eklenebilir.

## Referanslar

- https://adk.dev/get-started/python/
- https://adk.dev/agents/models/google-gemini/
- https://earthquake.usgs.gov/earthquakes/search/
- https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/

## 5. v2.5 — Harita ve ADK doğrulama düzenlemesi

**Harita düzeltmesi:** `Genel görünüm` haritası artık `go.Choropleth`/Plotly Geo çizimine bağlı değil. `harita_cizimi.py`, gerçek il GeoJSON sınırlarını kendi Plotly vektör çizgilerine dönüştürür; **haritanın gösterimi için dış harita/harita döşemesi servisi gerekmez.** İl–deprem eşleştirmesi, 1/3/5/7 puanlama ve beş yakınlık ayarı değiştirilmedi.

**ADK izleme:** Ajanın hangi Python fonksiyonlarını hangi argümanlarla çağırdığını görmek için `Siz Sorun` sekmesinde bir soru sor; yanıtın altındaki **ADK işlem geçmişi** kısmını aç. `ADK_TEST_PLANI.md` dosyasında örnek sorular ve beklenen sonuçlar yer alır.

Yerel bağımsız testler (API anahtarsız):

```powershell
python -m unittest test_harita.py test_adk_araclari.py -v
python test_hesaplama.py
```

**Not:** Harita geometri üretimi gerçek GeoJSON ile test edilmiştir. Tarayıcıda kullanıcıya görünen son çizim ve canlı Gemini yanıtı, API/Streamlit çalışma ortamına bağlı olduğundan burada uçtan uca doğrulanmış değildir.

## 6. v2.6 — Arayüz metinleri

- ADK sekmesi ve bölüm başlığı **Siz Sorun** olarak değiştirildi.
- Soru alanı **Sorunuz**, gönderme düğmesi **Soruyu gönder** oldu.
- Anahtar varsa görünen yeşil **API anahtarı yapılandırıldı** bildirimi kaldırıldı. Anahtar yoksa gerekli uyarı görünmeye devam eder; bağlantı veya hesaplama koduna dokunulmadı.
