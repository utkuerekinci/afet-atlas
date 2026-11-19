## v4.0 — Genel Bakış yenilendi

Ana sayfada deprem paneli yerine üç mercekli ortak harita bulunur: **Yaşam ve nüfus**, **Ticari hareketlilik**, **Doğal afetler**. Nüfus/SEGE, OSM işletme-ulaşım ve orman yangını katmanlarını seçebilir, il seçip dinamik açıklamaları okuyabilirsin. Giriş metni ve özet kartları yenilendi. **Analiz Alanları** kartları korundu. Detaylı değişiklikler `V40_GENEL_BAKIS.md` dosyasında.

# Afet Atlas v3.9 — Yorum Odaklı Analiz

Önce [V39_DEGISIKLIKLER.md](V39_DEGISIKLIKLER.md) dosyasını okuyun. Türkiye geneli ve il içi ticaret/yaşam yorumları geliştirildi.

---

# Afet Atlas v3.8 — Türkiye geneli ticari OSM verileri entegre

Bu ZIP v3.6 afet katmanlarını korurken ticari potansiyel için **OSM işletme kümelenmesi, nüfusa göre rekabet baskısı, toplu taşıma kayıtları ve opsiyonel kira verisi** entegrasyonunu ekler. Akışın nasıl açılacağı ve eksik olan büyük kaynak dosyalarının nasıl hazırlanacağı için [TICARET_V37_KURULUM.md](TICARET_V37_KURULUM.md) belgesini oku.

**Veri durumu:** 2025 nüfus + SEGE-2022, 973 ilçede hazırdır. OSM işletme/ulaşım özet sayıları için geliştirici bir defa Geofabrik 623 MB PBF dosyasını işleyip `ticaret_osm_ilce.csv` + manifesti üretmelidir. Üretilmediği sürece mevcut nüfus/SEGE tabanlı ticari puanlama çalışır, OSM göstergeleri gösterilmez. Ücretli Tapusor kiraları gerçek veri olmadan kullanılmaz. Uydurma müşteri, kira veya yaya sayısı yoktur.

Çalıştırma: `python -m pip install -r requirements.txt`, sonra `python -m streamlit run app.py`. Test: `python -m unittest discover -v`.

---

# Afet Atlas v3.6 — Altı yeni afet katmanı (2024/2025)

Bu sürümde önceki deprem, SEGE-2022, TÜİK ADNKS 2025, yaşam kalitesi, ticaret ve Google ADK modülleri korunmuş; **Afet Analizi** içindeki altı bekleme ekranı gerçek kaynaklı inceleme ekranlarına dönüştürülmüştür. 81 il haritası her afet sekmesinde kullanılabilir. **Ancak altı afetin tamamında 81 ilin kesin olay sayısına ulaşılmış değildir.** Veri kanıtının izin verdiği analiz türü farklıdır.

| Afet | Aktif yıl | Ekranda gösterilen | Kaynak kesinliği |
|---|---|---|---|
| Deprem | 2025 varsayılan; USGS seçilebilir tarih | Olay sayısı, puan, harita, ADK | USGS gerçek olay CSV |
| Orman yangını | 2024, 2025 | 2025'te 81 il sayısı; 2024'te 77 il sayısı; yanan alan, ilk 10, il haritası | **İkincil aktarım**, ulusal OGM toplamı kontrol edildi; resmî Excel satır karşılaştırması yapılmadı |
| Sel / taşkın | 2024 | MGM ulusal 434 olay; raporda adı belirtilen 8 il, harita | Resmî rapor metni; tüm iller için kesin il sayıları **yok** |
| Heyelan | 2024 | MGM ulusal 42 olay; adı belirtilen 10 il, harita | Resmî rapor metni; tüm iller için kesin il sayıları **yok** |
| Çığ | 2024 | MGM ulusal 17 olay; Van 6–8 ve raporda belirtilen diğer iller 1–2 sınıfı | Resmî rapor harita sınıfları; kesin sayıya dönüştürülmez |
| Fırtına | 2024 | MGM ulusal 257 olay; metinde öne çıkan 5 il, harita | Resmî rapor metni; tüm iller için kesin il sayıları **yok** |
| Kuraklık | 2024 | 7 coğrafi bölgenin yıllık yağış sapması ve bunların 81 ile haritada yansıtılması | **Bölgesel yağış anomalisi**; il düzeyi SPI ya da afet sayısı değildir |

