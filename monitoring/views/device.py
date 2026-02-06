from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from django.db.models import Count

from monitoring.filterset import DeviceFilter
from monitoring.models import Device, Object
from monitoring.serializers import DeviceSerializer, DeviceListSerializer, DeviceListForMapSerializer

from restapp.pagination import ResultsSetPagination
from restapp.utils.responses import nonContent


from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from monitoring.models import Device

class DeviceForMapView(APIView):
    def get(self, request):
        region_id = request.query_params.get('region_id')
        device_year_id = request.query_params.get('device_year_id')
        device_type_id = request.query_params.get('device_type_id')

        queryset = Device.objects.select_related(
            'device_year'
        ).filter(coordinate_x__isnull=False, coordinate_y__isnull=False)

        if region_id:
            queryset = queryset.filter(region_id=region_id)

        if device_year_id:
            queryset = queryset.filter(device_year_id=device_year_id)

        if device_type_id:
            queryset = queryset.filter(device_type_id=device_type_id)

        devices = queryset.values(
            'id',
            'coordinate_x',
            'coordinate_y',
            'device_type__key',
            'device_year__id',
            'device_year__color',
            'device_year__number',
            'address',
        )

        grouped_data = defaultdict(lambda: {
            'device_year_id': None,
            'device_year_color': None,
            'device_year_number': None,
            'devices': []
        })

        for d in devices:
            dy_id = d['device_year__id']
            if grouped_data[dy_id]['device_year_id'] is None:
                grouped_data[dy_id]['device_year_id'] = dy_id
                grouped_data[dy_id]['device_year_color'] = d['device_year__color']
                grouped_data[dy_id]['device_year_number'] = d['device_year__number']

            grouped_data[dy_id]['devices'].append({
                'id': d['id'],
                'coordinate_x': d['coordinate_x'],
                'coordinate_y': d['coordinate_y'],
                'device_type': d['device_type__key'],
                'address': d['address'],
            })

        return Response(list(grouped_data.values()))



class DeviceView(ListCreateAPIView):
    serializer_class = DeviceListSerializer
    pagination_class = ResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = DeviceFilter
    search_fields = ('name', 'project__name', 'ip_address', 'speed_limit', 'device_number',
                     'project_step__name', 'region__name', 'district__name', 'project_parent__name')
    ordering = ['-pk']

    def get_queryset(self):
        return Device.objects.all()

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)


class DeviceDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return Device.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get(self, request, pk):
        instance = get_object_or_404(Device, id=pk)
        serializer = DeviceListForMapSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        instance = get_object_or_404(Device, id=pk)
        serializer = self.serializer_class(instance, data=request.data, context={'request': request})
        # serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        instance = get_object_or_404(Device, id=pk)
        instance.delete()
        return Response(nonContent(), status.HTTP_204_NO_CONTENT)


class DeviceSummaryStatsAPIView(APIView):
    def get(self, request):
        # GET parametrlardan olish
        device_year_array_str = request.GET.get('device_year_array')
        region_id = request.GET.get('region_id')

        device_year_ids = []
        if device_year_array_str:
            try:
                device_year_ids = list(map(int, device_year_array_str.split(',')))
            except Exception:
                return Response({"error": "Invalid device_year_array values."}, status=400)

        # Ob'ektlar uchun filter
        object_filter = {}
        device_filter = {}

        if device_year_ids:
            object_filter["device_year_id__in"] = device_year_ids
            device_filter["device_year_id__in"] = device_year_ids

        if region_id:
            object_filter["region_id"] = region_id
            device_filter["region_id"] = region_id

        total_objects = Object.objects.filter(**object_filter).count()
        device_qs = Device.objects.filter(**device_filter)

        # Qurilmalarni device_type__key bo‘yicha sanash
        device_type_counts = (
            device_qs
            .values("device_type__key")
            .annotate(count=Count("id"))
        )

        # Hisoblash
        stats = {item["device_type__key"]: item["count"] for item in device_type_counts}
        total_faces = stats.get("face_soni", 0)
        total_directed = stats.get("yonaltirilgan_soni", 0)
        total_drb = stats.get("drb_soni", 0)
        total_ptz = stats.get("ptz_soni", 0)

        # Natija
        response_data = {
            'total_objects': total_objects,
            'total_cameras': total_faces + total_directed + total_drb + total_ptz,
            "total_faces": total_faces,
            "total_directed": total_directed,
            "total_drb": total_drb,
            "total_ptz": total_ptz,
        }
        return Response(response_data)


# class DeviceSummaryStatsAPIView(APIView):
#     def get(self, request):
#
#         device_year_array_str = request.GET.get('device_year_array')
#         device_year_ids = []
#
#         if device_year_array_str:
#             try:
#                 device_year_ids = list(map(int, device_year_array_str.split(',')))
#             except Exception:
#                 return Response({"error": "Invalid device_year_array values."}, status=400)
#
#         if device_year_ids:
#             total_objects = Object.objects.filter(device_year_id__in=device_year_ids).count()
#             device_qs = Device.objects.filter(device_year_id__in=device_year_ids)
#         else:
#             total_objects = Object.objects.count()
#             device_qs = Device.objects.all()
#
#         # total_objects = Object.objects.count()
#
#         # Barcha kameralarni device_type.key bo‘yicha guruhlab sanaymiz
#         device_type_counts = (
#             device_qs
#             .values("device_type__key")
#             .annotate(count=Count("id"))
#         )
#
#         # Natijalarni dict ga o‘tkazish
#         stats = {item["device_type__key"]: item["count"] for item in device_type_counts}
#
#         total_faces = stats.get("face_soni", 0)
#         total_directed = stats.get("yonaltirilgan_soni", 0)
#         total_drb = stats.get("drb_soni", 0)
#         total_ptz = stats.get("ptz_soni", 0)
#
#         response_data = {
#             'total_objects': total_objects,
#             'total_cameras': total_faces + total_directed + total_drb + total_ptz,
#             "total_faces": total_faces,
#             "total_directed": total_directed,
#             "total_drb": total_drb,
#             "total_ptz": total_ptz,
#         }
#         return Response(response_data)


class UpdateLocationAPIView(APIView):
    def post(self, request):
        updated = 0
        skipped = 0

        devices = Device.objects.exclude(coordinate_x=None).exclude(coordinate_y=None)

        for device in devices.iterator():  # iterator - katta dataset uchun samarali
            try:
                lat = float(device.coordinate_x)
                lon = float(device.coordinate_y)
                device.save(update_fields=['location'])
                updated += 1
            except Exception as e:
                skipped += 1

        return Response({
            'success': True,
            'updated_count': updated,
            'skipped_count': skipped,
        }, status=status.HTTP_200_OK)




