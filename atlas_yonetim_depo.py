"""Afet Atlas v4.8: ayrı, özel GitHub veri reposu ve güvenli veri yayını.

Uygulama kodu reposuna hiçbir zaman yazılmaz. Yalnızca sunucu tarafı
Secrets içerisindeki dar kapsamlı token özel veri reposuna erişebilir.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading
import time
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
BUNDLED = ROOT / 'indirilen_veriler'
MAX_BYTES = 2_000_000
CONTROL_FILE = '.afet_atlas_kontrol.json'

# Mevcut motorun okuyabildiği şemalar dışında rastgele dosya yayınlanmaz.
DATASETS: dict[str, dict[str, Any]] = {
    'ilce_nufus_2025.csv': {'title':'İlçe nüfusu · 2025', 'group':'Yaşam', 'required':True},
    'ilce_sege_2022.csv': {'title':'İlçe SEGE · 2022', 'group':'Yaşam', 'required':True},
    'ticaret_osm_ilce.csv': {'title':'OSM işletme ve ulaşım kayıtları', 'group':'Ticaret', 'required':False},
    'ticaret_osm_manifest.json': {'title':'OSM kaynak ve tarih manifestosu', 'group':'Ticaret', 'required':False},
    'ticaret_kira_ilce.csv': {'title':'Ticari kira verileri (isteğe bağlı)', 'group':'Ticaret', 'required':False},
    'orman_yangini_2024_IKINCIL_KAYNAK.csv': {'title':'Orman yangını · 2024', 'group':'Afet', 'required':True},
    'orman_yangini_2025_IKINCIL_KAYNAK.csv': {'title':'Orman yangını · 2025', 'group':'Afet', 'required':True},
}

REPO_RE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
BRANCH_RE = re.compile(r'^[A-Za-z0-9._/-]{1,120}$')


class DataRepositoryError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    repo: str = ''
    token: str = ''
    branch: str = 'main'

    @property
    def enabled(self) -> bool:
        return bool(self.repo and self.token)


def settings_from_secrets(secrets: Any) -> Settings:
    """Eksik Secrets dosyasında uygulama her zamanki paket verisiyle açılır."""
    try:
        repo = str(secrets.get('AFET_ATLAS_VERI_REPOSU', '')).strip()
        token = str(secrets.get('AFET_ATLAS_VERI_TOKEN', '')).strip()
        branch = str(secrets.get('AFET_ATLAS_VERI_DALI', 'main')).strip() or 'main'
    except (FileNotFoundError, KeyError, TypeError, AttributeError):
        return Settings()
    if repo and not REPO_RE.fullmatch(repo):
        raise DataRepositoryError('Veri deposu OWNER/REPO biçiminde olmalı.')
    if not BRANCH_RE.fullmatch(branch) or '..' in branch or branch.startswith('/'):
        raise DataRepositoryError('Geçersiz veri deposu dalı.')
    return Settings(repo, token, branch)


class GitHubDataRepository:
    def __init__(self, settings: Settings, session: requests.Session | None = None):
        if not settings.enabled:
            raise DataRepositoryError('Veri deposu ve erişim anahtarı tanımlanmamış.')
        self.settings = settings
        self.session = session or requests.Session()
        self.api = 'https://api.github.com/repos/' + settings.repo
        self.headers = {
            'Authorization': 'Bearer ' + settings.token,
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'Afet-Atlas-Admin/4.8',
        }

    def _request(self, method: str, endpoint: str, **kwargs):
        if not endpoint.startswith('/') or '://' in endpoint:
            raise DataRepositoryError('Geçersiz GitHub API yolu.')
        try:
            resp = self.session.request(method, self.api + endpoint,
                                        headers=self.headers, timeout=(7, 25), **kwargs)
        except requests.RequestException as exc:
            raise DataRepositoryError('GitHub bağlantısı kurulamadı.') from exc
        if resp.status_code not in (200, 201):
            if resp.status_code in (401, 403):
                raise DataRepositoryError('GitHub erişim anahtarı veya depo yetkileri yetersiz.')
            if resp.status_code == 404:
                raise DataRepositoryError('Özel veri deposu / dosya bulunamadı. Depo adını ve izinlerini kontrol et.')
            if resp.status_code in (409, 422):
                raise DataRepositoryError('GitHub sürüm çatışması veya geçersiz işlem; sayfayı yenileyip tekrar dene.')
            raise DataRepositoryError(f'GitHub işlemi tamamlanamadı (HTTP {resp.status_code}).')
        return resp.json()

    def check_access(self):
        data = self._request('GET', '/')
        if data.get('full_name', '').casefold() != self.settings.repo.casefold():
            raise DataRepositoryError('GitHub deposu kimliği uyuşmuyor.')
        if not data.get('private', False):
            raise DataRepositoryError('Veri deposu PRIVATE olmalı. Veri yayınlanmadı.')
        return True

    def index(self) -> dict[str, str]:
        """Özel veri reposu içindeki izinli dosyaların ad/sha listesi."""
        try:
            data = self._request('GET', '/contents/indirilen_veriler',
                                 params={'ref':self.settings.branch})
        except DataRepositoryError as exc:
            if 'dosya bulunamadı' in str(exc):
                return {}  # Yeni açılan, henüz verisiz private repo.
            raise
        if not isinstance(data, list):
            raise DataRepositoryError('Veri klasörü beklenen biçimde değil.')
        return {x['name']:x['sha'] for x in data
                if x.get('type')=='file' and x.get('name') in DATASETS}

    def get(self, filename: str, ref: str | None = None) -> tuple[bytes, str]:
        if filename not in DATASETS:
            raise DataRepositoryError('Dosya yönetim listesinde değil.')
        params={'ref':ref or self.settings.branch}
        data = self._request('GET', '/contents/indirilen_veriler/' + filename, params=params)
        if data.get('type')!='file' or data.get('encoding')!='base64':
            raise DataRepositoryError('GitHub dosyası okunabilir base64 biçiminde değil.')
        try:
            raw=base64.b64decode(data['content'],validate=False)
        except (ValueError,KeyError) as exc:
            raise DataRepositoryError('GitHub dosya içeriği çözülemedi.') from exc
        if len(raw)>MAX_BYTES:
            raise DataRepositoryError('Veri dosyası en fazla 2 MB olabilir.')
        return raw,data['sha']

    def put(self, filename: str, data: bytes, message: str) -> str:
        if filename not in DATASETS or len(data)>MAX_BYTES:
            raise DataRepositoryError('Dosya tipi veya boyutu geçersiz.')
        try:
            existing_sha=self.get(filename)[1]
        except DataRepositoryError as exc:
            if 'dosya bulunamadı' in str(exc):
                existing_sha=None
            else:
                raise
        body={'message':message[:200], 'content':base64.b64encode(data).decode('ascii'),
              'branch':self.settings.branch}
        if existing_sha:
            body['sha']=existing_sha
        answer=self._request('PUT','/contents/indirilen_veriler/'+filename,json=body)
        return answer['commit']['sha']

    def _control(self) -> tuple[dict, str | None]:
        try:
            data=self._request('GET','/contents/'+CONTROL_FILE,
                               params={'ref':self.settings.branch})
        except DataRepositoryError as exc:
            if 'dosya bulunamadı' in str(exc):
                return {'disabled':[]},None
            raise
        try:
            decoded=base64.b64decode(data['content'])
            payload=json.loads(decoded.decode('utf-8-sig'))
            disabled=payload.get('disabled',[])
            if not isinstance(disabled,list) or any(s not in DATASETS for s in disabled):
                raise ValueError('Geçersiz içerik')
            return {'disabled':list(set(disabled))},data['sha']
        except (ValueError,KeyError,UnicodeDecodeError) as exc:
            raise DataRepositoryError('Veri deposu kontrol dosyası bozuk.') from exc

    def disabled(self) -> list[str]:
        return self._control()[0]['disabled']

    def set_disabled(self, filename: str, disable: bool) -> None:
        if filename not in DATASETS:
            raise DataRepositoryError('Bilinmeyen veri seti.')
        if DATASETS[filename]['required'] and disable:
            raise DataRepositoryError('Temel veri seti kapatılamaz; önceki sürümünü geri yükle.')
        current,sha=self._control()
        values=set(current['disabled'])
        # OSM sayım ve kaynak manifestosu birbirinden ayrı aktif tutulmaz.
        names={'ticaret_osm_ilce.csv','ticaret_osm_manifest.json'} if filename in (
            'ticaret_osm_ilce.csv','ticaret_osm_manifest.json') else {filename}
        if disable: values.update(names)
        else: values.difference_update(names)
        body={'message':('Afet Atlas: veri katmanı devre dışı: ' if disable else
                         'Afet Atlas: veri katmanı tekrar etkin: ')+filename,
              'branch':self.settings.branch,
              'content':base64.b64encode(json.dumps({'disabled':sorted(values)},
                   ensure_ascii=False,indent=2).encode('utf-8')).decode('ascii')}
        if sha:body['sha']=sha
        self._request('PUT','/contents/'+CONTROL_FILE,json=body)

    def commits(self, filename: str) -> list[dict]:
        if filename not in DATASETS:
            raise DataRepositoryError('Bilinmeyen dosya.')
        data=self._request('GET','/commits',params={'path':'indirilen_veriler/'+filename,
                                    'sha':self.settings.branch,'per_page':12})
        return [{'sha':item['sha'], 'date':item['commit']['committer']['date'],
                 'message':item['commit']['message'].splitlines()[0]}
                for item in data]


# Doğrulama uygulama motorunun mevcut alan kurallarını tekrar kullanır.
def validate_upload(filename: str, raw: bytes, root: Path | None = None) -> dict:
    if filename not in DATASETS:
        raise ValueError('Yalnızca listede bulunan veri setleri yüklenebilir.')
    if not raw or len(raw)>MAX_BYTES:
        raise ValueError('Dosya boş veya 2 MB sınırını aşıyor.')
    root=root or BUNDLED
    if filename.endswith('.json'):
        try: obj=json.loads(raw.decode('utf-8-sig'))
        except (ValueError,UnicodeDecodeError) as exc:raise ValueError('Geçersiz JSON dosyası.') from exc
        if not isinstance(obj,dict) or obj.get('kaynak')!='OpenStreetMap / Geofabrik' or obj.get('olcek')!='Türkiye 973 ilçe' or not obj.get('olusturma_tarihi'):
            raise ValueError('OSM kaynak manifestosunun kaynak, ölçek veya tarih bilgisi geçersiz.')
        return {'satir':1,'il':81,'ozet':'OSM kaynak metadatası doğrulandı.','preview':pd.DataFrame([obj])}
    try:
        frame=pd.read_csv(BytesIO(raw),encoding='utf-8-sig')
    except (ValueError,UnicodeDecodeError,pd.errors.ParserError) as exc:
        raise ValueError('CSV okunamadı; UTF-8 kodlaması ve sütun ayracını kontrol et.') from exc
    if frame.empty:
        raise ValueError('CSV tablosu boş.')
    from ilce_veri import read_population_bytes, _check_official_2025_total, read_sege_csv, eslesme_anahtarlari, normalize_name
    if filename=='ilce_nufus_2025.csv':
        cleaned=read_population_bytes(raw)
        _check_official_2025_total(cleaned)
        # Mevcut SEGE ile tam uyumunu doğrula.
        if (root/'ilce_sege_2022.csv').exists():
            sege=read_sege_csv(root/'ilce_sege_2022.csv')
            eslesme_anahtarlari(cleaned,sege)
        summary='81 il, 973 ilçe ve resmî 2025 ulusal toplam doğrulandı.'
    elif filename=='ilce_sege_2022.csv':
        # read_sege_csv dosya yolu beklediği için içerik geçici dosyada doğrulanır.
        with tempfile.TemporaryDirectory(prefix='atlas-check-') as temp:
            path=Path(temp)/filename
            path.write_bytes(raw)
            sege=read_sege_csv(path)
        base=read_population_bytes((root/'ilce_nufus_2025.csv').read_bytes())
        eslesme_anahtarlari(base,sege)
        summary='973 tekil SEGE sırası ve nüfus ile tam eşleşme doğrulandı.'
    elif filename=='ticaret_osm_ilce.csv':
        from ticaret_veri import OSM_SUTUNLAR, _aligned
        if len(frame)!=973 or not {'il','ilce',*OSM_SUTUNLAR}.issubset(frame.columns):
            raise ValueError('OSM kaydı 973 satır ve beklenen sektörel sütunlara sahip olmalı.')
        for col in OSM_SUTUNLAR:
            values=pd.to_numeric(frame[col],errors='raise')
            if values.isna().any() or (values<0).any() or not (values%1==0).all():
                raise ValueError(f'{col}: kayıt sayısı negatif, eksik veya ondalık olamaz.')
        active=(frame[OSM_SUTUNLAR].sum(axis=1)>0)
        if frame.loc[active,'il'].nunique()!=81:
            raise ValueError('81 ilin tamamında en az bir OSM etiketi gözlenmeli.')
        base=read_population_bytes((root/'ilce_nufus_2025.csv').read_bytes())
        _aligned(base,frame,require_full=True)
        summary='973 ilçe, 81 il, OSM sütunları ve ilçe eşleşmesi doğrulandı.'
    elif filename=='ticaret_kira_ilce.csv':
        from ticaret_veri import _aligned
        need={'il','ilce','kira_m2_tl','kaynak','tarih','ilan_adedi'}
        if not need.issubset(frame) or len(frame)>973:
            raise ValueError('Kira tablosunun zorunlu alanları eksik veya satır sayısı geçersiz.')
        for c in ['kira_m2_tl','ilan_adedi']:
            vals=pd.to_numeric(frame[c],errors='raise')
            if vals.isna().any() or (vals<=0).any():raise ValueError(c+' pozitif sayı olmalı.')
        if frame[['kaynak','tarih']].isna().any().any():raise ValueError('Kira kaynağı/tarihi eksik.')
        base=read_population_bytes((root/'ilce_nufus_2025.csv').read_bytes())
        _aligned(base,frame,require_full=False)
        summary=f'{len(frame)} ilçe için kaynaklı kira kaydı doğrulandı.'
    elif filename.startswith('orman_yangini_'):
        from atlas_afet_veri import key
        year=int(filename.split('_')[2])
        if len(frame)!=81 or not {'il','yil','yangin_sayisi','yanan_alan_ha'}.issubset(frame.columns):
            raise ValueError('Orman yangını tablosu 81 il ve beklenen sütunlara sahip olmalı.')
        years=pd.to_numeric(frame['yil'],errors='raise')
        if not years.eq(year).all():raise ValueError('Yıl bilgileri dosyayla uyuşmuyor.')
        geo=json.loads((root/'turkiye_81_il.geojson').read_text(encoding='utf-8'))
        valid={key(f['properties']['shapeName']) for f in geo['features']}
        if {key(x) for x in frame.il}!=valid or len({key(x) for x in frame.il})!=81:
            raise ValueError('Yangın tablosu 81 il sınırıyla birebir eşleşmiyor.')
        counts=pd.to_numeric(frame['yangin_sayisi'],errors='coerce')
        areas=pd.to_numeric(frame['yanan_alan_ha'],errors='coerce')
        if (counts.dropna()<0).any() or (areas.dropna()<0).any():
            raise ValueError('Negatif yangın sayısı veya alan.')
        if int(counts.sum())!={2024:3797,2025:3224}[year] or abs(float(areas.sum())-{2024:27485,2025:81473}[year])>0.51:
            raise ValueError('OGM 2024/2025 kontrol toplamları eşleşmiyor.')
        summary='81 il ve OGM yıllık ulusal toplamları doğrulandı.'
    else:
        raise ValueError('Henüz desteklenmeyen dosya.')
    return {'satir':len(frame),'il':frame.il.nunique() if 'il' in frame else None,
            'ozet':summary,'preview':frame.head(8)}


_RUNTIME_LOCK=threading.RLock()
_RUNTIME={'updated_at':0.0, 'version':'', 'status':'Paketli veriler', 'folder':None,
          'repo_fingerprint':'', 'last_repo':''}


def runtime_version() -> str:
    return str(_RUNTIME.get('version',''))


def runtime_status() -> str:
    return str(_RUNTIME.get('status',''))


def initialize_remote_data(settings: Settings, force: bool=False) -> bool:
    """App importlarından ÖNCE çağır. GitHub verilerini temp alanda etkinleştir.

    Hatalı depodaki veri üretime geçmez; en son sağlam anlık görüntü kalır.
    Dönüş: aktif veri sürümü değişti mi?
    """
    if not settings.enabled:
        return False
    with _RUNTIME_LOCK:
        identity=settings.repo+'@'+settings.branch+':'+sha256(settings.token.encode()).hexdigest()[:12]
        if identity!=_RUNTIME['last_repo']:
            _RUNTIME.update(updated_at=0.0, version='',repo_fingerprint='',last_repo=identity)
        if not force and time.monotonic()-_RUNTIME['updated_at']<180:
            return False
        _RUNTIME['updated_at']=time.monotonic()
        # Veri okuyucuları ilk importtan itibaren sabit bir `current` yolu kullanır.
        # Repo henüz boş/erişilemez olsa bile yolu hazırla; sonradan repo değişince
        # kodun yüklenmiş Path sabitleri değişmek zorunda kalmaz.
        cache_root=_RUNTIME['folder']
        if cache_root is None:
            cache_root=Path(tempfile.mkdtemp(prefix='afet-atlas-snapshots-'))
            _RUNTIME['folder']=cache_root
        current=cache_root/'current'
        if not current.exists() and not current.is_symlink():
            if os.name!='nt':current.symlink_to(BUNDLED,target_is_directory=True)
            else:shutil.copytree(BUNDLED,current,dirs_exist_ok=True)
        os.environ['AFET_ATLAS_DATA_DIR']=str(current)
        client=GitHubDataRepository(settings)
        try:
            client.check_access()
            index=client.index()
            disabled=client.disabled()
            fingerprint=sha256(json.dumps({'files':index,'disabled':disabled},sort_keys=True).encode()).hexdigest()
            if fingerprint==_RUNTIME['repo_fingerprint']:
                _RUNTIME['status']='Özel GitHub veri deposu bağlı.'
                return False
            cache_root=_RUNTIME['folder']
            if cache_root is None:
                cache_root=Path(tempfile.mkdtemp(prefix='afet-atlas-snapshots-'))
                _RUNTIME['folder']=cache_root
            next_dir=Path(tempfile.mkdtemp(prefix='snapshot-',dir=cache_root))
            try:
                shutil.copytree(BUNDLED,next_dir,dirs_exist_ok=True)
                for fname in DATASETS:
                    if fname in disabled:
                        (next_dir/fname).unlink(missing_ok=True)
                    elif fname in index:
                        raw,remote_sha=client.get(fname)
                        if index[fname]!=remote_sha:
                            raise DataRepositoryError('GitHub dosyası güncellenirken sürüm değişti; tekrar dene.')
                        validate_upload(fname,raw,next_dir)
                        (next_dir/fname).write_bytes(raw)
                # Verilerin kombinasyonunu ayrıca son hâl üzerinde kontrol et.
                from ilce_veri import read_population_bytes, read_sege_csv, eslesme_anahtarlari
                pop=read_population_bytes((next_dir/'ilce_nufus_2025.csv').read_bytes())
                from ilce_veri import _check_official_2025_total
                _check_official_2025_total(pop)
                sege=read_sege_csv(next_dir/'ilce_sege_2022.csv')
                eslesme_anahtarlari(pop,sege)
                current=cache_root/'current'
                if os.name!='nt':
                    tmp_link=cache_root/'next_link'
                    tmp_link.unlink(missing_ok=True)
                    tmp_link.symlink_to(next_dir,target_is_directory=True)
                    os.replace(tmp_link,current)
                else:
                    # Windows'ta symlink yetkisi olmayabileceğinden kopya dizin kullan.
                    current.mkdir(exist_ok=True)
                    for old in current.iterdir():
                        if old.is_file():old.unlink()
                        elif old.is_dir():shutil.rmtree(old)
                    shutil.copytree(next_dir,current,dirs_exist_ok=True)
                os.environ['AFET_ATLAS_DATA_DIR']=str(current)
                _RUNTIME.update(repo_fingerprint=fingerprint,version=fingerprint,
                                status='Özel GitHub veri deposu bağlı.')
                return True
            except Exception:
                shutil.rmtree(next_dir,ignore_errors=True)
                raise
        except (DataRepositoryError,ValueError,OSError,KeyError,requests.RequestException) as exc:
            # Kimlik ve tokenlar asla log veya ziyaretçi ekranına taşınmaz.
            _RUNTIME['status']='Özel veri deposu senkronizasyonu tamamlanamadı: '+str(exc)
            return False
