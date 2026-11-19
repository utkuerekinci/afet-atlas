# Afet Atlas v3.5.4 — Nüfus + SEGE ilçe eşleşmesi

## Sorun ve çözüm

- Gerçek 2025 nüfus CSV dosyasında ilçe adı bazen il adını önek olarak taşıyor: `Ankara Gölbaşı` / SEGE: `Gölbaşı`.
- Samsun'daki `19 Mayıs` ilçesi SEGE-2022'de `Ondokuzmayıs` olarak yazılmış.
- Bu farklar **aynı il içinde, tekil ve deterministik** eşleştiriliyor; fuzzy tahmin yapılmıyor.
- 872 doğrudan + 100 il-öneki + 1 belgelenmiş ad karşılığı = **973/973**.
- Gerçek nüfus ve SEGE rakamları değiştirilmedi. Birleştirilmiş tabloda SEGE'deki standart ilçe adı gösteriliyor; özgün nüfus adı denetim dosyasında tutuluyor.

## Paket içeriği

`indirilen_veriler/ilce_nufus_2025.csv` — kullanıcı tarafından sağlanan gerçek 2025 nüfus CSV'si.

`indirilen_veriler/ilce_sege_2022.csv` — resmî PDF Ek-1 ve Ek-2 ile çapraz denetlenmiş 973 SEGE kaydı.

`indirilen_veriler/ilce_nufus_2025_sege_2022_BIRLESIK.csv` — 973 satır, 81 il, nüfus + SEGE.

`indirilen_veriler/sege_nufus_eslesme_denetimi.csv` — tüm eşleştirmelerin gerekçesi.

`indirilen_veriler/eslesme_sonuc.json` — makine tarafından doğrulanmış özet.

## Kullanım

Bu ZIP tam projedir; eski klasörün üzerine yazmak yerine kendi klasöründe açın.

```powershell
python kontrol_sege_nufus.py
python -m streamlit run app.py
```

SEGE 2022 yılı araştırmasıdır; nüfus 2025 yılındandır. SEGE puanları güncel 2025 gelişmişlik ölçümü olarak sunulmamalıdır.
