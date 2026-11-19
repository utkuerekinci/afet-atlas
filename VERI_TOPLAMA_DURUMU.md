> **v3.5.4 güncellemesi:** Önceki sürümlerdeki nüfus–SEGE eşleşme eksikliği çözüldü. 973/973 ilçe ve 81 il tam eşleşiyor. Paket gerçek nüfus, SEGE ve birleşik CSV dosyalarını içeriyor. Ayrıntılar için `ESLESME_DUZELTMESI.md` belgesine bakın. Aşağıdaki eski sürüm notları tarihsel bilgi olarak korunmuştur.

# Afet Atlas — veri toplama durumu (v3.5.3)

| Kaynak | Durum | Kontrol |
|---|---|---|
| Deprem, USGS 2025 | Kullanıma hazır | Eski hesaplamalar ve testler korundu |
| İlçe SEGE-2022 | **CSV eklendi** | Resmî 71 sayfalık PDF'nin Ek-1 ve Ek-2 tablolarının 973 kaydı birebir eşleşti; 81 il, 0 çelişki |
| 2025 ilçe nüfusu | ZIP'e dahil değil; kullanıcının bilgisayarında indirildi | 81 il, 973 ilçe ve 86.092.168 kişi toplamı önceki kontrolü geçti; PDF-SEGE ad eşleşmesi ayrıca çalıştırılacak |
| OGM 2024–2025 yangınları | Resmî Excel ile son karşılaştırma bekleniyor | Aday ikincil CSV kesin kaynak olarak kullanılmıyor |
| Sel, çığ, heyelan, fırtına, kuraklık | İl bazlı sayısal entegrasyon eksik | Çevrim içi rapor bulmak verinin sayısal sisteme alındığını kanıtlamaz |
| Ticari işletmeler | Sektörel veri entegrasyonu eksik | Model puanı doğrulanmış işletme sayısı değildir |

## SEGE kontrolü

Ham PDF SHA256: `5c99314d7a10558f9f607f1fe4c4135148b887a232e79984b4540a213d9ede8f`

- Ek-1: PDF sayfa 42–49, 973 kayıt.
- Ek-2: PDF sayfa 49–70, 973 kayıt.
- Sıra, il, ilçe, skor: 973/973, çelişki sıfır.
- Kademe dağılımı: 67, 173, 175, 215, 222, 121.

Nüfusla yerel eşleşme için: `python kontrol_sege_nufus.py`
Orijinal PDF'den yeniden oluşturma için: `python kaynaklari_topla.py --sege`

Ham PDF ZIP'e dahil değildir; kullanıcı bilgisayarında daha önce indirilen dosya korunmalıdır. SEGE kaydı 2022 yılına aittir; 2025 güncel yaşam kalitesini tek başına göstermez.
