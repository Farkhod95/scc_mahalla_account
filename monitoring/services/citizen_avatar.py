import hashlib
import mimetypes
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.files.base import ContentFile


BASE_URL = "http://172.20.20.9:7050/get-image/10/citizen-images"
TOKEN = "01277b22f8900d333171ed193fbd1eb7"


def generate_citizen_pinf(pinfl: Optional[str]) -> str:
    pinfl = (pinfl or "").strip()
    return hashlib.sha256(pinfl.encode("utf-8")).hexdigest()


def _guess_ext(content_type: str) -> str:
    ext = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
    if ext == ".jpe":
        ext = ".jpg"
    return ext or ".jpg"


def fetch_citizen_avatar_file(
    pinfl: Optional[str],
    *,
    token: str = TOKEN,
    base_url: str = BASE_URL,
    timeout: int = 20,
) -> Optional[Tuple[str, ContentFile]]:
    """
    PINFL -> citizen servisdan rasmni olib keladi va FILE qaytaradi.

    Return:
        (filename, ContentFile)  yoki  None
    """
    pinfl = (pinfl or "").strip()
    if not pinfl:
        return None

    pin_hash = generate_citizen_pinf(pinfl)
    print("pin_hash", pin_hash)
    url = f"{base_url}/{pin_hash}.jpg"

    headers = {
        "Authorization": f"Token {token}",
        "Accept": "image/*",
    }

    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=None,
        connect=3,
        read=3,
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)

    try:
        resp = session.get(url, headers=headers, timeout=timeout)

        if resp.status_code == 404:
            return None

    except requests.RequestException:
        return None

    if resp.status_code != 200:
        return None

    content_type = (resp.headers.get("Content-Type") or "").lower()
    if not content_type.startswith("image/"):
        return None

    ext = _guess_ext(content_type)
    filename = f"citizen_{pin_hash[:16]}{ext}"

    return filename, ContentFile(resp.content)
