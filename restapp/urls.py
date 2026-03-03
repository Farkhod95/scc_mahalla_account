from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from restapp.views.language import LanguagesView
from restapp.views.logout import LogoutView
from restapp.views.term import TermView, TermDetailView
from restapp.views.translations import TranslationsView
from restapp.views.user_log import UserLogsView

urlpatterns = [
    re_path(r'^auth/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^auth/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^auth/logout/$', LogoutView.as_view(), name='auth_logout'),
    path('', include('users.urls')),
    path('', include('monitoring.urls')),
    path('', include('directory.urls')),
    path('', include('reports.urls')),
    re_path(r'^settings/languages/$', LanguagesView.as_view(), name='languages_list'),
    re_path(r'^settings/translations/$', TermView.as_view(), name='translations_list'),
    path('settings/translations/<int:pk>', TermDetailView.as_view(), name='translations_list'),
    re_path(r'^settings/userlogs/$', UserLogsView.as_view(), name='user_logs'),

    path('translations', TranslationsView.as_view(), name='translations_list'),
]

router = DefaultRouter()
urlpatterns += router.urls