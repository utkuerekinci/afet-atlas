"""ADK Function Tools: mevcut Afet Atlas hesaplama çıktısını sadece OKUR.

Puan, olay sayısı, konum veya tahmin bu modülde yeniden hesaplanmaz.
Kullanılan bütün sayılar hesaplama.py tarafından elde edilen tablolardan gelir.
"""
from __future__ import annotations

import unicodedata
from typing import Callable

import pandas as pd


def _il_anahtari(metin: str) -> str:
    metin = str(metin).strip().replace("ı", "i").replace("İ", "I")
    return "".join(
        k for k in unicodedata.normalize("NFKD", metin)
        if not unicodedata.combining(k)
    ).casefold()


def araclari_olustur(iller: pd.DataFrame, depremler: pd.DataFrame,
                    eslesenler: pd.DataFrame, yil_bas: int, yil_son: int,
                    min_buyukluk: float, mesafe_km: int) -> list[Callable]:
    """ADK Agent.tools için doğrudan Python fonksiyonları oluşturur."""
    kayitlar = iller.copy(deep=True)
    il_adlari = {_il_anahtari(ad): ad for ad in kayitlar["İl"].astype(str)}
    kapsam = {
        "tarih_araligi": f"{yil_bas}-{yil_son}",
        "minimum_buyukluk": float(min_buyukluk),
        "il_sinirina_yakinlik_km": int(mesafe_km),
    }

    def _bul(il_adi: str):
        ad = il_adlari.get(_il_anahtari(il_adi))
        return None if ad is None else kayitlar.loc[kayitlar["İl"] == ad].iloc[0]

    def _ozet(satir) -> dict:
        if satir is None:
            return {"hata": "İl bulunamadı. 81 ilden birini yazın."}
        adet = int(satir["Deprem sayısı"])
        endeks = satir["Karşılaştırma endeksi"]
        buyukluk = satir["En büyük deprem"]
        return {
            "il": str(satir["İl"]),
            "deprem_eslesmesi_sayisi": adet,
            "toplam_olay_puani": int(satir["Toplam puan"]),
            "en_buyuk_kayitli_deprem": None if pd.isna(buyukluk) else float(buyukluk),
            "goreli_endeks_100_uzerinden": None if pd.isna(endeks) else round(float(endeks), 2),
            "gozlem_durumu": "Eşleşen olay yok; güvenli anlamına gelmez" if adet == 0 else "Eşleşen kayıt var",
            "kapsam": kapsam,
        }

    def il_ozeti(il_adi: str) -> dict:
        """Belirtilen ilin kayıtlı deprem sayısını, olay puanını ve endeksini getirir.

        Args:
            il_adi: İncelenecek il adı, örnek Ankara ya da İstanbul.
        """
        return _ozet(_bul(il_adi))

    def il_karsilastir(il_1: str, il_2: str) -> dict:
        """İki ilin gözlenen deprem hareketliliğini kıyaslar.

        Args:
            il_1: Birinci il adı.
            il_2: İkinci il adı.
        """
        a, b = _ozet(_bul(il_1)), _ozet(_bul(il_2))
        if "hata" in a or "hata" in b:
            return {"hata": "Bir veya iki il bulunamadı", "birinci": a, "ikinci": b}
        return {"birinci": a, "ikinci": b,
                "uyari": "Daha düşük olay puanı daha güvenli bir il anlamına gelmez."}

    def hareketliligi_en_yuksek_iller() -> dict:
        """Olay puanı en yüksek ilk beş ili listeler."""
        sirali = kayitlar.sort_values(["Toplam puan", "İl"], ascending=[False, True])
        return {"iller": [_ozet(s) for _, s in sirali.head(5).iterrows()], "kapsam": kapsam}

    def hareketliligi_en_dusuk_kayitli_iller() -> dict:
        """Deprem eşleşmesi olan illerden en düşük puanlı beşini getirir."""
        pozitif = kayitlar[kayitlar["Deprem sayısı"] > 0]
        sirali = pozitif.sort_values(["Toplam puan", "İl"])
        return {
            "kaydi_olan_illerde_en_dusukler": [_ozet(s) for _, s in sirali.head(5).iterrows()],
            "sifir_eslesmeli_il_sayisi": int((kayitlar["Deprem sayısı"] == 0).sum()),
            "aciklama": "Sıfır kayıt sıfır tehlike veya %100 güvenlik değildir.",
            "kapsam": kapsam,
        }

    def veri_kapsami() -> dict:
        """USGS olay sayısını, il eşleşme sayısını ve veri kaynaklarını açıklar."""
        return {
            "kapsam": kapsam,
            "usgs_olay_sayisi": int(len(depremler)),
            "il_sayisi": int(len(kayitlar)),
            "il_olay_eslesme_sayisi": int(len(eslesenler)),
            "farkli_eslesen_olay_sayisi": int(eslesenler["USGS Olay ID"].nunique()) if len(eslesenler) else 0,
            "eslesme_olan_il_sayisi": int((kayitlar["Deprem sayısı"] > 0).sum()),
            "olay_agirliklari": {"4.5-4.9": 1, "5.0-5.9": 3, "6.0-6.9": 5, "7.0+": 7},
            "veri_kaynaklari": ["USGS Earthquake Catalog", "geoBoundaries TUR ADM1"],
            "uyari": "Bu veriler geçmiş hareketliliktir; gelecekteki risk veya güvenlik yüzdesi değildir.",
        }

    def ilin_en_buyuk_depremleri(il_adi: str, adet: int = 5) -> dict:
        """Bir ilde veya yakınlığında kayıtlı en büyük depremleri listeler.

        Args:
            il_adi: İncelenecek il adı.
            adet: Döndürülecek en fazla olay sayısı; 1-10 arası.
        """
        satir = _bul(il_adi)
        if satir is None:
            return {"hata": "İl bulunamadı."}
        if not 1 <= adet <= 10:
            return {"hata": "Adet 1 ile 10 arasında olmalıdır."}
        filtre = eslesenler.loc[eslesenler["İl"] == satir["İl"]]
        filtre = filtre.sort_values(["Büyüklük", "Tarih"], ascending=[False, False]).head(adet)
        olaylar = []
        for _, k in filtre.iterrows():
            olaylar.append({
                "tarih": str(k["Tarih"]), "buyukluk": float(k["Büyüklük"]),
                "usgs_olay_id": str(k["USGS Olay ID"]),
                "yer_aciklamasi": str(k["Yer"]),
                "il_sinirina_uzaklik_km": float(k["İl sınırına uzaklık (km)"]),
            })
        return {"il": str(satir["İl"]), "olaylar": olaylar, "kapsam": kapsam,
                "uyari": "Merkez üssü ilin sınırlarında veya seçili mesafede olabilir."}

    return [il_ozeti, il_karsilastir, hareketliligi_en_yuksek_iller,
            hareketliligi_en_dusuk_kayitli_iller, veri_kapsami,
            ilin_en_buyuk_depremleri]
