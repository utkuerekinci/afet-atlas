# Afet Atlas v3.6 — Veri kalitesi ve kalan eksikler

**2026-11-19** tarihinde erişilebilen resmî kaynak bağlantıları yeniden kontrol edildi. Uygulamanın veri tabanında altı afet için aşağıdaki ayrım korunmuştur.

1. **Orman yangını:** 2024–2025 ikincil tablo kayıtları toplam/il sayısı açısından sınandı. 2024 olay sayısı 77/81; yanan alan 74/81, 2025 ikisi de 81/81. Resmî OGM XLSX ağ sınırlaması nedeniyle indirilemedi; *resmî satır-satır doğrulama bekliyor*.
2. **Sel:** MGM 2024 Türkiye geneli 434 olay. Metinde Van, Elazığ, Ankara, Konya, Muğla, Antalya, İzmir, Balıkesir geçer. Van en yüksek kaydedilen il olarak vurgulanır. Diğer illere ulusal sayıyı paylaştırmadık.
3. **Heyelan:** MGM 2024 Türkiye geneli 42 olay. Artvin, Siirt, Rize yıl geneli öne çıkan iller; Bitlis, Elazığ, Yozgat, Ankara, Şırnak, Hakkâri ve Bursa ilkbahar örnekleridir. Tüm illere kesin sayı atanmadı.
4. **Çığ:** MGM 2024 Türkiye geneli 17 olay. MGM haritasında Van 6–8, diğer sekiz belirtilen il 1–2 aralığında; kesin bireysel sayıya çevrilmedi.
5. **Fırtına:** MGM 2024 Türkiye geneli 257 olay. Kayseri, Antalya, Muğla, Çorum ve Burdur öne çıkan iller; kesin il sayıları yok.
6. **Kuraklık:** MGM'nin 2024 raporundaki 7 bölgesel yıllık yağış değişimi (%). Bu bir SPI haritası değil. İl bazlı sayısal kuraklık analizini tamamlamak için il istasyonu veya kuraklık indeksi gerekiyor.

### İleri entegrasyon için tamamlama işi

- OGM 2015–2023 ve resmî OGM 2024–2025 il Excel dosyalarını ayrı ayrı temin edip yılları veri setine eklemek.
- MGM 2024 haritalarındaki 81 il için olay sınıflarını görsel doğrulamayla çıkarmak veya erişilebilir bir resmî sayısal tablo bulmak. 2025 raporunu da benzer biçimde işlemek.
- Kuraklık için MGM SPI'yi il bazında kapsayan uygun lisanslı/verilebilir tabloyu almak veya istasyon tarihsel verileriyle tanımlı metodoloji üretmek. Bölgesel yağış anomalisi SPI olarak sunulmaz.
- Google ADK'nin API üzerinden uçtan uca testi ve Streamlit Cloud'da il seçme tarayıcı denemesi.
