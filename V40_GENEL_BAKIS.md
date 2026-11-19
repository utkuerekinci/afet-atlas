# Afet Atlas v4.0 — Genel Bakış yeniden tasarımı

- Deprem ağırlıklı karşılama ekranı kaldırıldı. USGS kaydı, M büyüklüğü ve olay eşleşmesi kartları yalnızca **Afet Analizi > Deprem** sayfasında bulunur.
- Yeni karşılama metni: **Türkiye’nin haritasından fazlası.** Alt metin yaşam, ticaret ve afet modüllerini birlikte anlatır.
- Genel Bakış metrikleri: **81 il / 973 ilçe / 7 afet türü / 4 ticaret sektörü**.
- Tek Türkiye haritası üç keşif merceğine ayrıldı: **Yaşam ve nüfus**, **Ticari hareketlilik**, **Doğal afetler**.
- Yaşam haritasında nüfus, ilçe sayısı ve SEGE ortalama sırası; ticaret haritasında OSM yeme-içme, perakende, hizmet, lojistik ve ulaşım; afet görünümünde 2024/2025 yangın sayısı ve 2025 yanan alan karşılaştırılır.
- İl seçimi harita işaretçileriyle veya **Şehir seç** alanından yapılır. Sağ panel konuyla birlikte değişir ve ilgili ayrıntı sayfasına götürür.
- Kullanıcının sevdiği **Analiz alanları** bölümü aynen korundu.
- Google ADK, diğer bölümler, 973 ilçe nüfus/SEGE ve OSM veri dosyaları değiştirilmedi.
- Ana sayfanın çalışması için USGS'ye ağ isteği gerekmez; proje verilerini yerel dosyalardan okur.

Yerelde çalıştırma: `python -m streamlit run app.py`
