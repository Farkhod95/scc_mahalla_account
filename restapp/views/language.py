from rest_framework.views import APIView
from rest_framework.response import Response
from main import settings
from restapp.utils.enumserialize import enum_serialize


class LanguagesView(APIView):

    def get(self, request):
        return Response(enum_serialize(settings.LANGUAGES), status=200)