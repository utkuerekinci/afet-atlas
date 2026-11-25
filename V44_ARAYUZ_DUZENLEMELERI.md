# Afet Atlas v4.4 — Arayüz ince ayarı

Bu sürüm v4.3 verileri, model hesaplamaları, sabit Folium haritaları ve mevcut Google ADK / Gemini entegrasyonunu korur.

- Genel Bakış üstünde BİR ÜLKE · ÜÇ FARKLI BAKIŞ, AFET ATLAS., Türkiye’nin haritasından fazlası. ve eski açıklama metni geri getirildi.
- 81 il / 973 ilçe / 7 afet türü / 4 ticari sektör özet kartları geri getirildi.
- Ana sayfanın Gemini açılır kutusu kaldırıldı; bütün analizlerde Gemini eylemi bulunduğu il veya ilçe adını içeren “... hakkında daha fazla bilgi” düğmesine dönüştürüldü.
- Yaşam ve ticarette tercih / sektör kontrollerinin yanına mevcut il içi sıralamanın birincisini özetleyen kompakt kart yerleştirildi. Sekmeler korunarak ilçe tablosu sola, yatay çubuk grafiği sağa taşındı.
- Grafikler sürüklenemez, yakınlaşıp uzaklaştırılamaz, mod çubuğu göstermez. Puan değerleri eksende veya çubuk üstünde değil, yalnızca fareyle üzerine gelindiğinde görülür.
- Nüfus haritalarındaki en koyu lacivert tonlar açık mavi/turkuaz ile değiştirildi. Diğer veri katmanları eski paletini korur.
- Afet türü seçimi sol menüde daha yukarı alındı ve yardım metinleri aşağı kaydırma yönlendirmeleriyle güncellendi.
- Analizler açılır menüsü kırmızı/mercan vurgu ve açıklayıcı etiketle daha belirgin hâle getirildi.
- GitHub bağlantısı ve yönetici paneli bu sürümde eklenmedi. Canlı GitHub/Streamlit deposunda değişiklik yapılmadı.

## Kontrol

`python -m unittest discover -v` ile regresyon testlerini çalıştırın. Yerel tarayıcıda 1366×768, 1920×1080 ve dar mobil boyutta grafik/menü seçimini ayrıca kontrol edin. Gemini için Secrets ayarındaki anahtarı kullanın; paket gerçek anahtar içermez.
