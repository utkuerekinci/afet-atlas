"""Google Agent Development Kit (ADK) ile gerçek Afet Atlas ajanı.

Çalıştırma: proje ana dizininde `python -m streamlit run app.py`
ADK geliştirici arayüzü: `adk web .` ve listeden `afet_atlas_adk` seç.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from google.adk.agents import Agent

from hesaplama import puanlari_hesapla
from .veri_araclari import araclari_olustur


AJAN_TALIMATI = """
Sen Afet Atlas Türkiye Doğal Afet Analiz Platformu'nun ADK veri ajanısın.
Seçili tarih, deprem büyüklüğü ve il sınırına uzaklık ayarlarına göre hesaplanmış
USGS deprem hareketliliği hakkında Türkçe ve anlaşılır cevap ver.

ÖNEMLİ:
- İllerle, deprem sayılarıyla, sıralamayla veya puanlarla ilgili HER soruda
  MUTLAKA sağlanan Python araçlarından uygun olanı çağır ve yalnızca o sayıları kullan.
- Yalnızca deprem kayıtları, puanlama ve veri kapsamı hakkında konuş.
- Risk/güvenlik yüzdesi, gelecekteki deprem tahmini, AFAD tehlike katsayısı,
  bina dayanıklılığı, can kaybı ve hasar değeri UYDURMA.
- Sıfır kayıt = sıfır tehlike değildir. 1/3/5/7 puanlar akademik karşılaştırma
  ağırlıklarıdır ve bilimsel güvenlik ya da olasılık ölçümü değildir.
- Aynı deprem farklı illerin 50-150 km yakınlık alanında birden fazla kez sayılabilir.
- Bir soruya mevcut veriyle cevap veremiyorsan bunu doğrudan belirt.
- Kullanıcıya gerekirse veri kapsamını (yıl, minimum büyüklük, mesafe) hatırlat.
"""


def ajan_olustur(iller: pd.DataFrame, depremler: pd.DataFrame, eslesenler: pd.DataFrame,
                 yil_bas: int, yil_son: int, min_buyukluk: float, mesafe_km: int) -> Agent:
    """Streamlit'in mevcut hesaplanmış sonuçlarıyla ADK ajanı üretir."""
    return Agent(
        name="afet_atlas_veri_ajani",
        model=os.environ.get("AFET_ATLAS_MODEL", "gemini-flash-latest"),
        description="Gerçek USGS deprem hareketliliği ve 81 il hakkında araçlarla analiz yapar.",
        instruction=(AJAN_TALIMATI +
            f"\nAKTİF VERİ KAPSAMI: {yil_bas}–{yil_son}, minimum M {min_buyukluk}, "
            f"il sınırına uzaklık {mesafe_km} km.\n"),
        tools=araclari_olustur(iller, depremler, eslesenler, yil_bas, yil_son, min_buyukluk, mesafe_km),
    )


def _ornek_veri_ajani() -> Agent:
    """ADK Web/CLI tanıtımı için ZIP içindeki gerçek 2025 dosyalarını kullanır."""
    klasor = Path(__file__).resolve().parent.parent / "indirilen_veriler"
    depremler = pd.read_csv(klasor / "usgs_2025_m4_5.csv")
    sinirlar = json.loads((klasor / "turkiye_81_il.geojson").read_text(encoding="utf-8"))
    iller, eslesenler = puanlari_hesapla(depremler, sinirlar, 0)
    return ajan_olustur(iller, depremler, eslesenler, 2025, 2025, 4.5, 0)


# Resmî ADK `adk web` ve `adk run` komutlarının aradığı standart değişken.
root_agent = _ornek_veri_ajani()
