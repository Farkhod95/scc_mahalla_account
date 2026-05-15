from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import CarFlow
from monitoring.serializer.car_flow import CarFlowCreateSerializer, CarFlowListSerializer
from restapp.pagination import ResultsSetPagination

CAR_FLOW_API_KEY = "f441ad4eb7cf8d5f3f474162baa49a30cda1e3c5643e6701e6077d727c75984e"


class CarFlowView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return [IsAuthenticated()]

    def _check_api_key(self, request):
        key = request.headers.get('X-Api-Key') or request.query_params.get('api_key')
        return key == CAR_FLOW_API_KEY

    def get(self, request):
        qs = CarFlow.objects.all()

        location_type = request.query_params.get('location_type')
        if location_type:
            qs = qs.filter(location_type=location_type)

        ip_address = request.query_params.get('ip_address')
        if ip_address:
            qs = qs.filter(ip_address=ip_address)

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        if from_date:
            qs = qs.filter(recorded_at__gte=from_date)
        if to_date:
            qs = qs.filter(recorded_at__lte=to_date)

        paginator = ResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CarFlowListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not self._check_api_key(request):
            return Response({'detail': 'Invalid or missing API key.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CarFlowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
