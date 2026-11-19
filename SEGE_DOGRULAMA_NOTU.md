# Afet Atlas — SEGE-2022 gerçek PDF düzeltme paketi

## Sonuç

Gönüllü olarak yüklenen **orijinal SEGE-2022 resmî PDF dosyası** (23.324.420 bayt) doğrudan incelendi.

- Ek-1 (Türkiye sıralaması, PDF fiziksel sayfa **42–49**): **973** sıra çıkarıldı.
- Ek-2 (81 ilin ayrı tabloları, PDF fiziksel sayfa **49–70**): **973** sıra çıkarıldı.
- Her iki ek arasında sıra, il, ilçe ve SEGE puanlarında **0 uyuşmazlık**.
- İl içindeki sıra ve kademe bilgileri de denetlendi.
- 81 il, 973 ayrı sıra ve 973 ayrı il/ilçe anahtarı doğrulandı.
- Artvin: **9/9**, Hakkari: **5/5**.
- Kademe dağılımları: **67 / 173 / 175 / 215 / 222 / 121**.
- PDF SHA-256: `5c99314d7a10558f9f607f1fe4c4135148b887a232e79984b4540a213d9ede8f`.

**Önemli:** Bu işlem, **SEGE PDF'si içindeki** iki bağımsız tablonun tam tutarlılığını gösterir. Kullanıcının bilgisayarındaki **2025 ilçe nüfus CSV'si ile 973/973 satır eşleşmesi** bu ortamda test edilemedi; bu kontrolü yerel komut çalıştıracaktır. SEGE skoru 2022'ye, nüfus verisi 2025'e aittir.

## Nereye kopyalanacak?

1. Projenin kökündeki `hazirla_ilce_verileri.py` dosyasını pakettekiyle **değiştir**.
2. Paket içindeki `indirilen_veriler/ilce_sege_2022.csv` dosyasını projedeki aynı klasöre **kopyala**.
3. `indirilen_veriler/sege_2022_dogrulama_denetcisi.csv` dosyasını da aynı klasöre kopyalayabilirsin; bu, orijinal PDF'de hangi sayfalardan okunduğunu gösteren denetim dosyasıdır.
4. Eskiden indirilen **`indirilen_veriler/ilce_nufus_2025.csv`** ve **`indirilen_veriler/ham_kaynaklar/ilce_sege_2022_kaynak.pdf`** dosyalarını silme.

İndirilen nüfus dosyasıyla doğrudan eşleşmeyi görmek için:

```powershell
python kontrol_sege_nufus.py
```

Uyumsuzluk varsa `indirilen_veriler/sege_nufus_eslesmeyenler.csv` oluşur; o dosyayı gönder, adları yalnızca doğrulanmış karşılıklarına göre düzeltebiliriz.

Yerel PDF'yi ve nüfus kaynağını beraber yeniden doğrulamak için:

```powershell
python kaynaklari_topla.py --sege
```

Ardından istersen testleri çalıştır:

```powershell
python -m unittest test_sege_ek1_ek2 -v
```

Başarılı sonuç: `OK sege_2022` ve `kaynak_durumu.json` içinde `973/973 doğrulanmış SEGE CSV üretildi`.

### Neden önceki çelişki oluşmuştu?

Eski ayrıştırıcı `sort=True` ile bütün sayfa metnini tek dizgeye çevirip düzenli ifadeyle arıyordu. `Ek-2` içindeki `Güdül 630 ... -0,493` satırını çevresindeki `Artvin` başlığından kaynaklanan metin kaymasıyla `4. sıra` zannedebiliyor ve `Kadıköy` ile çakıştırıyordu. Yeni ayrıştırıcı her iki eki **sayfa, yarım sayfa, metin bloğu ve sütun başlığı sınırlarında** ayrı okur. Sonra iki ekteki 973 kaydı sıra sıra karşılaştırır; çelişkide dosya üretmez.

### Dosyalar

- `hazirla_ilce_verileri.py`: Düzeltilmiş ve iki ekle karşılaştırmalı PDF ayrıştırıcı.
- `indirilen_veriler/ilce_sege_2022.csv`: Doğrulanmış 973 satırlık uygulama verisi.
- `indirilen_veriler/sege_2022_dogrulama_denetcisi.csv`: Kayıt başına Ek-1/Ek-2 PDF sayfaları ve il içi sıra.
- `test_sege_ek1_ek2.py`: Verinin bütünlük ve çelişki testleri.
- `kontrol_sege_nufus.py`: Gerçek 2025 nüfus dosyanla 973/973 eşleşmeyi denetler.

Kaynak: **T.C. Sanayi ve Teknoloji Bakanlığı, İlçelerin Sosyo-Ekonomik Gelişmişlik Sıralaması Araştırması, SEGE-2022**.