## Çalıştırma

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Sol menüden **Afet Analizi → Afet türü** seç, sağ taraftaki il haritasından ili seç. Yangın için ayrıca 2024/2025 ve yangın sayısı/yanan alan filtresi açılır. Diğer beş modülde MGM 2024 raporu kapsamıyla çalışılır. Bütün ekranlarda veri tablosu CSV indirilebilir.

## Kaynaklar

- OGM 2024 il verilerinin resmî adresi: https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2053
- OGM 2025 il verilerinin resmî adresi: https://istatistik.tarimorman.gov.tr/Sayfa/Detay/2364
- MGM 2024 meteorolojik afet raporu: https://www.mgm.gov.tr/FILES/genel/raporlar/2024%20MetAfet%20Degerlendirme%20Raporu_V1.pdf
- MGM 2024 iklim raporu: https://mgm.gov.tr/FILES/iklim/yillikiklim/2024-iklim-raporu.pdf

## Veri kanıtı ve puanlama

- Yangın sayısı ve yanan alan, kaynak tabloya dayalı sayısal ölçümlerdir; orijinal OGM Excel ile doğrulama bekler. 2024'te eksik hücreler `NaN`, yani **bilinmiyor** olarak kalır. 2025 toplamı 3.224; 2024 toplamı 3.797'dir.
- Diğer meteorolojik afetlerde `Rapor vurgusu=1/2` yalnızca kaynak metinde adı geçen/öne çıkan iller için **görsel gösterim kodudur**, olay sayısı veya risk puanı değildir. Raporda adı geçmeyen illere sıfır atanmamıştır.
- Çığ için rapordaki sayısal aralıkları (`6–8`, `1–2`) **kesin bir sayı** ile değiştirmedik.
- Kuraklık katmanında gösterilen yağış sapması **7 bölge** ölçümüdür. Coğrafi olarak aynı bölgedeki her il aynı değeri alır; il için özgün kuraklık verisi veya SPI değildir.
- Bu göstergeler tek bir sahte “% güvenlik” endeksinde birleştirilmez.
- ADK'ye `afet_ulusal_ozet`, `afet_il_detayi`, `afet_illeri_sirala`, `afet_veri_kaynagi` olmak üzere dört yeni araç eklendi; bunlar kaynak kısıtlarını da döndürür.
- Önceki `docs/screenshots` klasörü korunmuştur. İlk/son ekran görüntülerini o dizine yerleştirip README'ye bağlayabilirsiniz.

## Testler

```powershell
python -m unittest discover -v
```

Yeni afet testleri `test_diger_afet_katmanlari.py` içinde. Yerel otomatik testler gerçek Gemini servisine bağlanmaz; API yanıtı ve harita tıklaması tarayıcıda ayrıca sınanmalıdır.

---

## Önceki sürümün dokümantasyonu

# AFET ATLAS · Türkiye Bölgesel Analiz ve Karar Destek Platformu

**BBY261 İleri Programlama · Python / Streamlit / Google Agent Development Kit**  
**Sürüm: v3.5.4 — 973 ilçe nüfusu ve SEGE tam eşleşti; çok amaçlı ADK**

Afet Atlas, Türkiye'deki **81 ili** harita üzerinden keşfedip doğal afet hareketliliğini, ilçe nüfusunu ve projede tanımlanmış bölgesel değerlendirme modellerini karşılaştırmak için geliştirilen öğrenci projesidir.

## Kurulum ve çalıştırma

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Tarayıcıda terminalin gösterdiği yerel adresi aç. Google ADK'nin internetteki modeline erişmek için Google AI Studio anahtarını **ortam değişkenine** veya **Streamlit Secrets** bölümüne ekle; GitHub'a gönderme:

```toml
GOOGLE_API_KEY = "SENIN_GERCEK_ANAHTARIN"
GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
AFET_ATLAS_MODEL = "gemini-3.5-flash-lite"
```

