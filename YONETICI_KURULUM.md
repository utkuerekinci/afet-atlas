# Afet Atlas v4.8 — Yönetici paneli kurulumu

Bu rehber **iki ayrı GitHub deposu** kullanır. Kod deposu herkese açık kalır:

- **Kaynak kod:** https://github.com/utkuerekinci/afet-atlas (mevcut; Yardım sayfasındaki bağlantı burayı açar).
- **Veri deposu:** `utkuerekinci/afet-atlas-veri` (yeni oluşturulacak **Private** depo; örnek isim). Bu adres kod deposunun yerine geçmez.

**Uyarı:** Kullanıcı adını, gerçek şifreni ve GitHub erişim anahtarını sohbetlere ya da kod deposuna gönderme. Henüz özel repoda oluşturduğun veri dosyaları olmasa bile v4.8 paketli başlangıç verileriyle çalışır; yönetici güncellemeleri repo kurulduktan sonra etkinleşir.

## 1. Özel veri deposunu oluştur

1. GitHub hesabında **New repository** seç.
2. Repository name alanına `afet-atlas-veri` yaz. **Private** seçeneğini işaretle.
3. Depoyu oluştur. `main` dalı olacak şekilde başlangıç README dosyası oluşturabilirsin.
4. Bu paketten **ayrı verilen** `Afet_Atlas_Ozel_Veri_Deposu_Baslangic.zip` dosyasını aç.
5. İçindeki `indirilen_veriler` klasörünü ve `README.md` dosyasını yeni **özel veri reposuna** yükle, commit et. İstersen özel repo `README.md` dosyasını mevcut olanın üzerine koy.
6. CSV/JSON dosyalarını kod deposunun yanlış klasörüne yükleme: özel repo ile `afet-atlas` kod reposunu karıştırma.

## 2. Yalnızca bu depoya yetkili GitHub tokenı oluştur

GitHub > **Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token**:

- **Resource owner:** veri deposunu oluşturduğun kullanıcı.
- **Repository access:** `Only select repositories` > yalnızca `afet-atlas-veri`.
- **Repository permissions:** `Contents` → `Read and write` (Metadata: Read otomatik).
- Tokenın süresi dolduğunda yeni token üretip Streamlit Secrets'ta yenilemen gerekir.

Tokenı **koda, README'ye veya bu sohbete yapıştırma**. Sadece güvenli `secrets.toml` / Streamlit Cloud Secrets alanına yaz.

## 3. Kendi kullanıcı adı ve şifreni oluştur

v4.8 kod klasöründe terminal aç ve gerekli kütüphaneleri yükle:

```powershell
python -m pip install -r requirements.txt
```

Ardından:

```powershell
python yonetici_sifre_olustur.py
```

Şifreni *terminalin gizli girişinde* iki kez yaz (en az 12 karakter). Terminal yalnızca `$argon2id$...` ile başlayan **şifre özetini** gösterecek. Gerçek şifren hiçbir dosyaya yazılmaz.

## 4. Streamlit Secrets'ı doldur

Streamlit Community Cloud'da mevcut Afet Atlas uygulamana gir, uygulama ayarlarında **Secrets** alanını aç. Daha önceki Gemini anahtarını **silmeden** aşağıdaki satırları ekle:

```toml
AFET_ATLAS_VERI_REPOSU = "utkuerekinci/afet-atlas-veri"
AFET_ATLAS_VERI_DALI = "main"
AFET_ATLAS_VERI_TOKEN = "BURAYA_KENDI_FINE_GRAINED_TOKENIN"
AFET_ATLAS_ADMIN_KULLANICI = "KENDI_KULLANICI_ADIN"
AFET_ATLAS_ADMIN_SIFRE_OZETI = "BURAYA_URETTIGIN_$argon2id$_OZETI"
```

**Bu sadece bir şablondur.** Kullanıcı adı ve parolanı kendin belirlersin. Gerçek tokenı ve hash'i her iki repoda da tutma.

