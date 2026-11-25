# Afet Atlas v4.3 — Arayüz ve kullanım düzenlemesi

Bu sürüm v4.2.1 üzerine kuruldu. Onaylanan değişiklikler:

- **Genel Bakış:** Kısa açılış, 81 il/973 ilçe özetleri, Yaşam/Ticaret/Afet filtreleri; tam genişlikte sabit Türkiye haritası. Bir il seçince kısa bilgi kartı ve **Ayrıntıya Git** düğmesi gösterilir. **Analiz Alanları** korunur.
- **Menü:** Streamlit'in yerleşik kenar çubuğu açma-kapama kontrolü ve içeride açılır **Analizler** alt menüsü; menü ilk açılışta kapalıdır.
- **Haritalar:** Önceki beyaz nokta seçimi yerine tüm il poligonu tıklanabilir. Sürükleme, yakınlaştırma ve fare tekerleği harita etkileşimleri kapalıdır. İlin sınırı seçiliyken vurgulanır. Gösterge renk ölçeği aşağıdadır.
- **Yardım:** Ayrı kullanım rehberi ve sayfa içi kısa yardım açılır pencereleri.
- **Ekran uyumu:** Bütün modüllerde büyük süslü başlıklar kaldırıldı, metrikler kompakt hâle geldi, dar ekranlarda kolonlar alt alta geçiyor.
- **Yönetici paneli:** Bilerek **eklenmedi**. Bu konuda yeni bir karar alınmadan veri yönetimine dokunulmadı.
- **Veri / hesaplama / Gemini:** Mevcut il ve ilçe verileri, analiz puanlamaları, Google ADK ve Gemini entegrasyonu korundu.

## Kurulum

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Haritanın alan tıklaması için `folium` ve `streamlit-folium` paketleri requirements.txt'ye eklendi. Harita JavaScript/CSS kütüphanelerini ilk gösterimde yükler; çevrimiçi bağlantı gerekir.

## Canlı site güncelleme

1. ZIP içindeki güncel dosyaları mevcut GitHub reposunun **ana dizinine** yükle, klasör yapısını koru.
2. `.streamlit/secrets.toml` dosyasını GitHub'a **yükleme**. ZIP'te yalnızca örnek dosya vardır.
3. `Commit changes` sonrası Streamlit Community Cloud'da yeni sürümün açılışını kontrol et. Mevcut Streamlit Secrets ayarların saklı kalır.
4. Yerel kontrol için: Genel Bakış'ta 3 filtreyi, İstanbul/Ankara/Kars il seçimini; Afet'te Deprem/Orman Yangını; Yaşam ve Ticaret sıralamalarını; Gemini yorum butonunu; yardım sayfasını dene. 1366×768 çözünürlükte de kontrol et.

## Teknik doğrulama

- 81 il sınırı tek sefer `shapely.simplify(0.013, preserve_topology=True)` ile küçültülür; kaynak GeoJSON değiştirilmez.
- Seçilen il `st.session_state['secilen_il']` anahtarıyla modüller arasında korunur.
- Plotly veri grafiklerine müdahale edilmedi. İlleri gösteren ana haritalar Leaflet'e geçirildi.
- Otomatik testler: `python -m unittest test_v43_sabit_harita -v`; mevcut hesaplama testleri de çalışır.
- Streamlit ve streamlit-folium paketlerinin bu çalışma ortamında yüklenememesi nedeniyle **canlı tarayıcıdaki tüm etkileşimler burada test edilmedi**. İlk yerel çalıştırmada haritadan il tıklama ve kenar çubuğu aç/kapat hareketlerinin ayrıca sınanması gerekir.
