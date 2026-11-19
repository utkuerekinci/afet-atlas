"""Hazır 973 ilçe dosyalarını doğrula, birleştir ve kaynak bazlı audit oluştur."""
from pathlib import Path
import json
from collections import Counter
import pandas as pd
from ilce_veri import DATA_DIR, POP_LOCAL, SEGE_LOCAL, read_population_bytes, read_sege_csv, combine, OFFICIAL_TR_POP_2025


def main():
    if not POP_LOCAL.exists() or not SEGE_LOCAL.exists():
        raise SystemExit("Nüfus veya SEGE CSV mevcut değil. Hazır paket içeriğini kontrol edin.")
    pop = read_population_bytes(POP_LOCAL.read_bytes())
    if int(pop.nufus.sum()) != OFFICIAL_TR_POP_2025:
        raise SystemExit("Nüfus toplamı TÜİK 2025 toplamıyla uyuşmuyor.")
    sege = read_sege_csv(SEGE_LOCAL)
    merged, status = combine(pop, sege)
    if (len(merged)!=973 or merged.il.nunique()!=81 or
        set(merged.sege_sira.astype(int)) != set(range(1,974)) or
        int(merged.nufus.sum()) != OFFICIAL_TR_POP_2025):
        raise SystemExit("Son doğrulama başarısız, dosya yazılmadı.")
    out = DATA_DIR / "ilce_nufus_2025_sege_2022_BIRLESIK.csv"
    audit = DATA_DIR / "sege_nufus_eslesme_denetimi.csv"
    source = merged[["il", "ilce", "ilce_nufus_kaynagi", "nufus", "nufus_yogunlugu_km2",
                     "sege_sira", "sege_skor", "sege_kademe", "eslesme_yontemi"]].copy()
    source["nufus_yili"] = 2025
    source["sege_yili"] = 2022
    source.to_csv(out, index=False, encoding="utf-8-sig", float_format="%.6f")
    trace = merged[["il", "ilce_nufus_kaynagi", "ilce", "anahtar", "sege_anahtar", "eslesme_yontemi", "sege_sira"]].copy()
    trace.to_csv(audit, index=False, encoding="utf-8-sig")
    counts = dict(Counter(trace.eslesme_yontemi))
    report = {"nufus_ilce": len(pop), "sege_ilce":len(sege), "eslesen":len(merged),
              "il": merged.il.nunique(), "toplam_nufus":int(merged.nufus.sum()),
              "eslesme_yontemleri": counts,
              "veri_yillari":{"nufus":2025,"sege":2022},
              "kaynaklar":{"nufus":"TÜİK ADNKS 2025 kaynaklı Topografya aktarımı",
                          "sege":"T.C. Sanayi ve Teknoloji Bakanlığı İlçe SEGE-2022; Ek-1 ve Ek-2 çapraz doğrulama"},
              "dogrulama_limiti":"Tüm ilçelerin nüfus rakamları ayrı TÜİK tablosuyla satır satır çapraz kontrol edilmedi."}
    (DATA_DIR/"eslesme_sonuc.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("OK: 973/973 ilçe, 81 il; nüfus toplamı 86.092.168, SEGE 1-973 tam.")
    print("Eşleşme yöntemleri:",counts)
    print("Dosyalar:",out,audit,sep="\n  ")
    return merged

if __name__=='__main__': main()
