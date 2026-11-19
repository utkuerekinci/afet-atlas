> **v3.5.4 güncellemesi:** Önceki sürümlerdeki nüfus–SEGE eşleşme eksikliği çözüldü. 973/973 ilçe ve 81 il tam eşleşiyor. Paket gerçek nüfus, SEGE ve birleşik CSV dosyalarını içeriyor. Ayrıntılar için `ESLESME_DUZELTMESI.md` belgesine bakın. Aşağıdaki eski sürüm notları tarihsel bilgi olarak korunmuştur.

# v3.5.1 — Nüfus ve 404 hata düzeltmesi

## Hata nedenleri

1. Eski `turkiyeharitasi.site` CSV aktarımının 973 ilçesinin toplamı 86.080.727 olup resmî TÜİK ADNKS 2025 toplamı 86.092.168 değildir. 11.441 kişilik fark bulunduğundan veri reddedilmesi doğru davranıştı. Farkın nedenini resmî ilçe satırlarıyla kıyaslamadan kesin söyleyemeyiz.
2. `topografya/veri/main/nufus/gostergeler.json` bağlantısı 404 döner. JSON, `yayin` dalındadır.

## Çözüm

- Birincil veri kaynağı artık `https://raw.githubusercontent.com/topografya/veri/yayin/nufus/gostergeler.json`.
- JSON, TÜİK kaynak bildirimi ve yılları doğrulanarak içindeki 81 il ve 973 ilçe tablolarından işlenir.
- **Her ilin ilçe nüfusları toplamı o ilin nüfusuna eşit olmak zorunda.** Ayrıca bütün ilçelerin toplamı 86.092.168 olmalı; eşit değilse CSV kaydedilmez.
- Doğrulanırsa `indirilen_veriler/ham_kaynaklar/topografya_gostergeler.json` ve `indirilen_veriler/ilce_nufus_2025.csv` dosyaları oluşturulur.
- `--hepsi` sırasındaki demografi aşaması aynı, doğrulanmış JSON'u kullanır; yanlış URL veya gereksiz çift indirme olmaz.

## Senin bilgisayarında test

```powershell
python kaynaklari_topla.py --nufus --demografi
```

Ardından `indirilen_veriler/kaynak_durumu.json` içindeki `ilce_nufus_2025` ve `tuik_demografi_ikincil_aktarim` alanlarını kontrol et. Başarı durumunda `durum: indirildi` görünecek. İndirilemezse hata korunur; uydurma kayıt eklenmez.

**Bu ZIP içinde yeni indirilmiş nüfus CSV'si yok.** İnternet erişimi olan makinede komut çalıştırılmalıdır. SEGE PDF'sinin aktarımı ayrıca henüz doğrulanmış değildir.

Kaynaklar: TÜİK ADNKS 2025, Topografya yayın dalı ve üretim kodu, https://github.com/topografya/veri.
