# Afet Atlas v3.9 — Yorum Odaklı Ekranlar

## Güncelleme

- Ticaret ve yaşam modüllerindeki açıklamalar, birbiri ardına gelen veri/sınırlama cümlelerinden çıkarıldı.
- "Neden Bu İlçe Birinci?" bölümü, sektöre/yerleşim tercihine uygun gerekçe, ikinci ilçe ile güçlü-zayıf yön karşılaştırması ve somut öneri üretir.
- Tekrarlanan uyarı/etiketler ana ekrandan kaldırıldı; sayısal puan katkıları varsayılan olarak kapalı "Karşılaştırmanın sayısal ayrıntıları" bölümüne taşındı.
- Yaşam sıralaması artık yalnız nüfus ve yoğunluktan oluşmuyor: **yaşam ritmi %60 + SEGE-2022 %30 + OSM ulaşım %10**. Eksik kaynak varsa mevcut bileşenlerin ağırlıkları yeniden normalize edilir. SEGE-2022 araştırması 56 değişkenle eğitim, sağlık, istihdam ve yaşam koşullarını da değerlendiren bütünleşik bir göstergedir.
- Lojistik sektöründe seyrek OSM etiketleri zorla rekabet sayısına dönüştürülmez; işletme modeli ve konum seçimi için yorum yapılır.
- ADK talimatları sayı saymak yerine özgün gerekçe ve uygulanabilir öneri sunacak şekilde güncellendi.
- İşletme/ulaşım, nüfus ve SEGE veri dosyaları projede duruyor. 623 MB OSM kaynağını tekrar indirmeye veya işlemeye gerek yok.

## Kullanım

1. ZIP'i ayıkla ve klasörü VS Code'da aç.
2. İlk kullanımda `python -m pip install -r requirements.txt` komutunu çalıştır.
3. `python -m streamlit run app.py` ile aç.
4. Ticaret ve Yaşam Kalitesi sayfalarında il, sektör veya yaşam tercihini değiştir. "Neden Bu İlçe Birinci?" bölümünde yorum doğrudan görünür; istersen altındaki sayısal ayrıntıları aç.
5. Canlıya almak için bu klasörün içeriğiyle GitHub deposundaki uygulama dosyalarını güncelle; mevcut Vercel projesinin dağıtımı depodaki ayarına göre gerçekleşir.

## Metodoloji özeti

İlçe SEGE 2022, 973 ilçeyi 56 değişkenle değerlendiren bir bileşik gelişmişlik araştırmasıdır. Uygulama bu bileşik sonuçla yaşam profiline dair genel bir bağlam kurar; bağımsız asayiş, hastane memnuniyeti veya okul kalite verisi varmış gibi yeni rakam üretmez. Ticaret yorumu da gözlenen işletme kümelenmesini ve talep/rekabet arasındaki olası ilişkiyi yorumlar. Kaynak bağlantıları "Veri ve yöntem" sayfasında ve ilgili bölümlerde bulunur.

## Sürüm testi

`python -m unittest discover -p 'test_*.py' -q`
