# v4.2.1 — Gemini hata tespiti ve model ayarı

- Önceki sürümde tüm Gemini hataları tek bir genel uyarıyla gizleniyordu.
- Yeni sürüm hata türünü gösterir, `Teknik hata ayrıntısı` paneli API anahtarını maskeler.
- Varsayılan `gemini-3.1-flash-lite` modelidir. `secrets.toml` içinde `AFET_ATLAS_MODEL` hâlâ `gemini-3.5-flash-lite` ise eski ayar geçerlidir; bunu kendiniz değiştirmelisiniz.
- 429 kota, 403 izin, 401 kimlik, 404 model ve 503 servis hataları farklı mesajlarla görünür.
- Google API'ye erişim anahtarı bu pakette olmadığından gerçek API çağrısı testi yapılamadı.
