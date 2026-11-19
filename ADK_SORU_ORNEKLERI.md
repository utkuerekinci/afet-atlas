# Afet Atlas v3.5 · ADK / Gemini soru çeşitliliği

ADK her gerçek sayıyı Python veri araçlarından almalıdır. Örneklerde yıl, büyüklük ve mesafe filtreleri **sol panelden** seçilir; aynı il birden çok olayla eşleşebilir.

| Soru | Temel Python aracı | Hemen kullanılır mı? |
|---|---|---|
| Balıkesir'in gözlenen deprem puanı neden yüksek? | `deprem_puani_neden_yuksek` | Evet, paketli 2025 verisi |
| 2025'te deprem eşleşmesi en çok olan on il hangileri? | `deprem_illerini_sirala` | Evet |
| Ankara'nın deprem olay puanı İstanbul'dan yüksek mi? | `il_karsilastir` | Evet |
| Türkiye geneli depremler hangi aylarda yoğunlaşmış? | `deprem_aylik_dagilim` | Evet |
| Seçili dönemde yıllara göre kaç deprem var? | `deprem_yillik_dagilim` | Evet |
| M6 ve üzeri kaç deprem var? | `deprem_buyukluk_dagilimi` | Evet |
| Balıkesir'de M5 üzeri en büyük olaylar neler? | `deprem_olay_kayitlari` | Evet |
| En büyük 10 USGS olayını tarihlerle göster. | `buyuklugune_gore_en_onemli_depremler` | Evet |
| Hangi afetlerin gerçek il verisi hazır? | `afet_veri_durumu` | Evet |
| Yeme-içme modelinin ağırlıkları ve eksikleri neler? | `sektor_modeli_ve_gostergeler` | Evet |
| Ankara ve İzmir nüfus olarak kıyaslanabilir mi? | `iki_ili_nufusa_gore_karsilastir` | **973 ilçe 2025 CSV gerekir** |
| Türkiye'deki nüfusu en fazla ilk 20 ilçe hangileri? | `ilceleri_nufusa_gore_sirala` | CSV gerekir |
| Ankara'nın en kalabalık ilçeleri hangileri? | `ilceleri_nufusa_gore_sirala` | CSV gerekir |
| Çankaya ile Yenimahalle'yi hizmet sektöründe karşılaştır. | `iki_ilceyi_karsilastir` | CSV gerekir |
| Ankara'da dört sektörün birincileri aynı mı? | `sektorlerin_birincilerini_karsilastir` | CSV gerekir |
| Neden bu ilçe yeme-içmede birinci? | `neden_bu_ilce_birinci` | CSV gerekir |
| Ankara'da sakin yaşam tercihinde neden bu ilçe birinci? | `yasamda_neden_bu_ilce_birinci` | CSV gerekir |
| Türkiye'nin en gelişmiş SEGE ilçeleri hangileri? | `sege_en_gelismis_ilceler` | **973 ilçe SEGE eşleşmesi** gerekir |

## Gösterilmemesi gereken sahte kesinlik

- *Gerçek restoran kârlılığı* ve *günlük yaya trafiği* için yeterli veri yok. Ajan modelinin nüfus temelli sıralamasını bu veriler varmış gibi yorumlamamalı.
- *En güvenli il*, bütün afetlere ait bilimsel güvenlik olasılığı değildir. Yalnızca seçilen USGS kaydıyla deprem hareketliliği sıralaması üretilebilir.
- Model canlı `gemini` bağlantısı olmadan API yanıt testi yapılmış sayılmaz. Python araçlarına ait otomatik testler ayrıdır.
