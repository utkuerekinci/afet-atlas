# Afet Atlas v4.6 — Eksik alanların geri getirilmesi ve yaşam düzeni

Bu sürüm doğrudan **v4.5** kodu üzerine hazırlanmıştır. GitHub / Streamlit Cloud üzerindeki canlı uygulama değiştirilmemiştir.

## 1. Genel Bakış: eski TR / Yaşam / Ticaret / Afet görseli

- v4.2.1 sürümündeki özgün halkalı **TR · KEŞFET / YAŞAM / TİCARET / AFET** tasarımı aynı sınıf ve etiketlerle geri getirildi.
- v4.5'teki güncel **BİR ÜLKE · ÜÇ FARKLI BAKIŞ / AFET ATLAS / Türkiye’nin haritasından fazlası** metni ve metrik kartları korunuyor.
- Dar ekranlarda yörünge, üst başlığı sıkıştırmadan aynı etiketleri gösteren küçük kartlara dönüşüyor.

## 2. Sol menü: yanlışlıkla kaldırılan bağlantılar

`Siz Sorun`, `Yardım` ve `Veri ve Yöntem` düğmeleri v4.3 menüsünden geri getirildi. Bunlara ait sayfaların kodları zaten v4.5'te bulunuyordu; eksik olan menüye erişimdi. `Analizler` açılır menüsü, sol kenar aç/kapat düğmesi ve harita filtreleri korunuyor.

## 3. Yaşam Kalitesi: Neden Bu İlçe Birinci?

- Yaşam Kalitesi'nde, yaşam tercihi seçiminin yanındaki **Seçili İlde Öne Çıkan** kısa kartının yerinde artık il içi birinci ilçenin **Neden Bu İlçe Birinci?** açıklaması ve ilgili Gemini düğmesi gösteriliyor.
- İl içindeki aynı açıklama aşağıdaki sıralama sekmesinde tekrar gösterilmiyor.
- **Türkiye genelindeki enler** sekmesindeki Türkiye çapındaki gerekçe korunuyor.
- Hem Yaşam Kalitesi hem Ticari Potansiyel sıralamalarında **İki İlçeyi Karşılaştır** bölümü, **Karşılaştırmanın Sayısal Ayrıntıları** bölümünden önce geliyor.
- Ticari Potansiyel'in sağdaki kısa sektör/ilçe özeti korunuyor.

## Korunan işlevler

- v4.5'in Afet Analizi sayfası ve deprem kayıt veri modülü **değiştirilmedi**.
- 973 ilçenin nüfus/SEGE/OSM verileri, 81 il sınırları, sabit harita seçimi, Gemini/ADK yorumları ve önceki sıralama formülleri korunuyor.
- Yönetici paneli ve GitHub yönlendirmesi bu sürüme eklenmedi.

## Test ve çalıştırma

- Sözdizimi denetimi ve v4.5 deprem regresyon testleri çalıştırıldı.
- v4.6 menü / logo / sıralama sırası testleri başarılı.
- Gerçek 973 ilçe veri dosyasıyla yaşam ve ticaret il sıralama/yorum motoru çalıştırıldı.
- Tarayıcıda canlı Streamlit arayüzü test edilmedi. Özellikle mobil yerleşimi VS Code'da açarak kontrol edin.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Gemini'nin yerelde çalışması için eski **`.streamlit/secrets.toml`** dosyanızı yeni klasördeki `.streamlit` klasörüne kopyalayın. Gizli anahtar dosyasını GitHub'a yüklemeyin.
