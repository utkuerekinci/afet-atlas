"""Afet Atlas | Türkiye ilçe nüfusu ve SEGE verisi.

Sadece doğrulanmış değerler gösterilir. Hiçbir kayıt tahminle doldurulmaz.
"""
from __future__ import annotations

from io import BytesIO
import os
import json
from pathlib import Path
import re
import unicodedata

import pandas as pd
import requests

BASE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('AFET_ATLAS_DATA_DIR') or (BASE / 'indirilen_veriler'))
POP_LOCAL = DATA_DIR / "ilce_nufus_2025.csv"
SEGE_LOCAL = DATA_DIR / "ilce_sege_2022.csv"
POP_URL = "https://raw.githubusercontent.com/topografya/veri/yayin/nufus/gostergeler.json"
POP_RAW = DATA_DIR / "ham_kaynaklar" / "topografya_gostergeler.json"
SEGE_URL = "https://www.sanayi.gov.tr/assets/pdf/birimler/2022-ilce-sege.pdf"
OFFICIAL_TR_POP_2025 = 86092168  # TÜİK ADNKS 2025, 31 Aralık 2025


def normalize_name(value: str) -> str:
    s = unicodedata.normalize("NFKD", str(value).strip().translate(str.maketrans("İIı", "iii")))
    s = "".join(x for x in s if not unicodedata.combining(x))
    s = s.lower().replace("ı", "i")
    return re.sub(r"[^a-z0-9]", "", s)


def read_population_bytes(contents: bytes) -> pd.DataFrame:
    """2025 CSV'sindeki 973 ilçeyi doğrula. Başka yılları bu sütunda göstermeyiz."""
    df = pd.read_csv(BytesIO(contents), encoding="utf-8-sig")
    df.columns = [str(c).lstrip("\ufeff").strip().lower() for c in df.columns]
    need = {"il", "ilce", "nufus"}
    if not need.issubset(df.columns):
        raise ValueError("Nüfus CSV sütunları beklenenden farklı: " + repr(list(df.columns)))
    df["il"] = df["il"].astype(str).str.strip()
    df["ilce"] = df["ilce"].astype(str).str.strip()
    df["nufus"] = pd.to_numeric(df["nufus"], errors="raise")
    if len(df) != 973 or df["il"].nunique() != 81 or (df["nufus"] <= 0).any():
        raise ValueError("2025 nüfus verisinde 973 ilçe / 81 il / pozitif nüfus doğrulaması başarısız.")
    keys = [normalize_name(i) + ":" + normalize_name(j) for i, j in zip(df.il, df.ilce)]
    if len(set(keys)) != 973:
        raise ValueError("İl-ilçe isimlerinde tekrar var; eşleştirme yapılamıyor.")
    df["anahtar"] = keys
    if "nufus_yogunlugu_km2" in df.columns:
        df["nufus_yogunlugu_km2"] = pd.to_numeric(df["nufus_yogunlugu_km2"], errors="coerce")
    else:
        df["nufus_yogunlugu_km2"] = float("nan")
    cols = ["il", "ilce", "anahtar", "nufus", "nufus_yogunlugu_km2"]
    return df[cols].copy()


