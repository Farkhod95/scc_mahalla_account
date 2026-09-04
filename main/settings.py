import os
from datetime import timedelta
from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'django-insecure-+z(00bq*+-lxrzdvn3-6ti8czltg_8r0-+c$+q8+!e&j%u2m_v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['mm.safecity.uz','192.168.168.149','192.168.168.171','api-mm.safecity.uz','localhost','127.0.0.1', '10.6.189.50', '87.192.235.232']

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'channels',
    'users.apps.UsersConfig',
    'restapp',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    # 'django_dump_load_utf8',      # for backup
    'monitoring',
    'directory',
    'reports',
    'django_celery_results',
    'django_celery_beat',
    'ckeditor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # for front
    # ✅ DEBUG=True bo‘lsa ham 404 sahifani oddiy qiladi
    'restapp.middlewares.simple_404.SimpleNotFoundMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'restapp.middlewares.middlewares.RequestMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # for translation
]

CSRF_TRUSTED_ORIGINS = [
    "https://api-mm.safecity.uz",
    "http://api-mm.safecity.uz",
    "https://mm.safecity.uz",
    "http://mm.safecity.uz",
    "http://10.6.189.50",
    "https://10.6.189.50",
    "http://192.168.168.149:3000",
    "https://192.168.168.149:3000",
    "http://192.168.168.149",

    "http://192.168.168.149:8080",

    "http://192.168.168.171",
    "http://192.168.168.171:3000",
    "http://192.168.168.171:3030",
    "http://192.168.168.171:8080",
]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",

    "http://192.168.168.149:3000",
    "https://192.168.168.149:3000",
    "http://192.168.168.149:3030",
    "https://192.168.168.149:3030",

    "http://192.168.168.149:8080",

    "http://192.168.168.171:3000",
    "https://192.168.168.171:3000",
    "http://192.168.168.171:3030",
    "https://192.168.168.171:3030",
    "http://192.168.168.171:8080",
    "http://192.168.168.171",

    "https://mm.safecity.uz",
    "http://mm.safecity.uz",
    "https://api-mm.safecity.uz",
    "http://api-mm.safecity.uz",

    "http://10.6.189.50:8080",
    "http://10.6.189.50",
    "http://10.6.189.50:3000",
    "https://10.6.189.50:8080",
    "https://10.6.189.50",
    "https://10.6.189.50:3000",

    "https://87.192.235.232:1998",
    "https://87.192.235.232",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'language-code',
]

# go2rtc
GO2RTC_URL         = "http://mahalla_go2rtc:1984"
GO2RTC_PUBLIC_HOST = "192.168.168.149"          # serverning tashqi IP si
# Frontend stream URL — nginx /go2rtc/ proxy orqali (1984 portsiz).
# /api/ws — WebSocket endpoint, shuning uchun ws:// (TLS bo'lsa wss://).
GO2RTC_STREAM_BASE = f"ws://{GO2RTC_PUBLIC_HOST}:8080/go2rtc"

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

# WSGI_APPLICATION = 'main.wsgi.application'
ASGI_APPLICATION = 'main.asgi.application'

CELERY_RESULT_BACKEND = 'django-db'


