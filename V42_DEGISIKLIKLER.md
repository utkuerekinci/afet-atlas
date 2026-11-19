# Afet Atlas v4.2 — Değişiklik özeti

- v4.1'deki il ve ilçe bazında özgün Python yorumları korundu.
- Yeni `atlas_gemini_yorum.py` eklendi. Gemini yorumları yalnızca kullanıcı isteğiyle oluşturuluyor.
- Genel Bakış'ta seçilen 81 il için konu ve göstergeye özel veri paketi oluşturuluyor.
- Yaşam/Ticaret'te Türkiye genelindeki veya il içindeki birincinin gerçek göstergeleri, ikinci/üçüncü aday ve katkı farkları Gemini'ye aktarılıyor.
- Afet bölümünde seçili il ve olay/gösterge karşılaştırması üzerinden yorum üretilebiliyor; depremde de il ve dönem bağı korunuyor.
- `Siz Sorun` sayfasında USGS erişimi yokken tüm ADK ekranının kapanması önlendi. Bölgesel ve diğer afet araçları kullanılabilir.
- Anahtar `GOOGLE_API_KEY` / `GEMINI_API_KEY` veya Streamlit Secrets üzerinden sunucu tarafında okunuyor; istemciye eklenmiyor.
- Google Gen AI Python SDK bağımlılığı açıkça `requirements.txt` dosyasına eklendi.
- Gemini yanıtları için 6 saatlik sunucu önbelleği var, aynı veri kombinasyonunda tekrar API çağrısı azaltılıyor.
- Anahtar veya ağ sorunu olduğunda Python yorumlarına geri dönülüyor.
- Canlı Gemini testi, kullanıcıya ait API anahtarı olmadan yapılamadı.
