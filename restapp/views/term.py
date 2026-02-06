from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters

from restapp.models import TranslationTerm
from restapp.pagination import ResultsSetPagination
from restapp.serializers import TermSerializer


class TermView(ListCreateAPIView):

    serializer_class = TermSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'name_ru', 'name_en', 'name_uz')
    ordering = ['pk']

    def get_queryset(self):
        return TranslationTerm.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TermDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TermSerializer

    def get_queryset(self):
        return TranslationTerm.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
