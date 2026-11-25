"""Yerelde güvenli yönetici parolası özeti üret.

Çalıştır: python yonetici_sifre_olustur.py
Şifre ekrana veya komut satırı geçmişine yazılmaz; sadece Argon2id özeti basılır.
"""
from getpass import getpass
from argon2 import PasswordHasher


def main():
    print('Afet Atlas · Yönetici parolası özeti oluşturma (yerel)')
    first=getpass('Yeni şifre (en az 12 karakter): ')
    if len(first)<12:
        raise SystemExit('Şifre en az 12 karakter olmalı.')
    second=getpass('Şifreyi tekrar gir: ')
    if first!=second:
        raise SystemExit('Şifreler uyuşmuyor.')
    digest=PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2).hash(first)
    print('\nYalnızca Streamlit Secrets içerisine ekle (GitHub kod dosyalarına değil):')
    print('AFET_ATLAS_ADMIN_SIFRE_OZETI = "'+digest+'"')
    print('\nGerçek şifreni ve GitHub tokenını ChatGPT sohbetine gönderme.')


if __name__=='__main__':
    main()