def read_topografya_population_bytes(contents: bytes) -> pd.DataFrame:
    """Topografya yayını (TÜİK T22) -> 2025 ilçe CSV şeması.

    Kaynağın 81 il, 973 ilçe, her ilde ilçe toplamı ve ülke toplamı
    sınamaları geçmeden tek satır bile kullanıma alınmaz.
    """
    try:
        payload = json.loads(contents)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Topografya yanıtı geçerli JSON değil.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Topografya JSON nesnesi bekleniyor.")
    if payload.get("kaynak", {}).get("kurum") != "Türkiye İstatistik Kurumu (TÜİK)":
        raise ValueError("Topografya kaynak bildirimi TÜİK değil.")
    if payload.get("ilce_yillari") != [2024, 2025]:
        raise ValueError("İlçe veri yılları 2024 ve 2025 değil; şema değişmiş olabilir.")
    years = payload.get("yillar", [])
    if 2025 not in years:
        raise ValueError("Ülke/il nüfus serisinde 2025 bulunmuyor.")
    idx = years.index(2025)
    districts = []
    provinces = payload.get("iller", [])
    if not isinstance(provinces, list) or len(provinces) != 81:
        raise ValueError("Topografya 81 il içermiyor.")
    for province in provinces:
        name = province.get("ad")
        data = province.get("ilceler", [])
        series = province.get("nufus", [])
        if not isinstance(name, str) or not name.strip() or not isinstance(data, list):
            raise ValueError("İl adı veya ilçe listesi geçersiz.")
        if len(series) <= idx:
            raise ValueError(f"{name} için 2025 il nüfusu eksik.")
        province_total = 0
        for district in data:
            if not isinstance(district, dict) or not isinstance(district.get("ad"), str):
                raise ValueError(f"{name} için ilçe bilgisi geçersiz.")
            values = district.get("n")
            if not isinstance(values, list) or len(values) != 2:
                raise ValueError(f"{name} / {district['ad']} için nüfus serisi eksik.")
            n = values[1]
            if type(n) is not int or n <= 0:
                raise ValueError(f"{name} / {district['ad']} için 2025 nüfusu geçersiz.")
            area = district.get("alan_km2")
            density = (n / float(area)) if isinstance(area, (int, float)) and area > 0 else float("nan")
            districts.append({"il": name.strip(), "ilce": district["ad"].strip(),
                              "nufus": n, "nufus_yogunlugu_km2": density})
            province_total += n
        if province_total != series[idx]:
            raise ValueError(f"{name} ilindeki ilçeler toplamı {province_total:,}; il verisi {series[idx]:,}. Kullanılmadı.")
    frame = pd.DataFrame(districts)
    # Mevcut standart CSV doğrulayıcımızı da aynen uyguluyoruz.
    data = frame.to_csv(index=False).encode("utf-8-sig")
    verified = read_population_bytes(data)
    official_total = payload.get("tr", {}).get("nufus", [None] * (idx + 1))[idx]
    if official_total != OFFICIAL_TR_POP_2025:
        raise ValueError(f"JSON içindeki ulusal 2025 toplamı {official_total}; resmî toplamla uyuşmuyor.")
    _check_official_2025_total(verified)
    return verified


def fetch_population(force_refresh: bool = False) -> pd.DataFrame:
    """Doğrulanmış yerel CSV varsa kullan, yoksa TÜİK T22 tabanlı JSON'dan üret."""
    if POP_LOCAL.is_file() and not force_refresh:
        try:
            local = read_population_bytes(POP_LOCAL.read_bytes())
            _check_official_2025_total(local)
            return local
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError):
            pass
    if POP_RAW.is_file() and not force_refresh:
        try:
            df = read_topografya_population_bytes(POP_RAW.read_bytes())
            _save_population_csv(df)
            return df
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError):
            pass
    response = requests.get(POP_URL, timeout=(15, 90), headers={
        "User-Agent": "AfetAtlas-BBY261/3.5.1 (academic project)"})
    response.raise_for_status()
    df = read_topografya_population_bytes(response.content)
    # Kayıtları ancak son toplama kadar doğruysa diske yazarız.
    POP_RAW.parent.mkdir(parents=True, exist_ok=True)
    temp = POP_RAW.with_suffix(".json.pending")
    temp.write_bytes(response.content)
    temp.replace(POP_RAW)
    _save_population_csv(df)
    return df