Model adı hesabının erişimi ve mevcut Google model seçenekleriyle uyumlu olmalı. Harita ve Python analizleri API anahtarı olmadan da çalışır.

## Uygulama bölümleri

| Bölüm | Etkileşim | Veri kapsamı |
|---|---|---|
| Genel Bakış | Ortak haritadan il seçimi, genel kayıtlar | Gerçek USGS 2025 verisi, 81 il |
| Afet Analizi | Deprem katmanı, yıl / M / 0–150 km seçenekleri, il sıralaması | Deprem hazır; diğer altı afet verisi henüz eklenmedi |
| Yaşam Kalitesi | Haritada nüfus ve SEGE, ulusal/il içi sıralamalar | 2025 nüfus + 2022 SEGE 973/973 eşleşmiş olarak pakette |
| Ticari Potansiyel | Sektör seçimi, nüfus katmanı, ilçe sıralaması | Nüfus, yoğunluk ve gerçek SEGE dahil; sektör işletme sayıları henüz yok |
| Neden Bu İlçe Birinci? | İkinci ile puan farkı, katkı/ağırlıklar | Hem ulusal hem il içi, ticarette sektöre göre |
| Siz Sorun | Gemini + Google ADK araçlarının çalışması ve izleri | 13 deprem + 3 kaynak/metodoloji + nüfus varsa 13 bölgesel araç |
| Veri ve Yöntem | Açık kaynak ve puanlama anlatımı | Verinin türü ve yılı açıklanır |

**Nüfus kaynağı düzeltildi:** `topografya/veri/yayin/nufus/gostergeler.json` kullanılıyor. Eski CSV 11.441 kişi eksik toplama neden oluyordu. [Düzeltme notları](HATA_DUZELTME_NOTLARI.md).

**2025 nüfus + SEGE-2022 veri entegrasyonu tamamlandı:** Paket içinde gerçek `ilce_nufus_2025.csv` ve resmî PDF'nin Ek-1 ile Ek-2 tablolarından doğrulanmış `ilce_sege_2022.csv` bulunuyor. Yüklenen nüfus CSV'sindeki 100 il adı önek farkı ve Samsun'daki `19 Mayıs / Ondokuzmayıs` ad farkı, aynı il içinde tekil biçimde eşleştirildi: **973/973 ilçe, 81/81 il, 86.092.168 kişi**. `python kontrol_sege_nufus.py` hazır birleştirilmiş tabloyu ve denetim dosyasını yeniden üretir. `ESLESME_DUZELTMESI.md` ayrıntıları içerir. 2022 SEGE, 2025 yaşam kalitesinin resmî ölçümü değildir. Deprem dışındaki altı afetin sayısal entegrasyonu hâlâ eksik.

**Endekslerimiz resmî güvenlik veya gerçek işletme kazancı yüzdesi değildir.** Ticaret modelleri veri bulunduğu ölçüde çalışan, açıkça tanımlanmış ağırlıklı göreli sıralamalardır. Eksik göstergelere 0 puan yazılmaz. Ayrıntılar: [VERI_VE_EKRAN_KAPSAMI.md](VERI_VE_EKRAN_KAPSAMI.md).

## Yeni: Çok yönlü ADK araçları

ADK'ye 13 deprem aracı eklendi: il özetleri/karşılaştırmaları, esnek il sıralaması,
aylık/yıllık olaylar, büyüklük grupları, olay filtreleme, puan gerekçesi ve
ülke genelinde en büyük kayıtlar. Paketli doğrulanmış ilçe nüfusu sayesinde
13 ayrı il/ilçe/yaşam/ticaret aracı da açılır. İlçe verisi bulunmasa bile
3 genel kapsam/metodoloji aracı kullanılabilir.

**Dışarıdan ikinci yapay zekâ eklenmedi.** Google ADK + Gemini mevcut Python
veri araçlarının sonuçlarını yorumluyor; yorum tek başına istatistik üretmiyor.

## Yeni: Eksik veri toplama komutu

Gerçek dosyaları indirme/dönüştürme denemeleri ve doğrulama koşullarının ayrıntıları:
[VERI_TOPLAMA_DURUMU.md](VERI_TOPLAMA_DURUMU.md).