CELERY_CACHE_BACKEND = 'default'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# Davriy vazifalar. DatabaseScheduler bu jadvalni o'qib DB ga sinxronlaydi.
CELERY_BEAT_SCHEDULE = {
    # Har kuni 02:00 da faktura tushumini FacturaRevenueDaily ga yig'adi.
    'sync-factura-revenue-daily': {
        'task': 'celery_task.sync_factura_revenue_task',
        'schedule': crontab(hour=2, minute=0),
    },
    # Har kuni 03:00 da BUGUNGI OKKM (NKM cheklar) tushumini OkkmRevenueDaily ga
    # yig'adi. O'tgan kunlar — `python manage.py sync_okkm_revenue --from .. --to ..`
    # (bir martalik backfill).
    'sync-okkm-revenue-daily': {
        'task': 'celery_task.sync_okkm_revenue_task',
        'schedule': crontab(hour=3, minute=0),
    },
    # Har oyning 1-kuni 04:00 da ijara (rent) integratsiyasidan ijarachilarni sync qiladi.
    'sync-tenants-rent-monthly': {
        'task': 'celery_task.sync_tenants_rent_task',
        'schedule': crontab(day_of_month=1, hour=4, minute=0),
    },
    # Har 15 daqiqada do'kon kassa (NKM, bugungi kun) rangi keshini
    # to'ldiradi, shunda /shop/cash-status/ jonli soliqqa bormay tez javob beradi.
    'warm-shop-cash-status': {
        'task': 'celery_task.warm_shop_cash_status_task',
        'schedule': crontab(minute='*/15'),
    },
    # Har 6 soatda soliq rekvizit + faktura tushumini ShopTenant maydonlariga
    # yozadi, shunda shop-tenant API lari request thread da soliqqa bormaydi.
    'sync-tenant-soliq': {
        'task': 'celery_task.sync_tenant_soliq_task',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Har kuni 06:00 da soliq tushumi OYLIK tarixini (TaxRevenueMonthly) JORIY oy
    # uchun yangilaydi (company-account payTax, kodlar 1/32/46/100). Dashboard
    # (oylik/yillik) va reports/tax-revenue SHU jadvaldan o'qiydi. O'tgan oylar —
    # bir martalik backfill: `python manage.py sync_tax_revenue_monthly`.
    # (Nom o'zgarmadi — DatabaseScheduler mavjud entry'ni yangilashi uchun;
    #  eski snapshot task o'rniga endi oylik task chaqiriladi.)
    'sync-tax-revenue-daily': {
        'task': 'celery_task.sync_tax_revenue_monthly_task',
        'schedule': crontab(hour=6, minute=0),
    },
    # Har kuni 01:00 da 7 kundan eski CarFlow rasmlarini (base64 JPEG) tozalaydi
    # (baza hajmi cheksiz o'smasligi uchun; boshqa maydonlar saqlanadi).
    'cleanup-carflow-images': {
        'task': 'celery_task.cleanup_carflow_images_task',
        'schedule': crontab(hour=1, minute=0),
    },
}

# Damafon (Dahua VTO intercom) mikroservis — bizning backend faqat PROXY qiladi
# (REST + WebSocket). Ma'lumot mikroservis DB sida; mahalla bog'lanishi location_id.
DAMAFON_BASE_URL = "https://192.168.168.170:8000"
DAMAFON_VERIFY_SSL = False  # self-signed sertifikat
DAMAFON_TIMEOUT = 15

### Local Host uchun

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }
#
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
#
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://localhost:6379/1',
#     }
# }
#
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'db_mahalla_account',
#         'USER': 'postgres',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

### Server uchun

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

CELERY_BROKER_URL = 'redis://redis:6379/0'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mahalla_account_db',
        'USER': 'mahalla_account_user',
        'PASSWORD': 'mahalla_account_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django REST framework simplejwt
# https://github.com/SimpleJWT/django-rest-framework-simplejwt

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'restapp.authentication.StaticTokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ),
    'UNICODE_JSON': True,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'EXCEPTION_HANDLER': 'restapp.exceptions.custom_exception_handler',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1500),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'BLACKLIST_AFTER_ROTATION': True,
}

# =========================
# Raqamli bozor (scc_raqamli_bozor) proxy — statik token
# Boshqa loyiha shu token bilan (X-Api-Key header) barcha API ma'lumotlarini
# o'qiy oladi (restapp.authentication.StaticTokenAuthentication).
# Qiymat FAQAT environment (.env / docker-compose secret) orqali beriladi —
# kodga hardcode qilinmaydi.
# =========================
MALIKA_PROXY_STATIC_TOKEN = os.environ.get('MALIKA_PROXY_STATIC_TOKEN', '')

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
}

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

LANGUAGES = (
    ('en', _('English')),
    ('uz', _('Uzbek')),
    ('ru', _('Russian')),
)
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGE_CODE = 'en'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.path.join(BASE_DIR, "media_static")
AUTH_USER_MODEL = 'users.User'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

MEDIA_URL = '/assets/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'