def _save_population_csv(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    staging = POP_LOCAL.with_suffix(".csv.pending")
    df.drop(columns=["anahtar"]).to_csv(staging, index=False, encoding="utf-8-sig")
    staging.replace(POP_LOCAL)

def read_sege_csv(filepath: Path = SEGE_LOCAL) -> pd.DataFrame:
    """Yalnızca 973 benzersiz genel sıra içeren resmî rapor dönüşümü kabul edilir."""
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    required = {"il", "ilce", "sege_sira", "sege_skor", "sege_kademe"}
    if not required.issubset(df.columns):
        raise ValueError("SEGE dosyasında gerekli alanlar eksik.")
    for col in ("sege_sira", "sege_kademe"):
        df[col] = pd.to_numeric(df[col], errors="raise").astype(int)
    df["sege_skor"] = pd.to_numeric(df["sege_skor"].astype(str).str.replace(",", ".", regex=False), errors="raise")
    if len(df) != 973 or set(df.sege_sira) != set(range(1, 974)) or not df.sege_kademe.between(1, 6).all():
        raise ValueError("SEGE 973 ilçe, 1–973 sıra veya kademe kontrolünden geçmedi.")
    df["anahtar"] = [normalize_name(i) + ":" + normalize_name(j) for i, j in zip(df.il, df.ilce)]
    if df["anahtar"].duplicated().any() or df.il.nunique() != 81:
        raise ValueError("SEGE isimleri / il sayısı eşleşme testini geçmedi.")
    df["sege_ilce_adi"] = df["ilce"].astype(str).str.strip()
    return df[["anahtar", "sege_ilce_adi", "sege_sira", "sege_skor", "sege_kademe"]]



# Sadece kaynaklarda gözlenen ve aynı ilde tekil olarak doğrulanabilen ad farkları.
# Bulanık/fuzzy eşleşme YOK: eşleşmeyen kayıt varsa işlem durur.
ILCE_AD_ESANLAM = {("samsun", "19mayis"): "ondokuzmayis"}


def eslesme_anahtarlari(pop: pd.DataFrame, sege: pd.DataFrame) -> pd.DataFrame:
    """Nüfus adlarını SEGE anahtarlarına birebir, il sınırı içinde eşleştir.

    Yöntemler: doğrudan; baştaki il adını atma; açık 19 Mayıs karşılığı.
    Birden çok adaya, eksik kayda veya tekrar anahtara izin verilmez.
    """
    if len(pop) != 973 or len(sege) != 973:
        raise ValueError("Eşleştirme için iki kaynak da 973 kayıt içermeli.")
    target = set(sege["anahtar"])
    if len(target) != 973:
        raise ValueError("SEGE anahtarları tekil değil.")
    records = []
    for row in pop.itertuples(index=False):
        prov = normalize_name(row.il)
        district = normalize_name(row.ilce)
        original = f"{prov}:{district}"
        candidates = []
        if original in target:
            candidates.append((original, "doğrudan"))
        if district.startswith(prov) and len(district) > len(prov):
            stripped = f"{prov}:{district[len(prov):]}"
            if stripped in target:
                candidates.append((stripped, "il öneki çıkarıldı"))
        alias = ILCE_AD_ESANLAM.get((prov, district))
        if alias and f"{prov}:{alias}" in target:
            candidates.append((f"{prov}:{alias}", "belgelenmiş eş anlam"))
        if len(candidates) != 1:
            raise ValueError(f"{row.il}/{row.ilce} için {len(candidates)} kesin SEGE eşleşmesi: {candidates}.")
        records.append({"nufus_anahtar": original, "sege_anahtar": candidates[0][0],
                        "eslesme_yontemi": candidates[0][1]})
    mapping = pd.DataFrame(records)
    if mapping.nufus_anahtar.nunique() != 973 or mapping.sege_anahtar.nunique() != 973:
        raise ValueError("İlçeler arasında birden bire veya tekrarlı eşleşme var.")
    if set(mapping.sege_anahtar) != target:
        raise ValueError("SEGE'deki bazı ilçeler eşleşmeden kaldı.")
    return mapping


def combine(pop: pd.DataFrame, sege: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    """Tam 973/973 eşleşme; çıktıdaki ilçe adı SEGE'nin standart adıdır."""
    result = pop.copy()
    status = {"nufus": "2025 TÜİK kaynaklı", "sege": "Henüz yüklenmedi"}
    if sege is None:
        return result, status
    mapping = eslesme_anahtarlari(pop, sege)
    m = mapping.rename(columns={"nufus_anahtar": "anahtar"})
    joined = result.merge(m, on="anahtar", how="left", validate="one_to_one")
    sege_rename = sege.rename(columns={"anahtar": "sege_anahtar"})
    joined = joined.merge(sege_rename, on="sege_anahtar", how="left", validate="one_to_one")
    if len(joined) != 973 or int(joined.sege_sira.notna().sum()) != 973 or joined.sege_sira.nunique() != 973:
        raise ValueError("Nüfus–SEGE eşleşmesi 973/973 tamamlanmadı; veri kullanılmadı.")
    joined["ilce_nufus_kaynagi"] = joined["ilce"]
    joined["ilce"] = joined["sege_ilce_adi"]
    if any(normalize_name(p) != k.split(":", 1)[0]
           for p, k in zip(joined["il"], joined["sege_anahtar"])):
        raise ValueError("İl sınırı aşan SEGE eşleştirmesi saptandı.")
    status["sege"] = "2022 resmî SEGE, 973/973 eşleşti"
    return joined, status


def _check_official_2025_total(df: pd.DataFrame) -> None:
    """Üçüncü taraf ilçe aktarımını TÜİK 2025 ulusal toplamıyla karşılaştırır."""
    observed = int(df['nufus'].sum())
    if observed != OFFICIAL_TR_POP_2025:
        raise ValueError(
            f"İlçe nüfus toplamı {observed:,}, TÜİK ADNKS 2025 resmî toplamı "
            f"{OFFICIAL_TR_POP_2025:,} ile eşleşmedi. Veri kullanılmadı."
        )