Yerelde çalıştırmak için `.streamlit/secrets.toml` oluşturup aynı ayarları oraya yazabilirsin. `.gitignore` bu dosyanın GitHub'a gönderilmesini engeller; yine de commit öncesi kontrol et.

## 5. Önce yerelde kontrol et

```powershell
python -m streamlit run app.py
```

Sol menüden **Yönetici Girişi** bölümüne geç. Giriş yap. **Veri Setleri** sekmesinde özel depo bağlantısını ve dosyaları gör. Küçük bir güncellemeyi önce yerelde test et. Yanlış veri eklemek için değil, gerçekten güncel ve kaynaklı bir dosya kullan.

Yayımlamadan önce CSV/JSON şeması, il/ilçe sayısı, sütunlar ve mevcut verilerle eşleşme sınanır. Testi geçmeyen dosya özel repoya **gönderilmez**. "Veriyi Yayınla" onayı olmadan mevcut veri değişmez.

## 6. Yönetim davranışı

- **Veri Ekle/Güncelle:** Önce dosyayı seç → kontrol et → önizle → açıklama gir → yayını onayla.
- **Yayından Kaldır:** OSM ve isteğe bağlı kira gibi katmanlar devre dışı bırakılabilir. Gereken nüfus/SEGE/yangın dosyaları bu yolla silinmez; önceki sürüme döndürülür.
- **Sürüm Geçmişi:** GitHub dosya commit geçmişindeki eski sürüm yeniden yayımlanabilir.
- **Yenileme:** Uygulama özel veri deposundaki güncellemeleri en fazla yaklaşık 3 dakikada bir kontrol eder. Yönetici panelindeki değişikliklerden hemen sonra yenileme yapılır; tekrar çizilen analiz önbelleği temizlenir.
- **Bağlantı kesilirse:** Önceden doğrulanmış son veri veya paketli başlangıç verisi kullanılır. Yönetici panelinde senkronizasyon sorunu gösterilir.
- **USGS deprem:** Otomatik veri akışı yönetici yükleme ekranına taşınmadı.
- **81 il sınır geometrisi:** Uygulama referansı olarak kalır; yönetici panelinde rastgele GeoJSON yüklenemez.

### Mevcut veri seti sınırı

İlk yönetici paneli, **mevcut şemadaki** 2025 nüfus, 2022 SEGE, OSM ve 2024/2025 orman yangını dosyalarını güncelleyebilir; ayrıca kira verisi ekleyebilir. Yeni yıl (2026 nüfus/SEGE), yeni afet türü veya tamamen yeni gösterge eklemek için önce veri şeması ve analiz kodunu ayrı bir sürümde güncellemek gerekir. Mevcut yıl doğrulamalarını geçersiz kılan verileri kabul etmez.

### Güvenlik notu

Şifreler düz metin saklanmaz: Argon2id özeti kullanılır. Oturum üç saat sonra biter; çıkış düğmesi vardır. Aynı oturumda art arda beş başarısız girişten sonra beş dakika beklenir. Bu temel Streamlit oturum denetimi, harici kimlik doğrulama sunucusunun dağıtık saldırı korumasını içermez. Yönetici hesabında güçlü ve benzersiz bir şifre kullan; GitHub tokenını sadece özel repoya sınırla.

## 7. Canlı yayına geçmeden önce

Kaynak kod reposuna v4.8 uygulama dosyalarını ekleyip commit et. Özel veri reposundaki dosyaları kaynak kod reposuna kopyalama. Streamlit Cloud Secrets yapılandırmasını tamamladıktan sonra yeniden başlat, harita/yaşam/ticaret/afet/Gemini ve Yönetici Girişi bölümlerini kontrol et.

GitHub kaynak kod bağlantısı Yardım bölümünde **https://github.com/utkuerekinci/afet-atlas** olarak kalır; özel veri deposuna ziyaretçi bağlantısı verilmez.
