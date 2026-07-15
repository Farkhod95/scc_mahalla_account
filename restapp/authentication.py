from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import constant_time_compare
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Raqamli bozor (scc_raqamli_bozor) shu username bilan xizmat foydalanuvchisi
# sifatida kiradi — statik token orqali autentifikatsiya qilinganda ishlatiladi.
RAQAMLI_BOZOR_PROXY_SERVICE_USERNAME = "raqamli_bozor_service"


class StaticTokenAuthentication(BaseAuthentication):
    """
    Boshqa loyiha (Raqamli bozor / scc_raqamli_bozor) proxy sifatida barcha
    API ma'lumotlarini olishi uchun statik token bilan autentifikatsiya.

    So'rovda `X-Api-Key: <MALIKA_PROXY_STATIC_TOKEN>` header kelsa va u
    settings dagi token bilan mos kelsa — maxsus xizmat foydalanuvchisi
    sifatida autentifikatsiya qilinadi (JWT/login shart emas).
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_X_API_KEY")
        if not token:
            return None

        expected = getattr(settings, "MALIKA_PROXY_STATIC_TOKEN", "") or ""
        if not expected or not constant_time_compare(token, expected):
            raise AuthenticationFailed("Noto'g'ri statik token (X-Api-Key).")

        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username=RAQAMLI_BOZOR_PROXY_SERVICE_USERNAME,
            defaults={"is_active": True},
        )
        if not user.is_active:
            raise AuthenticationFailed("Xizmat foydalanuvchisi faol emas.")
        return (user, None)

    def authenticate_header(self, request):
        return "X-Api-Key"
