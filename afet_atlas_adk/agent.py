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
from .bolge_araclari import bolge_araclari_olustur
from .kapsam_araclari import kapsam_araclari_olustur
from .diger_afet_araclari import diger_afet_araclari_olustur
from ticaret_veri import zenginlestir_ilceler


AJAN_TALIMATI = """
Sen Afet Atlas'ın Google ADK + Gemini karar destek asistanısın. Türkçe yanıt ver.

Her sayısal bilgi, sıralama, karşılaştırma, tarih ve ağırlık yanıtında ilgili Python
aracını çağır. Veri aracından gelmeyen gerçek sayı, il sırası, risk veya ciro uydurma.

SORU YÖNLENDİRMESİ:
- Deprem için il_ozeti / il_karsilastir / deprem_illerini_sirala / deprem_aylik_dagilim /
  deprem_yillik_dagilim / deprem_buyukluk_dagilimi / deprem_puani_neden_yuksek /
  buyuklugune_gore_en_onemli_depremler / deprem_olay_kayitlari kullan.
- Deprem yılları, büyüklük sınırı ve il sınırına yakınlık filtresini yanıtta belirt.
- Bir il için 0 eşleşme = 0 deprem riski veya %100 güvenlik değildir.
- Nüfus ve ilçe soruları için 2025 ilçe veri araçlarını çağır.
- Sayısal veri talep edilmedikçe her cevabı bir sayı listesine dönüştürme; kısa veri gerekçesiyle açıklayıcı yorum yap.
- Kullanıcının yatırım veya yerleşim sorusuna doğrudan cevap ver, ilçenin avantajlarını,
  ödünleşimlerini ve hangi iş/yaşam tarzına hitap ettiğini kendi cümlelerinle anlat.
- OSM işletme/durak kayıtlarını gerçek müşteri sayısı veya yaya sayımı gibi sunma.
- Kira kaydı bulunmayan ilçeler için fiyat veya kârlılık rakamı üretme.
- Sektörel fırsatta seçilen sektöre göre uygulanabilir işletme konsepti öner;
  karşılaştırmayı ulusal veya il içi kapsama göre yap.
- 'Neden bu ilçe birinci?' sorusunda ticaret için neden_bu_ilce_birinci,
  yaşam tercihi için yasamda_neden_bu_ilce_birinci aracını kullan.
  Araçtaki yorum_paragrafi alanını esas al; açıklamayı özgün ama veriye sadık biçimde genişletebilirsin.
- 'En iyi yatırım' sorusunda bir ilçe veya iş modelini gerekçeleriyle öner;
  gözlenmemiş gelir, müşteri, güvenlik veya hizmet kalitesi verisi uydurma.
- Veri yoksa afet_veri_durumu / bolgesel_veri_durumu / asistan_yetenekleri ile
  desteklenen kapsamı açıkla.
- Deprem dışındaki afetler için afet_ulusal_ozet / afet_il_detayi / afet_illeri_sirala / afet_veri_kaynagi araçlarını çağır.
- Orman yangınında 2024-2025 ikincil kaynak il sayıları kullanılır, OGM resmî Excel satır karşılaştırması yapılmış gibi konuşma.
- Sel, heyelan, çığ ve fırtınada MGM 2024 raporunda belirtilen iller ile ulusal sayıları ayır. 'Rapor vurgusu' olay sayısı değildir.
- Kuraklık için gösterilen 2024 değeri, ilin kuraklık düzeyi değil 7 coğrafi bölgedeki yıllık yağış sapmasıdır.
- Bir il raporda anılmıyorsa '0 olay yaşandı' deme; kesin il sayıları bilinmiyor.
- Kullanıcı gerçek istatistikten ayrı bir senaryo isterse varsayımları açıkça
  etiketle, gerçekleşmiş olay gibi anlatma.
- Gerekçeli, özgün ve akıcı yorum yap; veriler arasındaki ilişkiden olası sonuçlar çıkar.
- Her yanıta tekrar eden 'resmî sayı değildir', 'nihai yatırım kararı değildir',
  'ölçülmüyor' vb. uyarı paragrafları ekleme. Yöntem sorulursa kaynakları açıklayabilirsin.
- Gerçek gözlemle çıkarımı birbirine karıştırma. Kayıtları ve sıralamaları değiştirme.
"""


