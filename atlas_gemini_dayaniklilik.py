"""Gemini 5xx yoğunluk hataları için sınırlı yeniden deneme ve model yedeği.

Kota, şifre veya yanlış istek hatalarını başka model ile gizlemez.
Anahtarlar bu modülde tutulmaz; istemciye ait veriler kaydedilmez.
"""
from __future__ import annotations

import asyncio
import os
import re
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar('T')
_TRANSIENT_CODES = {'500', '502', '503', '504'}


def gecici_hata(exc: Exception) -> bool:
    """Yalnızca API sunucu/kapasite hatalarında yeniden dene."""
    current = exc
    for _ in range(4):
        if current is None:
            break
        status = getattr(current, 'code', None) or getattr(current, 'status_code', None)
        try:
            if str(int(status)) in _TRANSIENT_CODES:
                return True
        except (TypeError, ValueError):
            pass
        message = str(current)
        if re.search(r'(?<!\d)(?:500|502|503|504)(?!\d)', message):
            return True
        # Google bazen sayısal kodu iç içe mesajlarda gizleyebilir.
        if 'UNAVAILABLE' in message.upper() and ('high demand' in message.lower() or 'overload' in message.lower()):
            return True
        current = current.__cause__ or current.__context__
    return False


def model_sirasi(primary: str) -> tuple[str, ...]:
    """Yapılandırılan modeli koru; 503 durumunda tek alternatif dene."""
    primary = str(primary or '').strip() or 'gemini-3.5-flash-lite'
    override = os.environ.get('AFET_ATLAS_YEDEK_MODEL', '').strip()
    fallback = override or ('gemini-3.8-flash' if primary == 'gemini-3.5-flash-lite'
                            else 'gemini-3.5-flash-lite')
    return (primary,) if fallback == primary else (primary, fallback)


def guvenli_uret(generate: Callable[[str], T], model: str, *, wait: Callable[[float], None] = time.sleep) -> T:
    """Birincil modelde bir kez yeniden dene; sürerse ikinci modele geç."""
    last_error = None
    for index, candidate in enumerate(model_sirasi(model)):
        count = 2 if index == 0 else 1
        for attempt in range(count):
            try:
                return generate(candidate)
            except Exception as exc:
                if not gecici_hata(exc):
                    raise
                last_error = exc
                if attempt + 1 < count:
                    wait(1.3)
    assert last_error is not None
    raise last_error


async def guvenli_uret_async(generate: Callable[[str], Awaitable[T]], model: str,
                             *, wait: Callable[[float], Awaitable[None]] = asyncio.sleep) -> T:
    """ADK Runner'ın bir seferlik oturumunu her denemede yeniden kur."""
    last_error = None
    for index, candidate in enumerate(model_sirasi(model)):
        count = 2 if index == 0 else 1
        for attempt in range(count):
            try:
                return await generate(candidate)
            except Exception as exc:
                if not gecici_hata(exc):
                    raise
                last_error = exc
                if attempt + 1 < count:
                    await wait(1.3)
    assert last_error is not None
    raise last_error
