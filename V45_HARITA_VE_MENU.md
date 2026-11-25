# Afet Atlas v4.5 — Harita ve menü kullanım iyileştirmeleri

Bu sürüm v4.4 üzerine kuruludur. **Gerçek veriler, puanlama, yaşam/ticaret sıralamaları, seçilebilir sabit il haritaları ve Gemini/Google ADK entegrasyonu korunmuştur.** GitHub veya Streamlit Community Cloud'a otomatik yükleme yapılmamıştır.

## Kullanıcı arayüzü

- **Gerçek kenar menüsü aç/kapat düğmesi:** Streamlit'in sol üstte görünen iki oklu düğmesi kırmızı vurgulu hamburger (☰), menü açıkken kapatma (✕) işaretiyle stillendi. Native Streamlit düğmesi korunur. Streamlit sürümlerinde düğmenin DOM yapısı farklılaşabileceği için yerel tarayıcıda kontrol edilmelidir.
- **Analizler alt menüsü:** v4.3'teki sade `▾ Analizler` görünümüne geri alındı. v4.4'ün kırmızı çerçeveli/uzun açıklamalı alt menü başlığı kaldırıldı.
- **Afet türü:** Ana Afet Analizi sayfasının en üstünde, harita filtrelerine yakın bir seçim alanına taşındı; artık kenar menüsünde aranmasına gerek yok.
- **Deprem filtreleri:** Başlangıç yılı, bitiş yılı, minimum büyüklük ve il sınırına yakınlık birlikte haritanın hemen üstünde. `↺ Sıfırla` 2025, M4.5 ve 0 km varsayılanına döndürür. Filtreler yine aynı USGS analiz hesaplamalarını çalıştırır.
- **Deprem il kayıtları:** Haritadan seçilen ilin eşleşen gerçek deprem kayıtları ülke genelindeki ilk beşin yerine, il özetinin içinde gösterilir; en yeni kayıt en üsttedir. Sekmelerden **Hareketliliği en yüksek 5 il** tablosuna ayrıca erişilebilir. Göstergeler uydurma sayı kullanılmadan doğrudan `eslesenler` tablosundan çekilir.
- **Yardım metinleri:** Afet türü ve deprem filtrelerinin yeni konumunu tarif edecek şekilde güncellendi.

## İncelenen örnekler

- **USGS Latest Earthquakes:** Harita ile ilişkili filtrelerin ve seçili deprem kayıtlarının liste halinde sunulması. https://earthquake.usgs.gov/earthquakes/map/
- **ArcGIS Dashboards:** Seçicilerin (tarih/kategori vb.) başlık ve yan panelde gruplandırılması. https://doc.arcgis.com/en/dashboards/latest/create-and-share/selectors.htm

Bu örneklerin bütün davranışları birebir kopyalanmadı. Afet Atlas'ın sürüklenmeyen ve il alanına tıklanan sabit Türkiye haritası korundu.

## Kurulum ve test

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Önce **Afet Analizi → Deprem** alanına girip başka bir il seç, kayıt tablosunu kontrol et, yıl / büyüklük / km filtresini değiştir, `Sıfırla` düğmesini dene. Ardından soldaki menüyü aç/kapat ve v4.3 tarzındaki **Analizler** alt menüsünü kontrol et.

**Not:** Veri/paket kontrolleri ve ilgili Python testleri gerçekleştirilmiştir. Bu ortamda Streamlit arayüzünün gerçek tarayıcı testi yapılamadı. İlk denemeyi yerel ortamda yapıp sonra GitHub'a yükleyin.
