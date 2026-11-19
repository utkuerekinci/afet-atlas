# SEGE-2022 PDF ayrıştırma düzeltmesi (v3.5.2)

## Sorunun kaynağı

v3.5.1, 973 sıranın 968'ini okuyup şu beşini atlıyordu: 366, 542, 613, 746, 946. Beşinin tamamı Hakkari iline ait. Resmî SEGE 2022 raporunda bu il "Hakkari", demografi dosyasında ise "Hakkâri" gibi yazılabildiği için il adı düzenli ifadesi uyuşmuyordu.

Kaynak (resmî raporun kamu kurumundaki kopyası): https://geka.gov.tr/uploads/supports_v/sege-2022.pdf

| Ulusal sıra | İl | İlçe | Skor | Kademe |
|---:|---|---|---:|---:|
| 366 | Hakkari | Merkez | -0,077 | 3 |
| 542 | Hakkari | Çukurca | -0,386 | 4 |
| 613 | Hakkari | Yüksekova | -0,477 | 4 |
| 746 | Hakkari | Şemdinli | -0,633 | 5 |
| 946 | Hakkari | Derecik | -1,135 | 6 |

## Düzeltilenler

- `hazirla_ilce_verileri.py`: PDF il adlarında â/î/û farklılıklarını nüfus kaynağındaki kanonik il adına eşler. Örn. Hakkari => Hakkâri. Sayısal değer tahmini veya değişikliği yapılmaz.
- `hazirla_ilce_verileri.py`: `import fitz` yerine `import pymupdf` kullanılır.
- `kaynaklari_topla.py`: Yerelde bulunan SEGE PDF tekrar indirilmez, yeniden işlenir. Eksik dönüşüm durumunda `OK` yerine `EKSİK` mesajı gösterilir.
- Tamamı ayrıştırılmadıkça ve nüfus tablosuyla 973/973 eşleştirilmedikçe CSV üretimini engelleyen kontroller yerinde kalır.

## Kullanım

1. ZIP içindeki yalnızca `hazirla_ilce_verileri.py` ve `kaynaklari_topla.py` dosyalarını çalıştırmakta olduğunuz **v3.5.1 proje klasöründeki aynı isimli dosyaların üzerine** kopyalayın. `indirilen_veriler/` klasörünü **silmeyin**.
2. VS Code terminalinde bu proje klasöründeyken `python kaynaklari_topla.py --sege` çalıştırın.
3. `indirilen_veriler/kaynak_durumu.json` içinde `sonuc.donusum` alanı `973/973 doğrulanmış SEGE CSV üretildi` olmalıdır.
4. Dosya `indirilen_veriler/ilce_sege_2022.csv` oluşmalıdır. Eksik/hatalı çıktı olursa terminal metnini ve yeni `kaynak_durumu.json` dosyasını iletin.

Not: Düzeltme, kullanıcı bilgisayarındaki gerçek PDF üzerinde henüz test edilmedi. 973 kayıt için ayrıştırma algoritması sentetik PDF ile test edilmiştir; gerçek 973/973 işlemi ancak yerel PDF ile tamamlandığında doğrulanmış olur.
