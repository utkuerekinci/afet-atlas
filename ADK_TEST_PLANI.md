# Afet Atlas – Google ADK ajan testi

## Önce filtreler

Streamlit ana sayfada başlangıç/bitiş yılı **2025–2025**, minimum büyüklük **4.5**, il sınırına yakınlık **0 km** olsun. Bu paket içindeki gerçek 2025 USGS CSV dosyasına dayalı bilinen sonuçlar aşağıdadır.

| Sorulacak soru | Beklenen bilgi | Beklenen araç |
|---|---|---|
| Bu analiz kaç USGS olayına dayanıyor? | 159 USGS olayı; 81 il; 33 il–olay eşleşmesi | `veri_kapsami` |
| Balıkesir'de kaç deprem var, toplam puanı kaç? | 18 eşleşme; 30 puan | `il_ozeti` |
| Ankara ile İstanbul'u karşılaştır. | Ankara: 2 eşleşme / 4 puan. İstanbul: 0 eşleşme / 0 puan. Sıfır eşleşme güvenli anlamına gelmez. | `il_karsilastir` |
| En yüksek hareketlilik puanlı il hangisi? | Balıkesir: 30 puan | `hareketliligi_en_yuksek_iller` |
| Balıkesir'deki en büyük üç depremi tarihlerle listele. | Ekrandaki İl İncelemesi ile karşılaştırılabilecek üç gerçek kayıt ve olay kimliği | `ilin_en_buyuk_depremleri` |
| Gelecek ay nerede kesin deprem olacak? | Belirsizliğini açıklamalı; tarih ve şehir uydurmamalı | Araç kullanımı gerekli olmayabilir |

## Nasıl ölçülür?

- **Sayısal doğruluk:** İlk beş sorgudaki sayı ve kayıtlar il inceleme/sıralama/veri kapsamıyla uyuşuyor mu? (doğru / toplam, örneğin 4/5)
- **Araç kullanımı:** Sayısal sorularda ADK işlem geçmişinde uygun Python aracı gerçekten çağrıldı mı?
- **Yanıltıcı iddialar:** Sıfır kayıt için %100 güvenli diyorsa veya deprem tahmini uyduruyorsa test başarısız.
- **Kararlılık:** Aynı soruyu üç kez sorarak tutarlılığı karşılaştır. Model yanıtının kelimeleri değişebilir; sayılar değişmemeli.
- **Kullanışlılık:** Aynı veriyi menülerden bulmak mı, ajana sormak mı daha kolay? Aradığın bilgiler net mi?

> **Önemli:** İlk beş sorunun beklenen araçları birer kural değildir; ADK alternatif olarak birden fazla doğru araç da kullanabilir. Önemli olan veriyi gerçekten araçtan alması ve doğru aktarmasıdır.

## ADK'nin kendi geliştirici ekranı

Proje klasöründe ve API anahtarı tanımlı terminalde:

```powershell
adk web .
```

Ajan olarak `afet_atlas_adk` seç. ADK Web'deki **Trace** ve **Eval** bölümlerinden araç çağrılarını ve test oturumlarını görebilirsin. Bu ayrı arayüz sabit **2025, M ≥ 4.5, 0 km** dosyalarıyla çalışır. Streamlit filtreleri bu ayrı ADK Web ekranına otomatik aktarılmaz.

**ADK'nin resmî değerlendirme açıklaması:** https://adk.dev/evaluate/

## Neyi henüz kanıtlamaz?

Bu paketle yapılan yerel Python testleri ADK araçlarının gerçek veriyle çalıştığını gösterir, fakat canlı Gemini API yanıtlarının kalitesini kanıtlamaz. Bunun için API anahtarıyla test sorgularını çalıştırmak gerekir.