```powershell
python kaynaklari_topla.py --hepsi
```

Bu komut uygulamanın ziyaretçilerine değil, geliştiriciye aittir. Nüfus ve SEGE dosyaları artık pakete eklenmiş ve 973/973 eşleştirilmiştir; bu ikisi için indirme komutu çalıştırman gerekmez. `python kontrol_sege_nufus.py` doğrulamayı tekrarlar. 2024/2025 orman yangını XLSX sayfaları
**ham CSV** olarak çıkarılır; il sayısal değerleri kontrol edilmeden haritaya
aktarılmaz. Bu ortamdan canlı dosya indirme **DNS bağlantı hatası** nedeniyle
başarılı olmadı. Deprem dışındaki afet verileri bu ZIP içinde hâlâ hazır değildir.

## Doğrulama

```powershell
python -m unittest test_ortak_mimari test_adk_araclari test_bolge_puanlari test_harita test_yasam_ticaret -v
python test_hesaplama.py
python -m unittest test_adk_genisleme -v
```

Yerel testler gerçek 2025 USGS CSV'sini, 81 il GeoJSON'u ve sadece test sırasında oluşturulmuş örnek ilçe tablolarını kullanır. **Test tabloları yayımlanan nüfus verisi değildir.** Canlı Streamlit il tıklaması ve Gemini bağlantısı bilgisayarında ayrıca denenmelidir.

## Proje geçmişi ve hocanın istediği ekran görüntüleri

Daha önceki ZIP klasörleriyle gerçek tarihî ekran görüntüsü çekilerek aşağıya eklenecek:

| Sürüm | Ekran görüntüsü |
|---|---|
| İlk deprem prototipi | `docs/screenshots/01-ilk-prototip.png` |
| Koyu tema ve ilk Google ADK | `docs/screenshots/02-adk-sismik.png` |
| Ortak harita v3.4/v3.5 | `docs/screenshots/03-ortak-harita.png` |
| Ticaret & birincilik açıklaması | `docs/screenshots/04-neden-birinci.png` |

Görüntüleri çekip `docs/screenshots/` içine koyduktan sonra Markdown ile ekle:

```markdown
![İlk prototip](docs/screenshots/01-ilk-prototip.png)
![Son arayüz - Türkiye haritası](docs/screenshots/03-ortak-harita.png)
![Neden Bu İlçe Birinci](docs/screenshots/04-neden-birinci.png)
```

**Görseller henüz ZIP'te yoktur.** Görseller gerçek uygulamadan çekilmeli; tarihî sürüm için yeni sahte ekran çizilmemeli.

## Kaynak ve lisanslar