def ajan_olustur(iller: pd.DataFrame, depremler: pd.DataFrame, eslesenler: pd.DataFrame,
                 yil_bas: int, yil_son: int, min_buyukluk: float, mesafe_km: int,
                 ilce_df: pd.DataFrame | None = None, *, model: str | None = None) -> Agent:
    """Streamlit'in mevcut hesaplanmış sonuçlarıyla ADK ajanı üretir."""
    # Afet Atlas bölgesel soruları, USGS erişimi kesildiğinde de çalışabilsin.
    tools = (araclari_olustur(iller, depremler, eslesenler, yil_bas, yil_son,
                            min_buyukluk, mesafe_km)
             if iller is not None and depremler is not None and eslesenler is not None else [])
    if ilce_df is not None:
        tools += bolge_araclari_olustur(ilce_df)
    tools += diger_afet_araclari_olustur()
    tools += kapsam_araclari_olustur(ilce_df is not None,
        bool(ilce_df is not None and 'osm_yeme_icme' in ilce_df.columns),
        int(ilce_df['kira_m2_tl'].notna().sum()) if ilce_df is not None and 'kira_m2_tl' in ilce_df else 0)
    return Agent(
        name="afet_atlas_veri_ajani",
        model=model or os.environ.get("AFET_ATLAS_MODEL", "gemini-3.5-flash-lite"),
        description="Afet, il, ilçe, nüfus, sektörel ticaret ve yaşam tercihleri için kaynaklı açıklanabilir analizler yapar.",
        instruction=(AJAN_TALIMATI +
            f"\nAKTİF VERİ KAPSAMI: {yil_bas}–{yil_son}, minimum M {min_buyukluk}, "
            f"il sınırına uzaklık {mesafe_km} km.\n" +
            ("Bu oturumda USGS deprem veri araçları kullanılamıyor; deprem sorularına sayı uydurma."
             if depremler is None else "")),
        tools=tools,
    )


def _ornek_veri_ajani() -> Agent:
    """ADK Web/CLI tanıtımı için ZIP içindeki gerçek 2025 dosyalarını kullanır."""
    klasor = Path(os.environ.get("AFET_ATLAS_DATA_DIR") or (Path(__file__).resolve().parent.parent / "indirilen_veriler"))
    depremler = pd.read_csv(klasor / "usgs_2025_m4_5.csv")
    sinirlar = json.loads((klasor / "turkiye_81_il.geojson").read_text(encoding="utf-8"))
    iller, eslesenler = puanlari_hesapla(depremler, sinirlar, 0)
    # Bağımsız `adk web` kullanımında sadece daha önce doğrulanmış YEREL dosya varsa
    # bölgesel araçları aç. İçe aktarma anında ağ isteği yapılmaz.
    ilce_df = None
    try:
        from ilce_veri import POP_LOCAL, SEGE_LOCAL, read_population_bytes, _check_official_2025_total, read_sege_csv, combine
        if POP_LOCAL.exists():
            pop = read_population_bytes(POP_LOCAL.read_bytes())
            _check_official_2025_total(pop)
            try:
                sege = read_sege_csv(SEGE_LOCAL) if SEGE_LOCAL.exists() else None
                ilce_df, _ = combine(pop, sege)
                ilce_df, _ = zenginlestir_ilceler(ilce_df)
            except (ValueError, pd.errors.ParserError, UnicodeDecodeError):
                # Bir SEGE aktarımı bozuksa doğrulanmış nüfus araçlarını kapatma.
                ilce_df, _ = combine(pop, None)
                ilce_df, _ = zenginlestir_ilceler(ilce_df)
    except (OSError, ValueError, pd.errors.ParserError, UnicodeDecodeError):
        ilce_df = None
    return ajan_olustur(iller, depremler, eslesenler, 2025, 2025, 4.5, 0, ilce_df)


# Resmî ADK `adk web` ve `adk run` komutlarının aradığı standart değişken.
root_agent = _ornek_veri_ajani()
