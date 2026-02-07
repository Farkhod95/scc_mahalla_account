from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from directory.filterset import RegionssFilter
from directory.models import Region
from directory.serializers import RegionSerializer, RegionListSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


class RegionViewList(ListCreateAPIView):
    serializer_class = RegionListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    search_fields = ('code', 'name_ru', 'name_en', 'name_uz', 'code')
    permission_classes = (AllowAny,)
    ordering = ['pk']
    http_method_names = ['get']

    def get_queryset(self):
        return Region.objects.all()


class RegionView(ListCreateAPIView):
    serializer_class = RegionListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = RegionssFilter
    search_fields = ('code', 'name_ru', 'name_en', 'name_uz', 'code')
    ordering = ['pk']

    def get_queryset(self):
        return Region.objects.all()

    def post(self, request):
        # serializer = RegionSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save(created_by=self.request.user)
        # return Response(serializer.data, status.HTTP_201_CREATED)
        regions_data =[
            {
                "id": 1,
                "code": 17,
                "name": "Andijan region",
                "name_en": "Andijan region",
                "name_uz": "Andijon viloyati",
                "name_ru": "Андижанская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 2,
                "code": 20,
                "name": "Bukhara region",
                "name_en": "Bukhara region",
                "name_uz": "Buxoro viloyati",
                "name_ru": "Бухарская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 3,
                "code": 13,
                "name": "Jizzakh region",
                "name_en": "Jizzakh region",
                "name_uz": "Jizzax viloyati",
                "name_ru": "Джизакская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 4,
                "code": 18,
                "name": "Kashkadarya region",
                "name_en": "Kashkadarya region",
                "name_uz": "Qashqadaryo viloyati",
                "name_ru": "Кашкадарьинская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 5,
                "code": 21,
                "name": "Navoi region",
                "name_en": "Navoi region",
                "name_uz": "Navoiy viloyati",
                "name_ru": "Навоийская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 6,
                "code": 16,
                "name": "Namangan region",
                "name_en": "Namangan region",
                "name_uz": "Namangan viloyati",
                "name_ru": "Наманганская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 7,
                "code": 14,
                "name": "Samarkand region",
                "name_en": "Samarkand region",
                "name_uz": "Samarqand viloyati",
                "name_ru": "Самаркандская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 8,
                "code": 19,
                "name": "Surkhandarya region",
                "name_en": "Surkhandarya region",
                "name_uz": "Surxondaryo viloyati",
                "name_ru": "Сурхандарьинская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 9,
                "code": 12,
                "name": "Syrdarya region",
                "name_en": "Syrdarya region",
                "name_uz": "Sirdaryo viloyati",
                "name_ru": "Сырдарьинская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 10,
                "code": 10,
                "name": "Tashkent city",
                "name_en": "Tashkent city",
                "name_uz": "Toshkent shahri",
                "name_ru": "город Ташкент",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 11,
                "code": 11,
                "name": "Tashkent region",
                "name_en": "Tashkent region",
                "name_uz": "Toshkent viloyati",
                "name_ru": "Ташкентская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 12,
                "code": 15,
                "name": "Fergana region",
                "name_en": "Fergana region",
                "name_uz": "Farg'ona viloyati",
                "name_ru": "Ферганская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 13,
                "code": 22,
                "name": "Khorezm region",
                "name_en": "Khorezm region",
                "name_uz": "Xorazm viloyati",
                "name_ru": "Хорезмская область",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            },
            {
                "id": 14,
                "code": 23,
                "name": "Republic of Karakalpakstan",
                "name_en": "Republic of Karakalpakstan",
                "name_uz": "Qoraqalpog'iston Respublikasi",
                "name_ru": "Республика Каракалпакстан",
                "created_time": "2020-01-01 00:00:00+00:00",
                "updated_time": "2020-01-01 00:00:00+00:00",
                "created_by": 1
            }
        ]

        for region in regions_data:
            # Prepare the data for serializer
            region_data = {
                'id': region['id'],
                'code': region['code'],
                'name': region['name'],
                'name_uz': region['name_uz'],  # Ensure that 'name_uz' is included in the input data
                'name_ru': region['name_ru'],  # Ensure that 'name_ru' is included in the input data
                'name_en': region['name_en'],  # Ensure that 'name_en' is included in the input data
            }

            # Instantiate the serializer with the data
            serializer = RegionSerializer(data=region_data)

            # Validate and save the data if valid
            if serializer.is_valid():
                # Create or update the region using serializer's save() method
                serializer.save()
                print(f"Region {region['name']} created/updated successfully.")
            else:
                # Handle validation errors
                print(f"Validation errors for region {region['name']}: {serializer.errors}")
        return Response({}, status.HTTP_201_CREATED)


class RegionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = RegionSerializer

    def get_queryset(self):
        return Region.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        region = get_object_or_404(Region, id=pk)
        serializer = RegionListSerializer(region)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        region = get_object_or_404(Region, id=pk)
        serializer = self.serializer_class(region, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        region = get_object_or_404(Region, id=pk)
        region.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)



