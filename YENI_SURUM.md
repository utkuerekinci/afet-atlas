# Afet Atlas v3.9 — Yorum Odaklı Analiz

Önce [V39_DEGISIKLIKLER.md](V39_DEGISIKLIKLER.md) dosyasını okuyun. Türkiye geneli ve il içi ticaret/yaşam yorumları geliştirildi.

---

> **v3.5.5 geliştirmesi:** “Neden Bu İlçe Birinci?” bölümüne her ilçe ve seçilen sektör/yaşam tercihine göre değişen **gerekçeli yorum paragrafı** eklendi. Yorum doğrudan nüfus, SEGE, yaklaşık yoğunluk, model ağırlıkları ve ilk iki ilçenin puan katkılarından oluşturulur. Birinci ilçenin ikinciye göre zayıf kaldığı göstergeler de açıklanır. Ayrıca ADK araçları aynı `yorum_paragrafi` alanını döndürür. Başka veri yokken kâr, işletme sayısı, ulaşım veya güvenlik iddiası üretilmez.

> **v3.5.4 güncellemesi:** Önceki sürümlerdeki nüfus–SEGE eşleşme eksikliği çözüldü. 973/973 ilçe ve 81 il tam eşleşiyor. Paket gerçek nüfus, SEGE ve birleşik CSV dosyalarını içeriyor. Ayrıntılar için `ESLESME_DUZELTMESI.md` belgesine bakın. Aşağıdaki eski sürüm notları tarihsel bilgi olarak korunmuştur.

# v3.5 — Çok amaçlı Google ADK ve kaynak toplama hattı

- Deprem araçları 6 → 13: ülke/il karşılaştırması, esnek sıralama, yıl/ay/büyüklük dağılımları, olay puanı gerekçesi.
- İlçe veri araçları 5 → 13 (973 ilçe/81 il nüfusu doğrulanınca): ülke çapında/il içinde nüfus sıralaması, iller kıyası, iki ilçe kıyası, sektör liderleri, yaşam için birincilik açıklaması, SEGE doğrulama durumu.
- 3 genel kaynak/kapasite aracı da eklendi: 7 afetin veri durumu, sektörel model tanımı, ADK'nin desteklediği soru türleri.
- `adk web` artık onaylı yerel ilçe nüfus dosyası bulunduğunda araçları otomatik açmayı deneyebilir; yoksa ilçe aracı açık görünmez.
- Siz Sorun ekranının örnek soruları arttırıldı.
- `kaynaklari_topla.py --hepsi`: nüfus/SEGE/demografi kaynaklarını ve OGM 2024–2025 Excel dosyalarını indirmeyi, içerik doğrulamasını ve ham CSV çıkarımını dener. Sonuçları `indirilen_veriler/kaynak_durumu.json` kaydına yazar.
- **18.11.2026 indirme durumu:** Mevcut konteynerde DNS/ağ erişimi başarısız; yeni kaynak verileri ZIP içinde değildir. Verinin yokluğu sayı uydurma yetkisi vermez.
- Paketli ve otomatik testli gerçek veri: 2025 USGS 159 kayıt ve 81 il sınırı. Erozyon kapsam dışında.

Tam veri aşamaları: [VERI_TOPLAMA_DURUMU.md](VERI_TOPLAMA_DURUMU.md)
