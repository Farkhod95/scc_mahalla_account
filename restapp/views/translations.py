from django.utils import translation, dateparse, timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from restapp.models import TranslationTerm
from restapp.serializers import TranslationSerializer


class TranslationsView(ListAPIView):
    # permission_classes = (permissions.AllowAny,)
    serializer_class = TranslationSerializer

    def get_queryset(self):
        return TranslationTerm.objects.all()

    def get(self, request, **kwargs):
        lang = request.GET.get('lang', 'en')
        translation.activate(lang)

        date_time = request.GET.get('updated_time', '1970-01-01T00:00:00.172Z')
        updated_time = timezone.localtime(dateparse.parse_datetime(date_time))

        data = self.get_queryset().filter(updated_time__gte=updated_time)
        translations = {}
        for item in data:
            translations[item.term_name] = item.name
        return Response(translations)
