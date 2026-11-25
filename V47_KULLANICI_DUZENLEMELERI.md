# Afet Atlas v4.7 — Arayüz ve karşılaştırma düzenlemeleri

## Tek “Neden Bu İlçe Birinci?”
Yaşam Kalitesi ve Ticari Potansiyel sayfalarında, seçilen ilin birinci ilçesine yönelik gerekçeli yorum sağ üstteki panelde tek kez görünür. Sıralama sekmelerinin altındaki tekrar eden yorumlar kaldırıldı. Gemini düğmesi bu üst yorumun içinde korunur.

## Kullanıcı dostu ilçe karşılaştırması
“Türkiye genelindeki enler” ve “Seçilen ildeki enler” sekmelerinde aynı karşılaştırma arayüzü vardır. Her iki tarafta önce **il**, ardından o ilin **ilçesi** seçilir. Listeler Türkçe alfabetik sıradadır. İl içi sekmesinde şehir sabittir. Seçilen iki ilçe sayısal tabloda ve puan farkıyla karşılaştırılır. Aynı ilçe iki kez seçilirse bilgilendirme yapılır.

## Ticari Potansiyel haritası
Eski sürümde ilk seçenekler ağırlıkla OpenStreetMap (OSM) işletme ve ulaşım kayıtlarıydı. Bunlar veri girdileridir; doğrudan model çıktısı değildir. Bu sürümde **Sektörel fırsat puanı** varsayılan harita göstergesidir. Her il için, seçilen sektörde *Türkiye genelinde aynı ölçekle* puanlanmış en yüksek üç ilçenin ortalamasını gösterir. Nüfus, ortalama ilçe SEGE sırası ve ilçe sayısı da haritada seçilebilir. OSM sektörel kayıtları yine isteğe bağlı filtrelerdir. Sektör seçimi değiştirilince fırsat haritası güncellenir.

## Görsel düzen
- Sol menüde **Analizler** bölümü ve alt sayfaları daha açık mavi tonlarla belirtilir.
- Genel Bakış, Siz Sorun, Yardım, Veri ve Yöntem menü düğmeleri kırmızı tonlarla gösterilir.
- Menü düğmelerinin yazı boyutları hafifçe büyütüldü.
- Ticaretin OSM işletme ve ulaşım sayıları, kapalı başlayan bir açılır/kapanır alana taşındı.
- Yaşam ve Ticaret sayfalarının Yardım yönergeleri aşağı kaydırma ve il/ilçe seçimini açıklayacak biçimde düzenlendi.

## Korunanlar
Afet Analizi v4.6 görünümü; sabit, tıklanabilir Türkiye haritası; deprem kayıtları; 973 ilçe nüfus/SEGE/OSM verisi; Gemini bağlantısı; analitik puanlama ve mevcut diğer modüller korunur. Yönetici paneli ve GitHub yönlendirmesi bu sürümde eklenmedi.

## Kontrol
İlgili UI, geçmiş sürüm ve gerçek 973 ilçe verisi testleri çalıştırıldı. Bu ortamda Streamlit paketi bulunmadığı için tarayıcı görsel testi yerel çalıştırma sırasında yapılmalıdır.