- [USGS Earthquake Catalog](https://earthquake.usgs.gov/earthquakes/search/)
- [geoBoundaries Türkiye ADM1](https://www.geoboundaries.org/api/current/gbOpen/TUR/ADM1/)
- [TÜİK tabanlı ilçe demografi JSON aktarımı](https://github.com/topografya/veri) — kaynak TÜİK ADNKS 2025
- [Resmî TÜİK ADNKS 2025](https://data.tuik.gov.tr/Bulten/Index?p=Adrese-Dayali-Nufus-Kayit-Sistemi-Sonuclari-2025-53899)
- [Sanayi ve Teknoloji Bakanlığı İlçe SEGE-2022](https://www.sanayi.gov.tr/assets/pdf/birimler/2022-ilce-sege.pdf)
- [Streamlit](https://docs.streamlit.io/)
- [Google ADK](https://adk.dev/)

## Sonraki veri aşamaları

1. **Tamamlandı:** 2025 ilçe nüfus CSV ve SEGE-2022 resmî PDF kaynaklarından 973 ilçe birebir eşleşti.
2. **Tamamlandı (v3.8):** Ulusal ilçe ticaret sıralamasına OSM işletme etiketleri ve toplu taşıma kayıtları eklendi; seyrek veri içeren lojistik puanında bu göstergeler kullanılmıyor.
3. Orman yangını, sel/taşkın, heyelan, çığ, fırtına ve kuraklık verilerini **81 il düzeyinde** doğrulayarak katmanlara ekle.
4. Gerçek ekran görüntülerini README'ye ekle; son sürüm GitHub/Streamlit üzerinde ayrı test edilsin.

**Hızlı doğrulama:** `python kontrol_sege_nufus.py` komutu `OK: 973/973` vermelidir. İlgili ham ve birleşik CSV'ler zaten pakettedir.


## SEGE-2022 gerçek PDF doğrulaması (v3.5.3)

`SEGE_DOGRULAMA_NOTU.md` dosyasında 81 il, 973 ilçe ve 0 PDF içi çelişki sonucunun ayrıntılı kanıtları yer alır. Paket içindeki `indirilen_veriler/ilce_sege_2022.csv` doğrudan uygulama tarafından okunur. 2025 nüfus dosyası başka kaynak olarak ve ayrı yıl etiketiyle kullanılır.


### v3.5.5 — Neden Birinci? gerekçeli paragraf

Türkiye genelindeki ve il içindeki yaşam/ticaret birincileri artık yalnızca puanla değil,
aynı karşılaştırmadaki gerçek nüfus (2025), SEGE (2022), yaklaşık nüfus yoğunluğu
ve model katkılarına dayanan kısa ve ilçeye özgü yorum paragrafıyla açıklanır.
Yorum, `atlas_analiz.neden_birinci` sonucunun `yorum_paragrafi` alanında yer alır;
hem Streamlit arayüzü hem Google ADK aynı veriyi kullanır.
Başka veri yokken kira, yaya trafiği, gerçek gelir, suç veya sağlık göstergeleri icat edilmez.


## v3.8 — Türkiye 973 ilçe OSM gerçek veri entegrasyonu

`indirilen_veriler/ticaret_osm_ilce.csv` ve `indirilen_veriler/ticaret_osm_manifest.json`
973 ilçenin tamamı için hazırdır; uygulama ve Google ADK bu özetleri otomatik okur.
**Ham `.osm.pbf` dosyasını siteye yüklemeyin; Python yeniden işlemeye gerek yoktur.**

Kaydedilen OSM kategorileri: yeme-içme 40.686, perakende 88.248, hizmetler 49.656,
lojistik 144, toplu taşıma 57.277. Toplam 236.011 kategori/ulaşım etiketi.
Kategoriler üst üste binebilir ve gönüllü OSM kapsamı bölgeye göre değişir.
Bu sayılar **resmî faal işletme veya müşteri sayısı değildir**.

Lojistik etiketleri 973 ilçenin yalnızca 79'unda sıfırdan büyüktür.
İşletme/rekabet göstergelerinin en az %20 ilçede ve en az üç ilçede
gözlenmesi koşulu, OSM kayıtları nadir olduğunda sıfırları rekabet avantajı saymamak için eklenmiştir.
Bu bir veri-kapsam korumasıdır, bilimsel olarak kalibre edilmiş eşik değildir.
Eksik göstergeler puandan çıkarılıp kalan ağırlıklar yeniden normalize edilir.
OSM lojistik sayımları yine harita ve tabloda görünürdür.

İlçe sınırı kaynağı, ilk bağlantı çalışmadığı için alternatif siteden indirilmiştir
(https://rodostoteknoloji.com/online-tools/turkey-boundaries.html);
ilçe adlarının eşleştirilmesi ve hatalı geometri düzeltmesi sonrasında veri işlenmiştir.
PBF'nin içindeki gerçek OSM snapshot tarihi bağımsız doğrulanmamıştır.
**Ticari kira, yaya sayısı, gerçek müşteri ve ciro verileri hâlâ yoktur.**

Testler: `python -m unittest discover -p "test_*.py"`

## v4.2 Gemini ile seçmeli açıklamalar

Genel Bakış, Yaşam Kalitesi, Ticari Potansiyel ve Afet Analizi ekranlarında **✦ Gemini ile özgün yorum oluştur** butonu bulunur. Gemini, Python'un çıkardığı hesaplanmış verileri yorumlar; sıralamalar Python'da kalır. API anahtarı bulunmadığında uygulama mevcut açıklamalarla çalışır. `V42_GEMINI_KURULUM.md` kurulum yönergelerini içerir.
