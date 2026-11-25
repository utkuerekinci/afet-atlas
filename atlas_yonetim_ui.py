"""Afet Atlas yönetici ekranı: Streamlit üzerinden sınırlı veri yönetimi."""
from __future__ import annotations

import hmac
import os
from pathlib import Path
from hashlib import sha256
import time
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, VerificationError
import pandas as pd
import streamlit as st

from atlas_yonetim_depo import (DATASETS, GitHubDataRepository, DataRepositoryError,
    Settings, validate_upload, initialize_remote_data, runtime_status)

HASHER=PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2)
AUTH_DURATION=3 * 60 * 60  # 3 saat sonra yeniden giriş
FAILED_LIMIT=5
FAILED_COOLDOWN=5 * 60


def _secret(name: str) -> str:
    try:return str(st.secrets.get(name, '')).strip()
    except (FileNotFoundError,KeyError,AttributeError):return ''


def _auth_settings_valid() -> bool:
    return bool(_secret('AFET_ATLAS_ADMIN_KULLANICI') and
                _secret('AFET_ATLAS_ADMIN_SIFRE_OZETI').startswith('$argon2id$'))


def logged_in() -> bool:
    expires=float(st.session_state.get('_atlas_admin_until',0))
    if time.time()>expires:
        st.session_state.pop('_atlas_admin_until',None)
        return False
    return bool(st.session_state.get('_atlas_admin_authenticated')) and _auth_settings_valid()


def _login_attempt(username: str, password: str) -> bool:
    next_try=float(st.session_state.get('_atlas_admin_blocked_until',0))
    if time.time()<next_try:
        return False
    good_name=hmac.compare_digest(username,_secret('AFET_ATLAS_ADMIN_KULLANICI'))
    try:
        good_pass=HASHER.verify(_secret('AFET_ATLAS_ADMIN_SIFRE_OZETI'),password)
    except (VerifyMismatchError, InvalidHashError, VerificationError,ValueError):
        good_pass=False
    if good_name and good_pass:
        st.session_state['_atlas_admin_authenticated']=True
        st.session_state['_atlas_admin_until']=time.time()+AUTH_DURATION
        st.session_state.pop('_atlas_admin_failed',None)
        st.session_state.pop('_atlas_admin_blocked_until',None)
        return True
    count=int(st.session_state.get('_atlas_admin_failed',0))+1
    st.session_state['_atlas_admin_failed']=count
    if count>=FAILED_LIMIT:
        st.session_state['_atlas_admin_blocked_until']=time.time()+FAILED_COOLDOWN
        st.session_state['_atlas_admin_failed']=0
    return False


def _logout():
    for key in ('_atlas_admin_authenticated','_atlas_admin_until','_atlas_admin_validated',
                '_atlas_admin_checked_hash','_atlas_admin_source'):
        st.session_state.pop(key,None)
    st.rerun()


def _protect():
    if not logged_in():
        raise PermissionError('Yönetici girişi gerekli.')


def _repo_client(settings: Settings) -> GitHubDataRepository:
    _protect()
    return GitHubDataRepository(settings)


def _repo_rows(client: GitHubDataRepository) -> tuple[dict,list[str]]:
    client.check_access()
    index=client.index()
    disabled=client.disabled()
    return index,disabled


def _publish(settings:Settings, fname:str, content:bytes, note:str) -> str:
    _protect()
    root=Path(os.environ.get('AFET_ATLAS_DATA_DIR') or __import__('atlas_yonetim_depo').BUNDLED)
    validate_upload(fname,content,root)
    client=_repo_client(settings)
    client.check_access()
    commit=client.put(fname,content,'Afet Atlas veri güncellemesi: '+fname+' | '+note.strip()[:90])
    # Yeni anlık görüntüyü çek; st cache temizlenince eski sıralama gösterilmez.
    if initialize_remote_data(settings,force=True):
        st.cache_data.clear()
    return commit


