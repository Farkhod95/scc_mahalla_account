"""
Paynet TMS API test skripti.

ISHLATISH TARTIBI:
1. Brauzerda tms.paynet.uz ga qo'lda kiring (reCAPTCHA + OTP qo'lda).
2. DevTools > Network > verify/ so'rovining Response'idan
   "token" va "refreshToken" qiymatlarini nusxalab, quyidagi
   TOKEN va REFRESH_TOKEN o'zgaruvchilariga joylashtiring.
3. Ushbu skriptni ishga tushiring: python tms_client.py

Bu skript reCAPTCHA yoki OTP'ni avtomatlashtirmaydi -
tokenni qo'lda olib kiritishingiz kerak.
"""

import requests

BASE_URL = "https://tms.paynet.uz/tms"

# Brauzerdan qo'lda olingan tokenlarni shu yerga joylashtiring:
TOKEN = "PASTE_TOKEN_HERE"
REFRESH_TOKEN = "PASTE_REFRESH_TOKEN_HERE"


def get_session(token: str) -> requests.Session:
    """Berilgan token bilan avtorizatsiya qilingan session yaratadi."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    return session


def check_profile(session: requests.Session):
    """Token to'g'ri ishlayotganini tekshirish uchun profile/ ni chaqiradi."""
    resp = session.get(f"{BASE_URL}/profile/")
    print("Status:", resp.status_code)
    print("Response:", resp.text[:1000])
    return resp


if __name__ == "__main__":
    if TOKEN == "PASTE_TOKEN_HERE":
        print("Avval TOKEN o'zgaruvchisiga brauzerdan olingan tokenni joylashtiring.")
    else:
        s = get_session(TOKEN)
        check_profile(s)