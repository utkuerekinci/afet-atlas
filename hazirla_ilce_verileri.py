"""Afet Atlas SEGE-2022: resmî PDF'nin iki ekini karşılaştırarak 973 ilçe çıkarır.

Ek-1: Türkiye genelindeki sıra, il, ilçe, puan.
Ek-2: İl bazında ilçe, genel sıra, il sırası, puan ve kademe.
Yalnızca iki ekteki 973 kayıt bütünüyle aynıysa CSV üretilir.

Kullanım (mevcut proje içinde):
    python kaynaklari_topla.py --sege
veya doğrudan:
    python hazirla_ilce_verileri.py --pdf indirilen_veriler/ham_kaynaklar/ilce_sege_2022_kaynak.pdf
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import re

import pandas as pd
import requests

from ilce_veri import (
    DATA_DIR, POP_LOCAL, SEGE_LOCAL, SEGE_URL,
    fetch_population, normalize_name, read_sege_csv, combine,
)

RANK_LIMITS = (67, 240, 415, 630, 852, 973)
GRADE_COUNTS = (67, 173, 175, 215, 222, 121)
ANCHORS = {
    1: ("İstanbul", "Şişli", 6.959),
    2: ("Ankara", "Çankaya", 6.901),
    4: ("İstanbul", "Kadıköy", 4.910),
    5: ("Ankara", "Yenimahalle", 4.481),
    11: ("İzmir", "Konak", 3.465),
    630: ("Ankara", "Güdül", -0.493),
    973: ("Şanlıurfa", "Harran", -1.447),
}
RANK_RE = re.compile(r"\d{1,3}\Z")
SCORE_RE = re.compile(r"-?\d{1,2},\d{3}\Z")
PROVINCE_HEADER_RE = re.compile(r"[A-ZÇĞİÖŞÜ ]+\Z")
MAIN_HEADER = "Sıra\nİl Adı\nİlçe Adı\nSkor\n"


def _read_ek1(document, start_page: int, end_page: int):
    """Yalnızca Ek-1 başlıklı sütunları, blok sınırlarını koruyarak ayrıştır."""
    rows = {}
    for pi in range(start_page, end_page + 1):
        page = document[pi]
        for block in page.get_text("blocks"):
            text = block[4]
            if not text.startswith(MAIN_HEADER):
                continue
            tokens = text[len(MAIN_HEADER):].strip().splitlines()
            if len(tokens) % 4:
                raise ValueError(f"Ek-1 PDF sayfa {pi+1}: dört sütunlu tablo bozuk.")
            for i in range(0, len(tokens), 4):
                sr, province, district, score = tokens[i:i+4]
                if not RANK_RE.fullmatch(sr) or not SCORE_RE.fullmatch(score):
                    raise ValueError(f"Ek-1 sayfa {pi+1}: tablo hücreleri bozuk: {tokens[i:i+4]!r}")
                rank = int(sr)
                if rank in rows:
                    raise ValueError(f"Ek-1: tekrarlanan Türkiye sırası {rank}.")
                rows[rank] = (province.strip(), district.strip(), float(score.replace(',', '.')), pi + 1)
    _ranks_complete(rows, "Ek-1")
    return rows


def _read_ek2(document, start_page: int, known_provinces: list[str]):
    """Ek-2'nin 81 il başlığı altındaki 5 sütunlu tablolarını ayrı oku.

    Sağ/sol sayfa yarılarını ayrı izler; başka bir ilin satırı önceki ile
    veya Ek-1'deki benzer sıra numarasıyla asla birleştirilmez.
    """
    by_key = {normalize_name(p): p for p in known_provinces}
    if len(by_key) != len(known_provinces):
        raise ValueError("Ek-1'de normalleştirilen il adları çakışıyor.")
    rows = {}
    headings = []
    for pi in range(start_page, len(document)):
        page = document[pi]
        mid = page.rect.width / 2
        blocks = page.get_text("blocks")
        for right_half in (False, True):
            ordered = sorted(
                (b for b in blocks if (b[0] >= mid) == right_half and b[1] < page.rect.height - 35),
                key=lambda b: (b[1], b[0])
            )
            province = None
            expecting_rows = False
            for block in ordered:
                text = block[4].strip()
                if not text:
                    continue
                if ('\n' not in text and len(text) <= 32 and
                        text == text.upper() and PROVINCE_HEADER_RE.fullmatch(text)):
                    key = normalize_name(text)
                    if key in by_key:
                        province = by_key[key]
                        headings.append((province, pi + 1))
                        expecting_rows = False
                        continue
                if "İlçe Adı" in text and "Genel Sıralama" in text and "Kademe" in text:
                    if province is None:
                        raise ValueError(f"Ek-2 sayfa {pi+1}: il başlığı olmadan tablo bulundu.")
                    expecting_rows = True
                    tokens = text.split("Kademe", 1)[1].strip().splitlines()
                elif expecting_rows:
                    tokens = text.splitlines()
                else:
                    continue
                if not tokens:
                    continue  # Sütun başlıkları başka, satırlar sonraki PDF bloğunda.
                if len(tokens) % 5:
                    raise ValueError(f"Ek-2 PDF sayfa {pi+1}, {province}: 5'li satırlar bozulmuş.")
                for i in range(0, len(tokens), 5):
                    district, sr, within, score, grade = tokens[i:i+5]
                    if not (RANK_RE.fullmatch(sr) and RANK_RE.fullmatch(within) and
                            SCORE_RE.fullmatch(score) and grade in {"1", "2", "3", "4", "5", "6"}):
                        raise ValueError(f"Ek-2 sayfa {pi+1}, {province}: geçersiz satır {tokens[i:i+5]!r}")
                    rank = int(sr)
                    if rank in rows:
                        raise ValueError(f"Ek-2: {rank}. Türkiye sırası birden fazla tabloda.")
                    rows[rank] = (
                        province, district.strip(), float(score.replace(',', '.')),
                        int(grade), int(within), pi + 1
                    )
                expecting_rows = False
    _ranks_complete(rows, "Ek-2")
    if len(headings) != 81 or len({p for p, _ in headings}) != 81:
        raise ValueError(f"Ek-2: 81 farklı il tablosu yerine {len(headings)} başlık okundu.")
    return rows


def _ranks_complete(rows: dict, label: str):
    ranks = set(rows)
    expected = set(range(1, 974))
    if ranks != expected:
        missing = sorted(expected-ranks)
        extra = sorted(ranks-expected)
        raise ValueError(f"{label}: {len(rows)}/973; eksik {missing[:20]}, fazla {extra[:20]}.")


def parse_sege_pdf(pdf_bytes: bytes, valid_provinces: list[str], return_audit: bool=False):
    """Doğrulanmış Ek-1 / Ek-2 eşleştirmesi; gerçeğe aykırı kayıt üretmez.

    return_audit=True çağrısında (sonuç_dataframe, denetim_dataframe) döner.
    Eski projenin parse_sege_pdf arayüzü korunmuştur.
    """
    import pymupdf  # 'fitz' uyarısını önler.
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    ek1 = [i for i, text in enumerate(pages) if "Ek-1: İlçelerin Sosyo-Ekonomik Gelişmişlik Sıralaması" in text]
    ek2 = [i for i, text in enumerate(pages) if "Ek-2: İlçelerin İl Bazında Sosyo-Ekonomik Gelişmişlik Sıralamaları" in text]
    if len(ek1) != 1 or len(ek2) != 1 or ek1[0] >= ek2[0]:
        raise ValueError("Resmî PDF Ek-1/Ek-2 başlıkları beklendiği gibi bulunmadı.")
    primary = _read_ek1(doc, ek1[0], ek2[0])
    provinces = {r[0] for r in primary.values()}
    if len(provinces) != 81:
        raise ValueError(f"Ek-1'de 81 il yerine {len(provinces)} il var.")
    appendix = _read_ek2(doc, ek2[0], sorted(provinces))
    norm_to_canonical = {normalize_name(p):p for p in valid_provinces}
    if len(norm_to_canonical) != 81:
        raise ValueError("Nüfus kaynağında 81 tekil il adı gerekir.")
    if set(norm_to_canonical) != {normalize_name(p) for p in provinces}:
        raise ValueError("SEGE ile nüfus kaynaklarının 81 il adı uyuşmuyor.")

    records = []
    audit = []
    province_groups = defaultdict(list)
    for rank in range(1,974):
        p, d, score, main_page = primary[rank]
        ap, ad, ascore, grade, localrank, appendix_page = appendix[rank]
        if (normalize_name(p) != normalize_name(ap) or
                normalize_name(d) != normalize_name(ad) or
                abs(score-ascore) > 0.0000001):
            raise ValueError(f"Ek-1 / Ek-2 çelişkili sıra {rank}: {(p,d,score)} <> {(ap,ad,ascore)}")
        expected_grade = next(j for j, rmax in enumerate(RANK_LIMITS,1) if rank <= rmax)
        if grade != expected_grade:
            raise ValueError(f"{rank}. sıradaki kademe tutarsız: PDF Ek-2={grade}, sınır={expected_grade}")
        province_groups[normalize_name(p)].append(localrank)
        official_name = norm_to_canonical[normalize_name(p)]
        records.append({"il": official_name, "ilce": d, "sege_sira": rank,
                        "sege_skor": score, "sege_kademe": grade})
        audit.append({"sege_sira":rank,"il":official_name,"ilce":d,"sege_skor":score,
                      "sege_kademe":grade,"il_ici_sira":localrank,
                      "pdf_ek1_sayfa":main_page,"pdf_ek2_sayfa":appendix_page})
    for prov, localranks in province_groups.items():
        expected = list(range(1, len(localranks)+1))
        if sorted(localranks) != expected:
            raise ValueError(f"{prov}: il içi sıralamada boşluk/tekrar var.")
    scores = [row["sege_skor"] for row in records]
    if any(scores[i] < scores[i+1] for i in range(len(scores)-1)):
        raise ValueError("SEGE puanları Türkiye sırasına göre azalmıyor.")
    if tuple(Counter(row["sege_kademe"] for row in records)[k] for k in range(1,7)) != GRADE_COUNTS:
        raise ValueError("SEGE kademe sayıları resmî tabloyla uyuşmuyor.")
    for rank,(ap,ad,val) in ANCHORS.items():
        row=records[rank-1]
        if normalize_name(row["il"])!=normalize_name(ap) or normalize_name(row["ilce"])!=normalize_name(ad) or abs(row["sege_skor"]-val)>0.000001:
            raise ValueError(f"{rank}. sıradaki referans kayıt uyuşmuyor: {row}")
    result=pd.DataFrame(records)
    if len({normalize_name(i)+":"+normalize_name(d) for i,d in zip(result.il,result.ilce)})!=973:
        raise ValueError("SEGE il/ilçe anahtarlarında çakışma tespit edildi.")
    audit_frame=pd.DataFrame(audit)
    return (result, audit_frame) if return_audit else result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sege",action="store_true", help="Resmî PDF'yi indirip iki ekini doğrula")
    ap.add_argument("--pdf", type=Path, help="Önceden indirilen yerel SEGE PDF'sini kullan")
    args=ap.parse_args()
    if not (args.sege or args.pdf):
        ap.error("--pdf DOSYA veya --sege parametresini kullanın")
    if args.pdf:
        pdf_bytes=args.pdf.read_bytes()
    else:
        response=requests.get(SEGE_URL,timeout=(15,120));response.raise_for_status()
        pdf_bytes=response.content
    pop=fetch_population()  # ÖNEMLİ: yerel nüfus varsa tekrar indirmez.
    sege,audit=parse_sege_pdf(pdf_bytes,pop.il.unique().tolist(),return_audit=True)
    DATA_DIR.mkdir(exist_ok=True)
    staging=SEGE_LOCAL.with_suffix(".partial.csv")
    sege.to_csv(staging,index=False,encoding="utf-8-sig",float_format="%.3f")
    try:
        verified=read_sege_csv(staging)
        combine(pop, verified)
        staging.replace(SEGE_LOCAL)
    finally:
        staging.unlink(missing_ok=True)
    audit.to_csv(DATA_DIR/"sege_2022_dogrulama_denetcisi.csv",index=False,encoding="utf-8-sig",float_format="%.3f")
    print(f"OK sege_2022: 973/973 Ek-1 ve Ek-2 eşleşti; nüfus ile 973 ilçe eşleşti. {SEGE_LOCAL}")


if __name__=="__main__":
    main()