def admin_page(settings: Settings):
    st.markdown('## Yönetim Paneli')
    st.caption('Veri dosyalarını yalnızca yetkili yönetici özel GitHub veri deposunda güncelleyebilir.')
    if not _auth_settings_valid():
        st.warning('Yönetici kullanıcı adı ve Argon2id şifre özeti henüz Streamlit Secrets içinde tanımlanmamış.')
        st.info('Kurulum talimatları: YONETICI_KURULUM.md. Bu ekran şu anda girişe kapalı.')
        return
    if not logged_in():
        left,right=st.columns([1,1.2])
        with left:
            with st.form('atlas-admin-login',clear_on_submit=True):
                username=st.text_input('Kullanıcı adı',max_chars=100)
                password=st.text_input('Şifre',type='password',max_chars=256)
                submit=st.form_submit_button('Giriş Yap',use_container_width=True)
            if submit:
                if _login_attempt(username,password):
                    st.rerun()
                elif time.time()<float(st.session_state.get('_atlas_admin_blocked_until',0)):
                    st.error('Çok sayıda başarısız deneme. Bu oturumda 5 dakika sonra tekrar deneyebilirsin.')
                else:
                    st.error('Kullanıcı adı veya şifre yanlış.')
        return

    _protect()
    a,b=st.columns([4,1])
    with a:st.success('Yönetici oturumu açık')
    with b:
        if st.button('Çıkış yap',use_container_width=True):_logout()
    # Veri yükleme sekmesini GitHub bağlantısı sorunlu diye gizleme.
    # Dosya her durumda seçilip önizlenebilir, yayınlama yalnızca bağlantı varsa yapılır.
    client = None
    index, disabled = {}, []
    connection_problem = ''
    if not settings.enabled:
        connection_problem = 'Streamlit Secrets içinde özel GitHub veri deposu veya token tanımlı değil.'
    else:
        try:
            client = _repo_client(settings)
            index, disabled = _repo_rows(client)
        except DataRepositoryError as exc:
            connection_problem = str(exc)
    repo_ready = not connection_problem
    if repo_ready:
        st.caption('Veri deposu durumu: ' + runtime_status())
    else:
        st.error('Özel GitHub veri deposu bağlantısı kurulamadı. Dosyaları seçip kontrol '
                 'edebilirsin, ancak bağlantı düzelene kadar yayınlama devre dışı.')
        with st.expander('GitHub bağlantısını kontrol et', expanded=True):
            st.write(connection_problem)
            st.write('**Ayarlanan veri deposu:** `' + (settings.repo or 'Tanımlı değil') + '`')
            st.write('**Ayarlanan dal:** `' + settings.branch + '`')
            st.markdown('**Kontrol et:** GitHub’da özel repo adının birebir aynı olması; '
                        'Streamlit Secrets içindeki `AFET_ATLAS_VERI_REPOSU` ve '
                        '`AFET_ATLAS_VERI_DALI`; fine-grained tokenın bu özel depoyu '
                        '**Only select repositories** listesinde içermesi ve '
                        '**Contents: Read and write** izninin bulunması.')
            if st.button('Bağlantıyı yeniden dene', key='atlas_admin_retry_connection'):
                st.rerun()
    st.caption('Veri yüklemek için ilk sekmeyi aç: dosya seç, doğrula ve bağlantı '
               'sağlandığında yayınla.')
    tabs=st.tabs(['📤 Veri yükle / güncelle','📂 Veri setleri','🕘 Sürüm geçmişi','⚙️ Kurulum bilgisi'])
    with tabs[1]:
        st.markdown('#### Yönetilebilir veri kaynakları')
        for name,spec in DATASETS.items():
            status=('Bağlantı bekleniyor' if not repo_ready else 'Devre dışı' if name in disabled else 'Özel depoda' if name in index else
                    'Paketli başlangıç verisi' if (settings.enabled and name not in index) else 'Bulunamadı')
            c1,c2,c3=st.columns([3.5,1.5,1.6])
            with c1:
                st.markdown('**'+spec['title']+'**')
                st.caption(name)
            with c2:st.write(status)
            with c3:
                if not spec['required']:
                    if st.button('Etkinleştir' if name in disabled else 'Yayından kaldır',
                                 key='admin_toggle_'+name,use_container_width=True,disabled=not repo_ready):
                        try:
                            _protect()
                            client.set_disabled(name,name not in disabled)
                            if initialize_remote_data(settings,force=True):st.cache_data.clear()
                            st.success('Veri seti durumu güncellendi.')
                            st.rerun()
                        except (DataRepositoryError,ValueError) as exc:st.error(str(exc))
                else:st.caption('Temel veri')
            st.divider()
        st.caption('Temel veri dosyaları silinmez; hatalı güncelleme geçmişteki sürüme döndürülür. ' 
                   'İsteğe bağlı veriler yayından kaldırılabilir.')
    with tabs[0]:
        st.markdown('#### 📤 Yeni veri yükle veya mevcut veriyi güncelle')
        st.caption('1 · Veri türünü seç  →  2 · CSV/JSON dosyasını yükle  →  '
                   '3 · Dosyayı Kontrol Et  →  4 · Yayınla')
        names=list(DATASETS)
        selected=st.selectbox('Veri seti türü',names,format_func=lambda n:DATASETS[n]['title'])
        filetype=selected.rsplit('.',1)[-1]
        uploaded=st.file_uploader('CSV veya JSON dosyası seç',type=[filetype],key='atlas_admin_file')
        source=st.text_input('Kaynak / açıklama (commit notu)',max_chars=90,
                             placeholder='Örnek: resmî kaynaktan 2025 nüfus güncellemesi')
        raw=uploaded.getvalue() if uploaded else b''
        content_hash=sha256(raw).hexdigest() if raw else ''
        verified_key=st.session_state.get('_atlas_admin_checked_hash')
        if st.button('Dosyayı Kontrol Et',disabled=not raw):
            try:
                info=validate_upload(selected,raw,Path(os.environ.get('AFET_ATLAS_DATA_DIR') or __import__('atlas_yonetim_depo').BUNDLED))
                st.session_state['_atlas_admin_checked_hash']=(selected,content_hash)
                st.session_state['_atlas_admin_validated']=info['ozet']
            except (ValueError,KeyError,UnicodeError) as exc:
                st.session_state.pop('_atlas_admin_checked_hash',None)
                st.error(str(exc))
        is_verified=st.session_state.get('_atlas_admin_checked_hash')==(selected,content_hash) and bool(raw)
        if is_verified:
            st.success(st.session_state.get('_atlas_admin_validated','Kontroller başarılı.'))
            try:
                preview=validate_upload(selected,raw,Path(os.environ.get('AFET_ATLAS_DATA_DIR') or __import__('atlas_yonetim_depo').BUNDLED))['preview']
                st.dataframe(preview,hide_index=True,use_container_width=True)
            except ValueError as exc:
                st.error(str(exc))
                is_verified=False
        confirm=st.checkbox('Bu dosyanın mevcut yayındaki veriyi değiştireceğini onaylıyorum.',value=False)
        if st.button('Doğrulanan Veriyi Yayınla',type='primary',
                     disabled=not(repo_ready and is_verified and confirm and source.strip()),
                     use_container_width=True):
            try:
                commit=_publish(settings,selected,raw,source)
                st.session_state.pop('_atlas_admin_checked_hash',None)
                st.success('Özel GitHub veri deposuna kaydedildi. Commit: '+commit[:10])
                if 'tamamlanamadı' in runtime_status():
                    st.warning('Veri GitHub’a kaydedildi ancak henüz canlı okuma önbelleğine uygulanamadı. Yönetim ekranında depo durumunu kontrol et.')
                st.rerun()
            except (DataRepositoryError,ValueError,PermissionError) as exc:st.error(str(exc))
        if not repo_ready:
            st.caption('Bağlantı kurulunca doğruladığın dosyayı yeniden seçerek yayınlayabilirsin.')
        st.caption('Dosya seçimi ve önizleme ziyaretçilere açık değildir. Kaynak kod deposuna veri yazılmaz.')
    with tabs[2]:
        if not repo_ready:
            st.info('Sürüm geçmişi için önce özel GitHub deposuna bağlantı kurulmalı.')
        else:
            fname=st.selectbox('Geri dönülecek veri seti',list(DATASETS),key='atlas_history_name',
                               format_func=lambda x:DATASETS[x]['title'])
            try:
                commits=client.commits(fname)
                if not commits:st.info('Bu veri setinin özel repoda henüz commit geçmişi bulunmuyor.')
                else:
                    opts={x['sha']:x for x in commits}
                    chosen=st.selectbox('Sürüm seç',list(opts),
                        format_func=lambda x:opts[x]['date'][:10]+' · '+opts[x]['message'][:65]+' · '+x[:7])
                    if st.button('Önceki Sürümü Önizle'):
                        raw,_=client.get(fname,ref=chosen)
                        info=validate_upload(fname,raw,Path(os.environ.get('AFET_ATLAS_DATA_DIR') or __import__('atlas_yonetim_depo').BUNDLED))
                        st.session_state['_atlas_history_checked']=(fname,chosen,sha256(raw).hexdigest())
                        st.success(info['ozet'])
                        st.dataframe(info['preview'],hide_index=True,use_container_width=True)
                    can_restore=st.session_state.get('_atlas_history_checked')
                    ready=bool(can_restore and can_restore[:2]==(fname,chosen))
                    confirm=st.checkbox('Seçilen eski sürümün yeniden yayınlanmasını onaylıyorum.',
                                        key='atlas_history_confirm')
                    if st.button('Seçilen Sürüme Geri Dön',disabled=not(ready and confirm)):
                        _protect()
                        raw,_=client.get(fname,ref=chosen)
                        if sha256(raw).hexdigest()!=can_restore[2]:
                            raise DataRepositoryError('Önizlemeden sonra dosya değişti.')
                        commit=_publish(settings,fname,raw,'Önceki sürüme dönüş '+chosen[:10])
                        st.success('Önceki sürüm yeniden yayınlandı: '+commit[:10])
                        st.rerun()
            except (DataRepositoryError,ValueError) as exc:st.error(str(exc))
    with tabs[3]:
        st.markdown('**Kod reposu:** https://github.com/utkuerekinci/afet-atlas')
        st.markdown('**Özel veri reposu:** `'+settings.repo+'` (yalnızca yönetici erişebilir)')
        st.write('Veri deposu GitHub üzerinde PRIVATE olmalı. Fine-grained token yalnızca bu repo için Contents: Read and write iznine sahip olmalı.')
        st.write('Şifre özeti ve token GitHub kod dosyalarına eklenmez; Streamlit Secrets içinde saklanır.')
