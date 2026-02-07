from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from restapp.urls import urlpatterns as rest_urlpatterns
from monitoring.view import index
from main.views import custom_404
from django.shortcuts import redirect
from django.http import HttpResponse


def empty_root(request):
    return HttpResponse("", content_type="text/html; charset=utf-8")
    # return redirect("https://www.google.com")


api_title = 'Mahalla Account API documentation'
schema_view = get_swagger_view(title=api_title, patterns=rest_urlpatterns, url='/api/v1/')

urlpatterns = [
    path('', empty_root),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/docs', schema_view),
    path('api/v1/', include('restapp.urls')),
    path('api/v1/gps-ws', index),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
