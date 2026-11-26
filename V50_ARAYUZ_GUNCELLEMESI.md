# Afet Atlas — Üst Menü ve İl Odaklı Harita (v5.0)

## Değişiklikler
- `.streamlit/config.toml` ile sabit koyu tema.
- Masaüstü yatay menü / mobil Streamlit hamburger navigasyonu.
- `Hakkımızda` sayfasına 81 il / 973 ilçe / 7 afet / 4 sektör bilgileri.
- Genel Bakış altındaki analiz kartları ve ana sayaçlar kaldırıldı.
- Genel Bakış haritası yanında seçili il özeti ve üç analize geçiş.
- Seçili il haritada odaklanır; Türkiye görünümüne dönüş düğmesi.
- Yaşam tercihi harita üstünde açılır kutuya taşındı.
- Yaşam/ticaret haritasının yanında il özeti, neden birinci ve il içi ilk 10.
- Kaydırma düğmesi ekranın altından daha yukarı taşındı.

## Önemli teknik notlar
- Streamlit, widget olaylarında uygulamayı yeniden çalıştırır. Seçili il ve odak durumu session_state üzerinde tutulur; yeniden çalıştırmayı tamamen kaldırmak ayrı bir istemci bileşeni gerektirir.
- İleri düzey Google Maps tarzı harita üstü sürüklenebilir paneller yerine responsive Streamlit kolon panelleri kullanıldı.
- İlk açılışta Türkiye genel haritası görünür; il seçildiğinde yakınlaşır.
- Özel GitHub veri deposu veya Streamlit Secrets arşive eklenmedi ve değiştirilmedi.
- Başlangıç testleri yalnızca statik Python derlemesidir; gerçek Streamlit tarayıcı testi bu ortamda yapılamamıştır.

## Yükleme
Arşivi açıp `afet-atlas-main` dizininin **içindeki** dosya ve klasörleri
GitHub kaynak kodu deposunun köküne aktar. Özellikle gizli `.streamlit` klasörünü de yükle.
Streamlit Cloud proje ayarları varsa `theme` kısmının proje dosyasıyla çakışmadığını kontrol et.
