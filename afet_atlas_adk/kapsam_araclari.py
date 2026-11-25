"""Tüm sorularda kullanılabilen kapsam ve sektör modeli açıklama araçları."""
from __future__ import annotations

from bolge_puanlari import SEKTOR_AGIRLIKLARI


def kapsam_araclari_olustur(ilce_verisi_var: bool, osm_aktif:bool=False, kira_kapsami:int=0):
    """Şimdiki uygulamanın gerçek veri durumunu veri tablosundan ayrı açıkla."""
    def afet_veri_durumu() -> dict:
        """Yedi afetin hangilerinde doğrulanmış il sayısal verisi bulunduğunu söyler."""
        return {
            "calisan_sayisal_afetler": ["Deprem: USGS il kayıt puanı", "Orman yangını: 2024–2025 ikincil aktarım il sayıları (OGM orijinal XLSX satır kontrolü eksik)"],
            "rapor_kayitli_afetler": ["Sel / taşkın: MGM 2024, ulusal toplam ve metinde belirtilen iller", "Heyelan: MGM 2024, ulusal toplam ve metinde belirtilen iller", "Çığ: MGM 2024, ulusal toplam ve sınıf aralıkları", "Fırtına: MGM 2024, ulusal toplam ve metinde belirtilen iller"],
            "bolgesel_iklim_gostergesi": ["Kuraklık başlığında 2024 yedi bölge yağış sapması (%); il SPI değeri değildir"],
            "henuz_sayisal_entegre_edilmeyen_afetler": ["Sel / taşkın, heyelan, çığ ve fırtına için 81 il kesin olay sayısı", "Kuraklık için 81 il SPI değeri"],
            "kaynak_adaylari": {"Orman yangını":"OGM il bazlı yıllık Excel tabloları",
                               "Sel/taşkın":"MGM meteorolojik afet raporları",
                               "Heyelan":"AFAD/MGM raporları",
                               "Çığ":"MGM yıllık meteorolojik afet raporları",
                               "Fırtına":"MGM veya metodolojisi açıklanmış meteorolojik ölçümler",
                               "Kuraklık":"MGM SPI veya açıkça tanımlanan iklim göstergeleri"},
            "kural":"Kaynağın ölçmediği il olay sayısını, SPI veya güvenlik yüzdesini üretme; rapor kanıtı ile kesin sayıyı ayır."}

    def sektor_modeli_ve_gostergeler(sektor: str = 'Yeme-içme') -> dict:
        """Ticaret sektörü için tasarlanan modeldeki ağırlıkları ve eksik gerçek değişkenleri açıklar.

        Args:
            sektor: 'Yeme-içme', 'Market / perakende', 'Hizmetler', 'Lojistik / depolama'.
        """
        if sektor not in SEKTOR_AGIRLIKLARI:return {'hata':'Desteklenmeyen sektör.'}
        return {'sektor':sektor,'tasarlanan_agirliklar':SEKTOR_AGIRLIKLARI[sektor],
                'osm_etiketli_isletme_sayilari_aktif':osm_aktif,
                'kira_kapsami_ilce':kira_kapsami,
                'gercek_olcum_olmayanlar':['Gerçek günlük yaya trafiği','Tüm kayıtlı rakip işletmeler','Gerçek müşteri sayısı','Ciro','Sektör bazlı harcama'],
                'yorum':'Eksik veri varsa hesaplama motoru mevcut gösterge ağırlıklarını yeniden ölçeklendirir. Bu yüzden farklı sektörler aynı ilçeyi önerebilir.'}

    def asistan_yetenekleri() -> dict:
        """ADK'nin şu anda yanıtlayabileceği sorularla eksik veri nedeniyle yanıtlayamayacaklarını açıklar."""
        return {'depremler':['İl karşılaştırma','İl sıralama','Aylık/yıllık kayıt dağılımı','Büyüklük sınıfları',
                             'En büyük kayıtlar','İl puanı gerekçesi','Veri kapsamı'],
                'bolgesel_araclar_aktif':ilce_verisi_var,
                'bolgesel_sorular':['İl/ilçe nüfusu','Türkiye geneli ve il içi sıralama','İlçe kıyaslama',
                                    'Dört sektörün fırsat puanları','Neden bu ilçe birinci?','Yaşam tercihi uyumu'] if ilce_verisi_var else [],
                'afet_sorgulari':['2024 ve 2025 orman yangını il sıralaması (ikincil ön veri)','2024 MGM sel/heyelan/çığ/fırtına ulusal toplamları ve vurgulu illeri','2024 coğrafi bölge yağış anomalisi'],
                'henuz_yapilamayanlar':['Gerçek ticaret ciro/kâr tahmini','Kapsamsız afet risk olasılıkları',
                                       'Gerçek yaya hareketliliği ve eksiksiz resmî işletme sayısı ölçümü'],
                'osm_verisi_aktif':osm_aktif,'kira_verisi_olan_ilce':kira_kapsami,
                'not':'Bölgesel araçlar ancak 973 ilçelik doğrulanmış nüfus dosyası yüklendiğinde etkinleşir.'}

    return [afet_veri_durumu, sektor_modeli_ve_gostergeler, asistan_yetenekleri]
