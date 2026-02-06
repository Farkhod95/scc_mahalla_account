from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from directory.filterset import DistrictFilter
from directory.models import District, Region
from directory.serializers import DistrictListSerializer, DistrictSerializer

from restapp.pagination import ResultsSetPagination


class DistrictFieldInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_info = []

        for field in District._meta.fields:
            field_info.append({
                "field_name": field.name,
                "verbose_name": str(field.verbose_name),
                "help_text": str(field.help_text) if field.help_text else "",
                "type": field.get_internal_type(),
                "max_length": getattr(field, 'max_length', None),
                "choices": dict(field.choices) if field.choices else None
            })

        return Response(field_info)


class DistrictViewList(ListCreateAPIView):
    serializer_class = DistrictListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DistrictFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['pk']
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        return District.objects.all()


class DistrictView(ListCreateAPIView):
    serializer_class = DistrictListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DistrictFilter
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ['pk']

    def get_queryset(self):
        queryset = District.objects.all()
        region_ids = self.request.GET.get('region')
        if region_ids is not None:
            try:
                regions = [int(id) for id in region_ids.split(',')]
                queryset = queryset.filter(region__in=regions)
            except ValueError:
                raise APIException("ID is not number")
        return queryset

    def post(self, request):
        # serializer = DistrictSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save(created_by=self.request.user)
        # return Response(serializer.data, status.HTTP_201_CREATED)
        json_data = [
      {
        "model": "directory.District",
        "pk": 1,
        "fields": {
          "code": 1702,
          "name": "Oltinko'l district",
          "name_en": "Oltinko'l district",
          "name_ru": "Алтынкульский район",
          "name_uz": "Oltinko'l tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 2,
        "fields": {
          "code": 1701,
          "name": "Andijon district",
          "name_en": "Andijon district",
          "name_ru": "Андижанский район",
          "name_uz": "Andijon tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 3,
        "fields": {
          "code": 1704,
          "name": "Baliqchi district",
          "name_en": "Baliqchi district",
          "name_ru": "Балыкчинский район",
          "name_uz": "Baliqchi tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 4,
        "fields": {
          "code": 1705,
          "name": "Bo'z district",
          "name_en": "Bo'ston district",
          "name_ru": "Бустонский район",
          "name_uz": "Bo'ston tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 5,
        "fields": {
          "code": 1713,
          "name": "Buloqboshi district",
          "name_en": "Buloqboshi district",
          "name_ru": "Булакбашинский район",
          "name_uz": "Buloqboshi tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 6,
        "fields": {
          "code": 1709,
          "name": "Jalaquduq district",
          "name_en": "Jalaquduq district",
          "name_ru": "Жалакудукский район",
          "name_uz": "Jalaquduq tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 7,
        "fields": {
          "code": 1712,
          "name": "Izboskan district",
          "name_en": "Izboskan district",
          "name_ru": "Избасканский район",
          "name_uz": "Izboskan tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 8,
        "fields": {
          "code": 1706,
          "name": "Ulug'nor district",
          "name_en": "Ulug'nor district",
          "name_ru": "Улугноpский район",
          "name_uz": "Ulug'nor tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 9,
        "fields": {
          "code": 1708,
          "name": "Qo'rg'ontepa district",
          "name_en": "Qo'rg'ontepa district",
          "name_ru": "Кургантепинский район",
          "name_uz": "Qo'rg'ontepa tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 10,
        "fields": {
          "code": 1703,
          "name": "Asaka district",
          "name_en": "Asaka district",
          "name_ru": "Асакинский район",
          "name_uz": "Asaka tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 11,
        "fields": {
          "code": 1711,
          "name": "Marxamat district",
          "name_en": "Marxamat district",
          "name_ru": "Мархаматский район",
          "name_uz": "Marxamat tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 12,
        "fields": {
          "code": 1707,
          "name": "Shaxrixon district",
          "name_en": "Shaxrixon district",
          "name_ru": "Шахриханский район",
          "name_uz": "Shaxrixon tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 13,
        "fields": {
          "code": 1714,
          "name": "Paxtaobod district",
          "name_en": "Paxtaobod district",
          "name_ru": "Пахтаабадский район",
          "name_uz": "Paxtaobod tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 14,
        "fields": {
          "code": 1710,
          "name": "Xo'jaobod district",
          "name_en": "Xo'jaobod district",
          "name_ru": "Ходжаабадский район",
          "name_uz": "Xo'jaobod tumani",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 15,
        "fields": {
          "code": 2004,
          "name": "Olot district",
          "name_en": "Olot district",
          "name_ru": "Алатский район",
          "name_uz": "Olot tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 16,
        "fields": {
          "code": 2010,
          "name": "Buxoro district",
          "name_en": "Buxoro district",
          "name_ru": "Бухарский район",
          "name_uz": "Buxoro tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 17,
        "fields": {
          "code": 2002,
          "name": "Vobkent district",
          "name_en": "Vobkent district",
          "name_ru": "Вабкентский район",
          "name_uz": "Vobkent tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 18,
        "fields": {
          "code": 2012,
          "name": "G'ijduvon district",
          "name_en": "G'ijduvon district",
          "name_ru": "Гиждуванский район",
          "name_uz": "G'ijduvon tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 19,
        "fields": {
          "code": 2011,
          "name": "Kogon district",
          "name_en": "Kogon district",
          "name_ru": "Каганский район",
          "name_uz": "Kogon tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 20,
        "fields": {
          "code": 2006,
          "name": "Qorako'l district",
          "name_en": "Qorako'l district",
          "name_ru": "Каракульский район",
          "name_uz": "Qorako'l tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 21,
        "fields": {
          "code": 2008,
          "name": "Qorovulbozor district",
          "name_en": "Qorovulbozor district",
          "name_ru": "Караулбазарский район",
          "name_uz": "Qorovulbozor tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 22,
        "fields": {
          "code": 2003,
          "name": "Peshku district",
          "name_en": "Peshku district",
          "name_ru": "Пешкунский район",
          "name_uz": "Peshku tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 23,
        "fields": {
          "code": 0,
          "name": "Romitan district",
          "name_en": "Romitan district",
          "name_ru": "Ромитанский район",
          "name_uz": "Romitan tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 24,
        "fields": {
          "code": 2005,
          "name": "Jondor district",
          "name_en": "Jondor district",
          "name_ru": "Жондоpский район",
          "name_uz": "Jondor tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 25,
        "fields": {
          "code": 2007,
          "name": "Shofirkon district",
          "name_en": "Shofirkon district",
          "name_ru": "Шафирканский район",
          "name_uz": "Shofirkon tumani",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 26,
        "fields": {
          "code": 1310,
          "name": "Arnasoy district",
          "name_en": "Arnasoy district",
          "name_ru": "Арнасайский район",
          "name_uz": "Arnasoy tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 27,
        "fields": {
          "code": 1307,
          "name": "Baxmal district",
          "name_en": "Baxmal district",
          "name_ru": "Бахмальский район",
          "name_uz": "Baxmal tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 28,
        "fields": {
          "code": 1306,
          "name": "G'allaorol district",
          "name_en": "G'allaorol district",
          "name_ru": "Галляаральский район",
          "name_uz": "G'allaorol tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 29,
        "fields": {
          "code": 1315,
          "name": "Sharof Rashidov district",
          "name_en": "Sharof Rashidov district",
          "name_ru": "Шароф Рашидовский район",
          "name_uz": "Sharof Rashidov tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 30,
        "fields": {
          "code": 1302,
          "name": "Do'stlik district",
          "name_en": "Do'stlik district",
          "name_ru": "Дустликский район",
          "name_uz": "Do'stlik tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 31,
        "fields": {
          "code": 1311,
          "name": "Zomin district",
          "name_en": "Zomin district",
          "name_ru": "Зааминский район",
          "name_uz": "Zomin tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 32,
        "fields": {
          "code": 1309,
          "name": "Zarbdor district",
          "name_en": "Zarbdor district",
          "name_ru": "Зарбдарский район",
          "name_uz": "Zarbdor tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 33,
        "fields": {
          "code": 1312,
          "name": "Mirzacho'l district",
          "name_en": "Mirzacho'l district",
          "name_ru": "Мирзачульский район",
          "name_uz": "Mirzacho'l tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 34,
        "fields": {
          "code": 1309,
          "name": "Zafarobod district",
          "name_en": "Zafarobod district",
          "name_ru": "Зафарабадский район",
          "name_uz": "Zafarobod tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 35,
        "fields": {
          "code": 1308,
          "name": "Paxtakor district",
          "name_en": "Paxtakor district",
          "name_ru": "Пахтакорский район",
          "name_uz": "Paxtakor tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 36,
        "fields": {
          "code": 1304,
          "name": "Forish district",
          "name_en": "Forish district",
          "name_ru": "Фаришский район",
          "name_uz": "Forish tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 37,
        "fields": {
          "code": 1313,
          "name": "Yangiobod district",
          "name_en": "Yangiobod district",
          "name_ru": "Янгиободский район",
          "name_uz": "Yangiobod tumani",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 38,
        "fields": {
          "code": 1808,
          "name": "G'uzor district",
          "name_en": "G'uzor district",
          "name_ru": "Гузарский район",
          "name_uz": "G'uzor tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 39,
        "fields": {
          "code": 1804,
          "name": "Dehqonobod district",
          "name_en": "Dehqonobod district",
          "name_ru": "Дехканабадский район",
          "name_uz": "Dehqonobod tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 40,
        "fields": {
          "code": 1805,
          "name": "Qamashi district",
          "name_en": "Qamashi district",
          "name_ru": "Камашинский район",
          "name_uz": "Qamashi tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 41,
        "fields": {
          "code": 1809,
          "name": "Qarshi district",
          "name_en": "Qarshi district",
          "name_ru": "Каршинский район",
          "name_uz": "Qarshi tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 42,
        "fields": {
          "code": 1802,
          "name": "Koson district",
          "name_en": "Koson district",
          "name_ru": "Касанский район",
          "name_uz": "Koson tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 43,
        "fields": {
          "code": 1811,
          "name": "Kitob district",
          "name_en": "Kitob district",
          "name_ru": "Китабский район",
          "name_uz": "Kitob tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 44,
        "fields": {
          "code": 1814,
          "name": "Mirishkor district",
          "name_en": "Mirishkor district",
          "name_ru": "Миришкорский район",
          "name_uz": "Mirishkor tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 45,
        "fields": {
          "code": 1813,
          "name": "Muborak district",
          "name_en": "Muborak district",
          "name_ru": "Мубарекский район",
          "name_uz": "Muborak tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 46,
        "fields": {
          "code": 1810,
          "name": "Nishon district",
          "name_en": "Nishon district",
          "name_ru": "Нишанский район",
          "name_uz": "Nishon tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 47,
        "fields": {
          "code": 1812,
          "name": "Kasbi district",
          "name_en": "Kasbi district",
          "name_ru": "Касбинский район",
          "name_uz": "Kasbi tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 48,
        "fields": {
          "code": 1801,
          "name": "Chiroqchi district",
          "name_en": "Chiroqchi district",
          "name_ru": "Чиракчинский район",
          "name_uz": "Chiroqchi tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 49,
        "fields": {
          "code": 1803,
          "name": "Shahrisabz district",
          "name_en": "Shahrisabz district",
          "name_ru": "Шахрисабзский район",
          "name_uz": "Shahrisabz tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 50,
        "fields": {
          "code": 1806,
          "name": "Yakkabog' district",
          "name_en": "Yakkabog' district",
          "name_ru": "Яккабагский район",
          "name_uz": "Yakkabog' tumani",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 51,
        "fields": {
          "code": 2102,
          "name": "Konimex district",
          "name_en": "Konimex district",
          "name_ru": "Канимехский район",
          "name_uz": "Konimex tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 52,
        "fields": {
          "code": 2109,
          "name": "Qiziltepa district",
          "name_en": "Qiziltepa district",
          "name_ru": "Кызылтепинский район",
          "name_uz": "Qiziltepa tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 53,
        "fields": {
          "code": 2105,
          "name": "Navbahor district",
          "name_en": "Navbahor district",
          "name_ru": "Навбахорский район",
          "name_uz": "Navbahor tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 54,
        "fields": {
          "code": 2110,
          "name": "Karmana district",
          "name_en": "Karmana district",
          "name_ru": "Карманинский район",
          "name_uz": "Karmana tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 55,
        "fields": {
          "code": 2107,
          "name": "Nurota district",
          "name_en": "Nurota district",
          "name_ru": "Нуратинский район",
          "name_uz": "Nurota tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 56,
        "fields": {
          "code": 2104,
          "name": "Tomdi district",
          "name_en": "Tomdi district",
          "name_ru": "Тамдынский район",
          "name_uz": "Tomdi tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 57,
        "fields": {
          "code": 2101,
          "name": "Uchquduq district",
          "name_en": "Uchquduq district",
          "name_ru": "Учкудукский район",
          "name_uz": "Uchquduq tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 58,
        "fields": {
          "code": 2108,
          "name": "Xatirchi district",
          "name_en": "Xatirchi district",
          "name_ru": "Хатырчинский район",
          "name_uz": "Xatirchi tumani",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 59,
        "fields": {
          "code": 1602,
          "name": "Mingbuloq district",
          "name_en": "Mingbuloq district",
          "name_ru": "Мингбулакский pайон",
          "name_uz": "Mingbuloq tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 60,
        "fields": {
          "code": 1609,
          "name": "Kosonsoy district",
          "name_en": "Kosonsoy district",
          "name_ru": "Касансайский район",
          "name_uz": "Kosonsoy tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 61,
        "fields": {
          "code": 1603,
          "name": "Namangan district",
          "name_en": "Namangan district",
          "name_ru": "Наманганский район",
          "name_uz": "Namangan tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 62,
        "fields": {
          "code": 1604,
          "name": "Norin district",
          "name_en": "Norin district",
          "name_ru": "Нарынский район",
          "name_uz": "Norin tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 63,
        "fields": {
          "code": 1611,
          "name": "Pop district",
          "name_en": "Pop district",
          "name_ru": "Папский район",
          "name_uz": "Pop tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 64,
        "fields": {
          "code": 1612,
          "name": "To'raqo'rg'on district",
          "name_en": "To'raqo'rg'on district",
          "name_ru": "Туракурганский район",
          "name_uz": "To'raqo'rg'on tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 65,
        "fields": {
          "code": 1605,
          "name": "Uychi district",
          "name_en": "Uychi district",
          "name_ru": "Уйчинский район",
          "name_uz": "Uychi tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 66,
        "fields": {
          "code": 1606,
          "name": "Uchqo'rg'on district",
          "name_en": "Uchqo'rg'on district",
          "name_ru": "Учкурганский район",
          "name_uz": "Uchqo'rg'on tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 67,
        "fields": {
          "code": 1607,
          "name": "Chortoq district",
          "name_en": "Chortoq district",
          "name_ru": "Чартакский район",
          "name_uz": "Chortoq tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 68,
        "fields": {
          "code": 1610,
          "name": "Chust district",
          "name_en": "Chust district",
          "name_ru": "Чустский район",
          "name_uz": "Chust tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 69,
        "fields": {
          "code": 1608,
          "name": "Yangiqo'rg'on district",
          "name_en": "Yangiqo'rg'on district",
          "name_ru": "Янгикурганский район",
          "name_uz": "Yangiqo'rg'on tumani",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 70,
        "fields": {
          "code": 1407,
          "name": "Oqdaryo district",
          "name_en": "Oqdaryo district",
          "name_ru": "Акдарьинский район",
          "name_uz": "Oqdaryo tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 71,
        "fields": {
          "code": 1411,
          "name": "Bulung'ur district",
          "name_en": "Bulung'ur district",
          "name_ru": "Булунгурский район",
          "name_uz": "Bulung'ur tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 72,
        "fields": {
          "code": 1403,
          "name": "Jomboy district",
          "name_en": "Jomboy district",
          "name_ru": "Джамбайский район",
          "name_uz": "Jomboy tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 73,
        "fields": {
          "code": 1408,
          "name": "Ishtixon district",
          "name_en": "Ishtixon district",
          "name_ru": "Иштыханский район",
          "name_uz": "Ishtixon tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 74,
        "fields": {
          "code": 1406,
          "name": "Kattaqo'rg'on district",
          "name_en": "Kattaqo'rg'on district",
          "name_ru": "Каттакурганский район",
          "name_uz": "Kattaqo'rg'on tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 75,
        "fields": {
          "code": 1414,
          "name": "Qo'shrabot district",
          "name_en": "Qo'shrabot district",
          "name_ru": "Кошрабадский район",
          "name_uz": "Qo'shrabot tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 76,
        "fields": {
          "code": 1401,
          "name": "Narpay district",
          "name_en": "Narpay district",
          "name_ru": "Нарпайский район",
          "name_uz": "Narpay tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 77,
        "fields": {
          "code": 1415,
          "name": "Payariq district",
          "name_en": "Payariq district",
          "name_ru": "Пайарыкский район",
          "name_uz": "Payariq tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 78,
        "fields": {
          "code": 1409,
          "name": "Pastdarg'om district",
          "name_en": "Pastdarg'om district",
          "name_ru": "Пастдаргомский район",
          "name_uz": "Pastdarg'om tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 79,
        "fields": {
          "code": 1405,
          "name": "Paxtachi district",
          "name_en": "Paxtachi district",
          "name_ru": "Пахтачийский район",
          "name_uz": "Paxtachi tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 80,
        "fields": {
          "code": 1413,
          "name": "Samarqand district",
          "name_en": "Samarqand district",
          "name_ru": "Самаркандский район",
          "name_uz": "Samarqand tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 81,
        "fields": {
          "code": 1402,
          "name": "Nurobod district",
          "name_en": "Nurobod district",
          "name_ru": "Нурабадский район",
          "name_uz": "Nurobod tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 82,
        "fields": {
          "code": 1404,
          "name": "Urgut district",
          "name_en": "Urgut district",
          "name_ru": "Ургутский район",
          "name_uz": "Urgut tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 83,
        "fields": {
          "code": 1410,
          "name": "Tayloq district",
          "name_en": "Tayloq district",
          "name_ru": "Тайлякский район",
          "name_uz": "Tayloq tumani",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 84,
        "fields": {
          "code": 1907,
          "name": "Oltinsoy district",
          "name_en": "Oltinsoy district",
          "name_ru": "Алтынсайский район",
          "name_uz": "Oltinsoy tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 85,
        "fields": {
          "code": 1911,
          "name": "Angor district",
          "name_en": "Angor district",
          "name_ru": "Ангорский район",
          "name_uz": "Angor tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 86,
        "fields": {
          "code": 1915,
          "name": "Bandixon district",
          "name_en": "Bandixon district",
          "name_ru": "Бандихонский район",
          "name_uz": "Bandixon tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 87,
        "fields": {
          "code": 1902,
          "name": "Boysun district",
          "name_en": "Boysun district",
          "name_ru": "Байсунский район",
          "name_uz": "Boysun tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 88,
        "fields": {
          "code": 1903,
          "name": "Muzrabot district",
          "name_en": "Muzrabot district",
          "name_ru": "Музрабадский район",
          "name_uz": "Muzrabot tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 89,
        "fields": {
          "code": 1914,
          "name": "Denov district",
          "name_en": "Denov district",
          "name_ru": "Денауский район",
          "name_uz": "Denov tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 90,
        "fields": {
          "code": 1909,
          "name": "Jarqo'rg'on district",
          "name_en": "Jarqo'rg'on district",
          "name_ru": "Джаркурганский район",
          "name_uz": "Jarqo'rg'on tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 91,
        "fields": {
          "code": 1908,
          "name": "Qumqo'rg'on district",
          "name_en": "Qumqo'rg'on district",
          "name_ru": "Кумкурганский район",
          "name_uz": "Qumqo'rg'on tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 92,
        "fields": {
          "code": 1910,
          "name": "Qiziriq district",
          "name_en": "Qiziriq district",
          "name_ru": "Кизирикский район",
          "name_uz": "Qiziriq tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 93,
        "fields": {
          "code": 1904,
          "name": "Sariosiyo district",
          "name_en": "Sariosiyo district",
          "name_ru": "Сариасийский район",
          "name_uz": "Sariosiyo tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 94,
        "fields": {
          "code": 1901,
          "name": "Termiz district",
          "name_en": "Termiz district",
          "name_ru": "Термезский район",
          "name_uz": "Termiz tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 95,
        "fields": {
          "code": 1913,
          "name": "Uzun district",
          "name_en": "Uzun district",
          "name_ru": "Узунский район",
          "name_uz": "Uzun tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 96,
        "fields": {
          "code": 1912,
          "name": "Sherobod district",
          "name_en": "Sherobod district",
          "name_ru": "Шерабадский район",
          "name_uz": "Sherobod tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 97,
        "fields": {
          "code": 1906,
          "name": "Sho'rchi district",
          "name_en": "Sho'rchi district",
          "name_ru": "Шурчинский район",
          "name_uz": "Sho'rchi tumani",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 98,
        "fields": {
          "code": 1207,
          "name": "Oqoltin district",
          "name_en": "Oqoltin district",
          "name_ru": "Акалтынский район",
          "name_uz": "Oqoltin tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 99,
        "fields": {
          "code": 1203,
          "name": "Boyovut district",
          "name_en": "Boyovut district",
          "name_ru": "Баяутский район",
          "name_uz": "Boyovut tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 100,
        "fields": {
          "code": 1201,
          "name": "Sayxunobod district",
          "name_en": "Sayxunobod district",
          "name_ru": "Сайхунабадский район",
          "name_uz": "Sayxunobod tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 101,
        "fields": {
          "code": 1202,
          "name": "Guliston district",
          "name_en": "Guliston district",
          "name_ru": "Гулистанский район",
          "name_uz": "Guliston tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 102,
        "fields": {
          "code": 1215,
          "name": "Sardoba district",
          "name_en": "Sardoba district",
          "name_ru": "Сардобский район",
          "name_uz": "Sardoba tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 103,
        "fields": {
          "code": 1206,
          "name": "Mirzaobod district",
          "name_en": "Mirzaobod district",
          "name_ru": "Мирзаабадский район",
          "name_uz": "Mirzaobod tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 104,
        "fields": {
          "code": 1209,
          "name": "Sirdaryo district",
          "name_en": "Sirdaryo district",
          "name_ru": "Сырдарьинский район",
          "name_uz": "Sirdaryo tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 105,
        "fields": {
          "code": 1205,
          "name": "Xovos district",
          "name_en": "Xovos district",
          "name_ru": "Хавасский район",
          "name_uz": "Xovos tumani",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 106,
        "fields": {
          "code": 1001,
          "name": "Uchtepa district",
          "name_en": "Uchtepa district",
          "name_ru": "Учтепинский район",
          "name_uz": "Uchtepa tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 107,
        "fields": {
          "code": 1011,
          "name": "Bektemir district",
          "name_en": "Bektemir district",
          "name_ru": "Бектемирский район",
          "name_uz": "Bektemir tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 108,
        "fields": {
          "code": 1010,
          "name": "Yunusobod district",
          "name_en": "Yunusobod district",
          "name_ru": "Юнусабадский район",
          "name_uz": "Yunusobod tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 109,
        "fields": {
          "code": 1003,
          "name": "Mirzo Ulug'bek district",
          "name_en": "Mirzo Ulug'bek district",
          "name_ru": "Мирзо-Улугбекский район",
          "name_uz": "Mirzo Ulug'bek tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 110,
        "fields": {
          "code": 1009,
          "name": "Mirobod district",
          "name_en": "Mirobod district",
          "name_ru": "Мирабадский район",
          "name_uz": "Mirobod tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 111,
        "fields": {
          "code": 1006,
          "name": "Shayxontoxur district",
          "name_en": "Shayxontoxur district",
          "name_ru": "Шайхантахурский район",
          "name_uz": "Shayxontoxur tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 112,
        "fields": {
          "code": 1012,
          "name": "Olmazor district",
          "name_en": "Olmazor district",
          "name_ru": "Алмазарский район",
          "name_uz": "Olmazor tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 113,
        "fields": {
          "code": 1008,
          "name": "Sirg'ali district",
          "name_en": "Sirg'ali district",
          "name_ru": "Сергелийский район",
          "name_uz": "Sirg'ali tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 114,
        "fields": {
          "code": 1005,
          "name": "Yakkasaroy district",
          "name_en": "Yakkasaroy district",
          "name_ru": "Яккасарайский район",
          "name_uz": "Yakkasaroy tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 115,
        "fields": {
          "code": 1013,
          "name": "Yashnobod district",
          "name_en": "Yashnobod district",
          "name_ru": "Яшнободский район",
          "name_uz": "Yashnobod tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 116,
        "fields": {
          "code": 1007,
          "name": "Chilonzor district",
          "name_en": "Chilonzor district",
          "name_ru": "Чиланзарский район",
          "name_uz": "Chilonzor tumani",
          "region_id": 10,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 117,
        "fields": {
          "code": 1106,
          "name": "Oqqo'rg'on district",
          "name_en": "Oqqo'rg'on district",
          "name_ru": "Аккурганский район",
          "name_uz": "Oqqo'rg'on tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 118,
        "fields": {
          "code": 1110,
          "name": "Ohangaron district",
          "name_en": "Ohangaron district",
          "name_ru": "Ахангаранский район",
          "name_uz": "Ohangaron tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 119,
        "fields": {
          "code": 1111,
          "name": "Bekobod district",
          "name_en": "Bekobod district",
          "name_ru": "Бекабадский район",
          "name_uz": "Bekobod tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 120,
        "fields": {
          "code": 1112,
          "name": "Bo'stonliq district",
          "name_en": "Bo'stonliq district",
          "name_ru": "Бостанлыкский район",
          "name_uz": "Bo'stonliq tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 121,
        "fields": {
          "code": 1113,
          "name": "Bo'ka district",
          "name_en": "Bo'ka district",
          "name_ru": "Букинский район",
          "name_uz": "Bo'ka tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 122,
        "fields": {
          "code": 1107,
          "name": "Qiyichirchiq district",
          "name_en": "Qiyichirchiq district",
          "name_ru": "Куйичирчикский район",
          "name_uz": "Qiyichirchiq tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 123,
        "fields": {
          "code": 1102,
          "name": "Zangiota district",
          "name_en": "Zangiota district",
          "name_ru": "Зангиатинский район",
          "name_uz": "Zangiota tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 124,
        "fields": {
          "code": 1114,
          "name": "Yuqorichirchiq district",
          "name_en": "Yuqorichirchiq district",
          "name_ru": "Юкоричирчикский район",
          "name_uz": "Yuqorichirchiq tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 125,
        "fields": {
          "code": 1108,
          "name": "Qibray district",
          "name_en": "Qibray district",
          "name_ru": "Кибрайский район",
          "name_uz": "Qibray tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 126,
        "fields": {
          "code": 1104,
          "name": "Parkent district",
          "name_en": "Parkent district",
          "name_ru": "Паркентский район",
          "name_uz": "Parkent tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 127,
        "fields": {
          "code": 1103
          ,
          "name": "Pskent district",
          "name_en": "Pskent district",
          "name_ru": "Пскентский район",
          "name_uz": "Pskent tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 128,
        "fields": {
          "code": 1105,
          "name": "O'rtachirchiq district",
          "name_en": "O'rtachirchiq district",
          "name_ru": "Уртачирчикский район",
          "name_uz": "O'rtachirchiq tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 129,
        "fields": {
          "code": 1115,
          "name": "Chinoz district",
          "name_en": "Chinoz district",
          "name_ru": "Чиназский район",
          "name_uz": "Chinoz tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 130,
        "fields": {
          "code": 1101,
          "name": "Yangiyo'l district",
          "name_en": "Yangiyo'l district",
          "name_ru": "Янгиюльский район",
          "name_uz": "Yangiyo'l tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 131,
        "fields": {
          "code": 1109,
          "name": "Toshkent district",
          "name_en": "Toshkent district",
          "name_ru": "Ташкентский район",
          "name_uz": "Toshkent tumani",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 132,
        "fields": {
          "code": 1507,
          "name": "Oltiariq district",
          "name_en": "Oltiariq district",
          "name_ru": "Алтыарыкский район",
          "name_uz": "Oltiariq tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 133,
        "fields": {
          "code": 2434,
          "name": "Qo'shtepa district",
          "name_en": "Qo'shtepa district",
          "name_ru": "Куштепинский район",
          "name_uz": "Qo'shtepa tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 134,
        "fields": {
          "code": 1508,
          "name": "Bog'dod district",
          "name_en": "Bog'dod district",
          "name_ru": "Багдадский район",
          "name_uz": "Bog'dod tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 135,
        "fields": {
          "code": 1509,
          "name": "Buvayda district",
          "name_en": "Buvayda district",
          "name_ru": "Бувайдинский район",
          "name_uz": "Buvayda tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 136,
        "fields": {
          "code": 1515,
          "name": "Beshariq district",
          "name_en": "Beshariq district",
          "name_ru": "Бешарыкский район",
          "name_uz": "Beshariq tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 137,
        "fields": {
          "code": 1503,
          "name": "Quva district",
          "name_en": "Quva district",
          "name_ru": "Кувинский район",
          "name_uz": "Quva tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 138,
        "fields": {
          "code": 1510,
          "name": "Uchko'prik district",
          "name_en": "Uchko'prik district",
          "name_ru": "Учкуприкский район",
          "name_uz": "Uchko'prik tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 139,
        "fields": {
          "code": 1511,
          "name": "Rishton district",
          "name_en": "Rishton district",
          "name_ru": "Риштанский район",
          "name_uz": "Rishton tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 140,
        "fields": {
          "code": 1516,
          "name": "So'x district",
          "name_en": "So'x district",
          "name_ru": "Сохский район",
          "name_uz": "So'x tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 141,
        "fields": {
          "code": 1504,
          "name": "Toshloq district",
          "name_en": "Toshloq district",
          "name_ru": "Ташлакский район",
          "name_uz": "Toshloq tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 142,
        "fields": {
          "code": 1514,
          "name": "O'zbekiston district",
          "name_en": "O'zbekiston district",
          "name_ru": "Узбекистанский район",
          "name_uz": "O'zbekiston tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 143,
        "fields": {
          "code": 1502,
          "name": "Farg'ona district",
          "name_en": "Farg'ona district",
          "name_ru": "Ферганский район",
          "name_uz": "Farg'ona tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 144,
        "fields": {
          "code": 1512,
          "name": "Dang'ara district",
          "name_en": "Dang'ara district",
          "name_ru": "Дангаринский район",
          "name_uz": "Dang'ara tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 145,
        "fields": {
          "code": 1513,
          "name": "Furqat district",
          "name_en": "Furqat district",
          "name_ru": "Фуркатский район",
          "name_uz": "Furqat tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 146,
        "fields": {
          "code": 1506,
          "name": "Yozyovon district",
          "name_en": "Yozyovon district",
          "name_ru": "Язъяванский район",
          "name_uz": "Yozyovon tumani",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 147,
        "fields": {
          "code": 1508,
          "name": "Bog'ot district",
          "name_en": "Bog'ot district",
          "name_ru": "Багатский район",
          "name_uz": "Bog'ot tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 148,
        "fields": {
          "code": 2203,
          "name": "Gurlan district",
          "name_en": "Gurlan district",
          "name_ru": "Гурленский район",
          "name_uz": "Gurlan tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 149,
        "fields": {
          "code": 2209,
          "name": "Qo'shko'pir district",
          "name_en": "Qo'shko'pir district",
          "name_ru": "Кошкупырский район",
          "name_uz": "Qo'shko'pir tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 150,
        "fields": {
          "code": 2204,
          "name": "Urganch district",
          "name_en": "Urganch district",
          "name_ru": "Ургенчский район",
          "name_uz": "Urganch tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 151,
        "fields": {
          "code": 2201,
          "name": "Xazorasp district",
          "name_en": "Xazorasp district",
          "name_ru": "Хазараспский район",
          "name_uz": "Xazorasp tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 152,
        "fields": {
          "code": 0,
          "name": "Tuproqqal'a district",
          "name_en": "Tuproqqal'a district",
          "name_ru": "Тупроккалинский район",
          "name_uz": "Tuproqqal'a tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 153,
        "fields": {
          "code": 2206,
          "name": "Xonqa district",
          "name_en": "Xonqa district",
          "name_ru": "Ханкинский район",
          "name_uz": "Xonqa tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 154,
        "fields": {
          "code": 2210,
          "name": "Xiva district",
          "name_en": "Xiva district",
          "name_ru": "Хивинский район",
          "name_uz": "Xiva tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 155,
        "fields": {
          "code": 2205,
          "name": "Shovot district",
          "name_en": "Shovot district",
          "name_ru": "Шаватский район",
          "name_uz": "Shovot tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 156,
        "fields": {
          "code": 2202,
          "name": "Yangiariq district",
          "name_en": "Yangiariq district",
          "name_ru": "Янгиарыкский район",
          "name_uz": "Yangiariq tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 157,
        "fields": {
          "code": 2208,
          "name": "Yangibozor district",
          "name_en": "Yangibozor district",
          "name_ru": "Янгибазарский район",
          "name_uz": "Yangibozor tumani",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 158,
        "fields": {
          "code": 2308,
          "name": "Amudaryo district",
          "name_en": "Amudaryo district",
          "name_ru": "Амударьинский район",
          "name_uz": "Amudaryo tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 159,
        "fields": {
          "code": 2309,
          "name": "Beruniy district",
          "name_en": "Beruniy district",
          "name_ru": "Берунийский район",
          "name_uz": "Beruniy tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 160,
        "fields": {
          "code": 2324,
          "name": "Bo'zatov district",
          "name_en": "Bo'zatov district",
          "name_ru": "Бозатауский район",
          "name_uz": "Bo'zatov tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 161,
        "fields": {
          "code": 2316,
          "name": "Qorao'zak district",
          "name_en": "Qorao'zak district",
          "name_ru": "Караузякский район",
          "name_uz": "Qorao'zak tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 162,
        "fields": {
          "code": 2307,
          "name": "Kegeyli district",
          "name_en": "Kegeyli district",
          "name_ru": "Кегейлийский район",
          "name_uz": "Kegeyli tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 163,
        "fields": {
          "code": 2302,
          "name": "Qo'ng'irot district",
          "name_en": "Qo'ng'irot district",
          "name_ru": "Кунградский район",
          "name_uz": "Qo'ng'irot tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 164,
        "fields": {
          "code": 2310,
          "name": "Qanliko'l district",
          "name_en": "Qanliko'l district",
          "name_ru": "Канлыкульский район",
          "name_uz": "Qanliko'l tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 165,
        "fields": {
          "code": 2303,
          "name": "Mo'ynoq district",
          "name_en": "Mo'ynoq district",
          "name_ru": "Муйнакский район",
          "name_uz": "Mo'ynoq tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 166,
        "fields": {
          "code": 2301,
          "name": "Nukus district",
          "name_en": "Nukus district",
          "name_ru": "Нукусский район",
          "name_uz": "Nukus tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 167,
        "fields": {
          "code": 2320,
          "name": "Taxiatosh district",
          "name_en": "Taxiatosh district",
          "name_ru": "Тахиаташский район",
          "name_uz": "Taxiatosh tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 168,
        "fields": {
          "code": 2313,
          "name": "Taxtako'pir district",
          "name_en": "Taxtako'pir district",
          "name_ru": "Тахтакупырский район",
          "name_uz": "Taxtako'pir tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 169,
        "fields": {
          "code": 2305,
          "name": "To'rtko'l district",
          "name_en": "To'rtko'l district",
          "name_ru": "Турткульский район",
          "name_uz": "To'rtko'l tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 170,
        "fields": {
          "code": 2314,
          "name": "Xo'jayli district",
          "name_en": "Xo'jayli district",
          "name_ru": "Ходжейлийский район",
          "name_uz": "Xo'jayli tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 171,
        "fields": {
          "code": 2311,
          "name": "Chimboy district",
          "name_en": "Chimboy district",
          "name_ru": "Чимбайский район",
          "name_uz": "Chimboy tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 172,
        "fields": {
          "code": 2312,
          "name": "Shumanay district",
          "name_en": "Shumanay district",
          "name_ru": "Шуманайский район",
          "name_uz": "Shumanay tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 173,
        "fields": {
          "code": 2306,
          "name": "Ellikkala district",
          "name_en": "Ellikkala district",
          "name_ru": "Элликкалинский район",
          "name_uz": "Ellikkala tumani",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 174,
        "fields": {
          "code": 1715,
          "name": "Andijon city",
          "name_en": "Andijon city",
          "name_ru": "город Андижан",
          "name_uz": "Andijon shahri",
          "region_id": 1,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 175,
        "fields": {
          "code": 2013,
          "name": "Buxoro city",
          "name_en": "Buxoro city",
          "name_ru": "город Бухара",
          "name_uz": "Buxoro shahri",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 176,
        "fields": {
          "code": 2015,
          "name": "Kogon city",
          "name_en": "Kogon city",
          "name_ru": "город Каган",
          "name_uz": "Kogon shahri",
          "region_id": 2,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 177,
        "fields": {
          "code": 1314,
          "name": "Jizzax city",
          "name_en": "Jizzax city",
          "name_ru": "город Джизак",
          "name_uz": "Jizzax shahri",
          "region_id": 3,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 178,
        "fields": {
          "code": 1815,
          "name": "Qarshi city",
          "name_en": "Qarshi city",
          "name_ru": "город Карши",
          "name_uz": "Qarshi shahri",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 179,
        "fields": {
          "code": 2111,
          "name": "Navoiy city",
          "name_en": "Navoiy city",
          "name_ru": "город Навои",
          "name_uz": "Navoiy shahri",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 180,
        "fields": {
          "code": 2112,
          "name": "Zarafshon city",
          "name_en": "Zarafshon city",
          "name_ru": "город Зарафшан",
          "name_uz": "Zarafshon shahri",
          "region_id": 5,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 181,
        "fields": {
          "code": 1613,
          "name": "Namangan city",
          "name_en": "Namangan city",
          "name_ru": "город Наманган",
          "name_uz": "Namangan shahri",
          "region_id": 6,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 182,
        "fields": {
          "code": 1421,
          "name": "The city of Kattakurgan",
          "name_en": "The city of Kattakurgan",
          "name_ru": "город Каттакурган",
          "name_uz": "Kattaqo'rg'on shahri",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 183,
        "fields": {
          "code": 1916,
          "name": "Termiz city",
          "name_en": "Termiz city",
          "name_ru": "город Термез",
          "name_uz": "Termiz shahri",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 184,
        "fields": {
          "code": 1210,
          "name": "Guliston city",
          "name_en": "Guliston city",
          "name_ru": "город Гулистан",
          "name_uz": "Guliston shahri",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 185,
        "fields": {
          "code": 1212,
          "name": "Shirin city",
          "name_en": "Shirin city",
          "name_ru": "город Ширин",
          "name_uz": "Shirin shahri",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 186,
        "fields": {
          "code": 1213,
          "name": "Yangiyer city",
          "name_en": "Yangiyer city",
          "name_ru": "город Янгиер",
          "name_uz": "Yangiyer shahri",
          "region_id": 9,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 187,
        "fields": {
          "code": 1118,
          "name": "Olmaliq city",
          "name_en": "Olmaliq city",
          "name_ru": "город Алмалык",
          "name_uz": "Olmaliq shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 188,
        "fields": {
          "code": 1116,
          "name": "Angren city",
          "name_en": "Angren city",
          "name_ru": "город Ангрен",
          "name_uz": "Angren shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 189,
        "fields": {
          "code": 1117,
          "name": "Bekobod city",
          "name_en": "Bekobod city",
          "name_ru": "город Бекабад",
          "name_uz": "Bekobod shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 190,
        "fields": {
          "code": 1120,
          "name": "Chirchiq city",
          "name_en": "Chirchiq city",
          "name_ru": "город Чирчик",
          "name_uz": "Chirchiq shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 191,
        "fields": {
          "code": 1521,
          "name": "Farg'ona city",
          "name_en": "Farg'ona city",
          "name_ru": "город Фергана",
          "name_uz": "Farg'on shahri",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 192,
        "fields": {
          "code": 1519,
          "name": "Qo'qon city",
          "name_en": "Qo'qon city",
          "name_ru": "город Коканд",
          "name_uz": "Qo'qon shahri",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 193,
        "fields": {
          "code": 1517,
          "name": "Quvasoy city",
          "name_en": "Quvasoy city",
          "name_ru": "город Кувасай",
          "name_uz": "Quvasoy shahri",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 194,
        "fields": {
          "code": 1520,
          "name": "Marg'ilon city",
          "name_en": "Marg'ilon city",
          "name_ru": "город Маргилан",
          "name_uz": "Marg'ilon shahri",
          "region_id": 12,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 195,
        "fields": {
          "code": 2211,
          "name": "Urganch city",
          "name_en": "Urganch city",
          "name_ru": "город Ургенч",
          "name_uz": "Urganch shahri",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 196,
        "fields": {
          "code": 1717,
          "name": "Xonobod city",
          "name_en": "Xonobod city",
          "name_ru": "город Ханабад",
          "name_uz": "Xonobod shahri",
          "region_id": 8,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 197,
        "fields": {
          "code": 2317,
          "name": "Nukus city",
          "name_en": "Nukus city",
          "name_ru": "город Нукус",
          "name_uz": "Nukus shahri",
          "region_id": 14,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 198,
        "fields": {
          "code": 1119,
          "name": "Ohangaron city",
          "name_en": "Ohangaron city",
          "name_ru": "город Ахангаран",
          "name_uz": "Ohangaron shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 199,
        "fields": {
          "code": 1122,
          "name": "Yangiyo'l city",
          "name_en": "Yangiyo'l city",
          "name_ru": "город Янгиюль",
          "name_uz": "Yangiyo'l shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 200,
        "fields": {
          "code": 1123,
          "name": "Nurafshon city",
          "name_en": "Nurafshon city",
          "name_ru": "город Нурафшан",
          "name_uz": "Nurafshon shahri",
          "region_id": 11,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 201,
        "fields": {
          "code": 1803,
          "name": "Shaxrisabz city",
          "name_en": "Shaxrisabz city",
          "name_ru": "город Шахрисабз",
          "name_uz": "Shaxrisabz shahri",
          "region_id": 4,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 20,
        "fields": {
          "code": 2212,
          "name": "Xiva city",
          "name_en": "Xiva city",
          "name_ru": "город Хива",
          "name_uz": "Xiva shahri",
          "region_id": 13,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      },
      {
        "model": "directory.District",
        "pk": 203,
        "fields": {
          "code": 1417,
          "name": "Samarqand city",
          "name_en": "Samarqand city",
          "name_ru": "город Самарканд",
          "name_uz": "Samarqand shahri",
          "region_id": 7,
          "created_time": "2020-01-01 00:00:00+00:00",
          "updated_time": "2020-01-01 00:00:00+00:00",
          "created_by": 1
        }
      }
    ]

        for item in json_data:
            fields = item['fields']
            region = Region.objects.get(id=fields['region_id'])

            # Prepare the data for serializer
            district_data = {
                'code': fields['code'],
                'name': fields['name'],
                'name_uz': fields['name_uz'],
                'name_ru': fields['name_ru'],
                'name_en': fields['name_en'],
                'region': region.id  # Pass the region id
            }

            # Instantiate the serializer with the data
            serializer = DistrictSerializer(data=district_data)

            # Validate and save the data if valid
            if serializer.is_valid():
                serializer.save()
                print(f"District {fields['name']} created successfully.")
            else:
                # Handle validation errors
                print(f"Validation errors: {serializer.errors}")
        return Response({}, status.HTTP_201_CREATED)


class DistrictDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        return District.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        district = get_object_or_404(District, id=pk)
        serializer = DistrictListSerializer(district)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        district = get_object_or_404(District, id=pk)
        serializer = self.serializer_class(district, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

