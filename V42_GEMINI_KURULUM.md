# Afet Atlas v4.2 — Gemini yorum motoru

Yeni sistem Python'un hesapladığı puan ve sıralamalara dokunmadan Gemini ile daha özgün bölge yorumları üretir. Yapay zekâ **yalnızca kullanıcı butona bastığında** çağrılır. Anahtar yoksa ve ağ hatası varsa Python açıklamaları devam eder.

## Yerelde çalıştırma (Windows / VS Code)

1. ZIP içindeki proje klasörünü VS Code ile aç.
2. Terminale `python -m pip install -r requirements.txt` yaz.
3. [Google AI Studio](https://aistudio.google.com/apikey) üzerinden Gemini API anahtarı oluştur. Anahtarı kimseyle paylaşma.
4. Proje klasöründe `.streamlit` klasörü varsa içine `secrets.toml` adlı bir dosya oluştur. `.streamlit/secrets.toml.example` dosyasını kopyalayarak da başlayabilirsin.
5. İçeriği, örneğin, şöyle olsun:

```toml
GOOGLE_API_KEY = "GOOGLE_AI_STUDIO_ANAHTARIN"
AFET_ATLAS_MODEL = "gemini-3.1-flash-lite"
```

6. Terminalde `python -m streamlit run app.py` çalıştır.
7. Genel Bakış'tan bir il seçip, Yaşam Kalitesi veya Ticari Potansiyel'e gidip **✦ Gemini ile özgün yorum oluştur** butonuna tıkla.

## Canlı dağıtım

Sunucunun/hostun ortam değişkenlerine `GOOGLE_API_KEY` ve isteğe bağlı `AFET_ATLAS_MODEL` ekle. **API anahtarını hiçbir koşulda GitHub'a, `app.py` dosyasına, ZIP içindeki kodlara veya istemci JavaScript'ine yazma.** `.gitignore`, `.streamlit/secrets.toml` dosyasını zaten hariç tutuyor.

> Uygulamanın kullanıldığı platformda Python/Streamlit sunucusunun çalışması ve dış HTTPS isteklerine izin verilmesi gerekir. Vercel'deki dağıtım biçimine göre sunucu yapılandırması ayrıca gerekebilir.

## Nasıl çalışıyor?

- **Python:** 81 il / 973 ilçeye ilişkin sayıları, sıralamaları, en yüksek katkılı göstergeyi ve karşılaştırma verilerini belirler.
- **Gemini:** Bu özeti kullanarak Türkçe doğal yorum üretir. Veri özetinin dışındaki özellikleri gerçek gözlemmiş gibi eklememesi yönünde talimat alır.
- **Önbellek:** Aynı veri/model kombinasyonu için sonuç 6 saat tutulur (sunucu tarafında). Aynı konuyu yeniden açmak gereksiz API çağrısı yapmaz.
- **Hata:** Anahtar eksik, kota dolu veya servis erişilemez ise Python yorumları kullanılabilir kalır.
- **Siz Sorun:** Mevcut Google ADK ajanı korunmuştur. USGS geçici olarak erişilemezse bile yaşam/ticaret araçlarıyla devam edebilir.

## Test ve sınırlar

- API anahtarı bu çalışma ortamında bulunmadığından gerçek Gemini yanıtı **canlı olarak doğrulanamadı**; butonun çalıştığını yerelde gerçek anahtarla kontrol etmek gerekiyor.
- Model erişimi hesap ve API kotalarına bağlıdır. Gerekirse `AFET_ATLAS_MODEL` değiştirilebilir.
- Gemini yorumları otomatik üretildiğinde sistemin puan ve sıralamalarını değiştirmez. İnceleme için sayısal karşılaştırmalar uygulamada ayrıca bulunur.


## v4.2.1 hata ayıklama
- Gemini isteği hata verdiğinde artık kod gerçek hata türünü (400/401/403/404/429/503, kütüphane, bağlantı) gösterir.
- “Teknik hata ayrıntısı” paneli API anahtarını gizleyerek hata açıklamasını gösterir.
- Varsayılan model `gemini-3.1-flash-lite` olarak değiştirildi. **Eski `secrets.toml` varsa model satırını da güncellemelisin; ZIP içindeki .example tek başına etkin ayarı değiştirmez.**
- `.streamlit/secrets.toml` gizlidir ve ZIP içinde bulunmaz. Eski klasöründen yeni klasöre kendin kopyalayabilirsin; hiçbir zaman sohbet veya GitHub'a yükleme.
- Google servisi hata verirse hatayı gidermeden sonuç başarıyla üretilmiş sayılmaz. Python yorumları kullanılabilir kalır.
