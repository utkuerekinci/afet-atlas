# Afet Atlas v3.8 — 973 İlçe OSM Sonuç Özeti

## Entegrasyon
- Gerçek kullanıcı üretimi `ticaret_osm_ilce.csv` ve `ticaret_osm_manifest.json` proje içindeki `indirilen_veriler/` klasörüne eklendi.
- Nüfus/SEGE veri tablosundaki 973 ilçe ile 973/973 eşleşme: başarılı.
- İl sayısı: 81. Eksik/çift satır yok.
- Uygulama ve Google ADK bu dosyaları otomatik okur.

## Etiket sayıları
| Kategori | OSM etiketi | Sıfır kayıtlı ilçe |
|---|---:|---:|
| Yeme-içme | 40.686 | 250 |
| Market/perakende | 88.248 | 207 |
| Hizmet | 49.656 | 14 |
| Lojistik | 144 | 894 |
| Toplu taşıma | 57.277 | 310 |
| **Toplam** | **236.011** | — |

Toplam, **tekil işletme sayısı değildir**. Örtüşen kategori etiketleri bulunabilir.
8 ilçede bu beş başlıkta da sıfır etiket var: bu ilçelerde işletme bulunmadığını kanıtlamaz.

## Model
- Yeme-içme, market ve hizmetler için OSM etiket yoğunluğu, nüfusa göre OSM rekabet baskısı, ulaşım, nüfus, nüfus yoğunluğu ve SEGE sırası kullanılır.
- Lojistik etiketleri çok seyrek olduğundan **bu sektördeki işletme/rekabet göstergeleri ulusal puana alınmaz**; ham lojistik etiketleri haritada ve tabloda kalır.
- Veri yeterlilik kuralı: karşılaştırılan ilçelerin en az %20'si ve en az üç ilçe ilgili sektörde pozitif OSM etiketine sahip olmalıdır. Bu kural projenin ihtiyatlı tercihi olup ampirik doğrulanmış eşik değildir.
- Müşteri sayısı, yaya trafiği, işyeri kiraları, ciro ve kâr **mevcut değil**. Bu nedenle model yalnızca ilçe önceliklendirme aracıdır.

## Kaynaklar ve kullanım
- Geofabrik Türkiye PBF: https://download.geofabrik.de/europe/turkey-latest.osm.pbf
- GeoJSON ilçe sınırları: https://rodostoteknoloji.com/online-tools/turkey-boundaries.html (kullanıcının sağladığı, eşleşme/geometri düzeltmeleri uygulanmış dosya)
- PBF snapshot tarihi veri dosyasından ayrıca doğrulanmadı. Kaynakta 2026-11-18 dosya değiştirilme tarihi beyan edilmiş.
- `python -m unittest discover -p "test_*.py"`
- `python -m streamlit run app.py` ile siteyi başlat. Ham `.osm.pbf` dosyasını yükleme veya yeniden işleme gerek yok.
