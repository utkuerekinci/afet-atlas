# Afet Atlas v4.8 — Özel yönetici paneli

- Sol menüye **🔒 Yönetici Girişi** eklendi. Ana site, 7 genel modülü ve navigasyon düzeni aynı şekilde korur.
- Kullanıcı adı + Argon2id şifre özeti Streamlit Secrets üzerinden doğrulanır. Google oturum açma kullanılmaz.
- Sadece yönetici CSV/JSON yükleyebilir; yükleme öncesi şema, il/ilçe sayısı, eşleşme ve resmî 2025/2024 toplamları kontrol edilir.
- Veri setleri **kaynak kod reposundan farklı** ve **Private** GitHub veri deposunda sürümlenir.
- Veri dosyası güncellendiğinde geçici çalışma alanı yeniden oluşturulur; hata halinde son geçerli anlık görüntü korunur.
- OSM ve isteğe bağlı kira verileri devre dışı bırakılabilir. Nüfus, SEGE ve yangın kayıtları temel olduğu için yanlışlıkla silinemez.
- GitHub dosya geçmişinden önceki içerik geri yüklenebilir.
- Otomatik USGS veri akışı ve Gemini API anahtarı mevcut düzeninde kalır.
- Yardım'daki açık kaynak kod bağlantısı **https://github.com/utkuerekinci/afet-atlas** olarak korunur.
- Adım adım kurulum: [YONETICI_KURULUM.md](YONETICI_KURULUM.md).

**Önemli:** Bu pakette gerçek yönetici şifresi, şifre özeti veya GitHub tokenı **yoktur**. Yeni private repo ve Streamlit Secrets kurulmadan özel depoya kayıt yapılamaz.
