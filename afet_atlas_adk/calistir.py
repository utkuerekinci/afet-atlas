"""Afet Atlas Streamlit ekranından ADK Runner ile soru çalıştırma.

Ayrıntılı çalışma, ADK tool-call izini döndürür. Bu, ajanın sayıları gerçekten
Python veri araçlarından alıp almadığını gözlemlemeyi kolaylaştırır.
"""
from __future__ import annotations

import asyncio
import os

from atlas_gemini_dayaniklilik import guvenli_uret_async


def ajana_sor(soru: str, iller, depremler, eslesenler,
              yil_bas: int, yil_son: int, min_buyukluk: float, mesafe_km: int, ilce_df=None) -> str:
    """Eski çağrılar için geriye uyumlu, yalnızca yanıt metnini döndürür."""
    return ajana_sor_ayrintili(soru, iller, depremler, eslesenler,
                              yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df)["cevap"]


def ajana_sor_ayrintili(soru: str, iller, depremler, eslesenler,
                        yil_bas: int, yil_son: int, min_buyukluk: float, mesafe_km: int, ilce_df=None) -> dict:
    """Yanıtı, kullanılan ADK araçlarını ve araç çağrısı adedini döndürür."""
    if not soru.strip():
        raise ValueError("Sorun boş olamaz.")
    return asyncio.run(_calistir(soru, iller, depremler, eslesenler,
                               yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df))


async def _calistir(soru, iller, depremler, eslesenler,
                   yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df) -> dict:
    async def run_one(model: str):
        return await _calistir_tek_model(soru, iller, depremler, eslesenler,
                                        yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df, model)

    return await guvenli_uret_async(run_one, os.environ.get('AFET_ATLAS_MODEL', 'gemini-3.5-flash-lite'))


async def _calistir_tek_model(soru, iller, depremler, eslesenler,
                             yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df, model: str) -> dict:
    from google.adk.apps import App
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from .agent import ajan_olustur

    ajan = ajan_olustur(iller, depremler, eslesenler,
                       yil_bas, yil_son, min_buyukluk, mesafe_km, ilce_df, model=model)
    uygulama = App(name="afet_atlas_streamlit", root_agent=ajan)
    oturum_servisi = InMemorySessionService()
    kullanici = "yerel_kullanici"
    oturum = await oturum_servisi.create_session(app_name=uygulama.name, user_id=kullanici)
    calistirici = Runner(app=uygulama, session_service=oturum_servisi)

    yanit = ""
    cagri_kayitlari = []
    try:
        async for olay in calistirici.run_async(
                user_id=kullanici,
                session_id=oturum.id,
                new_message=types.Content(role="user", parts=[types.Part(text=soru)])):
            parcalar = olay.content.parts if olay.content and olay.content.parts else []
            for parca in parcalar:
                fonksiyon = getattr(parca, "function_call", None)
                if fonksiyon:
                    cagri_kayitlari.append({
                        "arac": str(fonksiyon.name),
                        "parametreler": dict(fonksiyon.args or {}),
                    })
            if olay.is_final_response() and parcalar:
                metinler = [bolum.text for bolum in parcalar if bolum.text]
                if metinler:
                    yanit = "\n".join(metinler).strip()
    finally:
        pass

    return {
        "cevap": yanit or "ADK ajanı kullanılabilir bir yanıt üretmedi.",
        "arac_cagrilari": cagri_kayitlari,
        "arac_sayisi": len(cagri_kayitlari),
    }
