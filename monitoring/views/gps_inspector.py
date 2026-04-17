from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from monitoring.serializer.gps_inspector import (
    GPSInspectorDistrictSerializer,
    GPSInspectorMFYSerializer,
    GPSInspectorItemSerializer,
)
from monitoring.services.gps_inspector import GPSInspectorService


class GPSInspectorDistrictListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        result = GPSInspectorService.get_districts()

        if not result["success"]:
            return Response(
                {
                    "success": False,
                    "message": "Districtlar ro‘yxatini olishda xatolik yuz berdi",
                    "error": result["error"],
                },
                status=result["status_code"],
            )

        payload = result["data"]
        items = payload.get("data", [])

        serializer = GPSInspectorDistrictSerializer(items, many=True, context={"request": request})

        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "total": payload.get("total", len(serializer.data)),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GPSInspectorMFYListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page = 1

        try:
            limit = int(request.query_params.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100

        district_cad_code = request.query_params.get("district_cad_code")
        mfy_cad_code = request.query_params.get("mfy_cad_code")

        if page < 1:
            return Response(
                {"success": False, "message": "page 1 dan kichik bo‘lmasligi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if limit < 1 or limit > 50000:
            return Response(
                {"success": False, "message": "limit 1 va 50000 oralig‘ida bo‘lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = GPSInspectorService.get_mfys(
            page=page,
            limit=limit,
            district_cad_code=district_cad_code,
            mfy_cad_code=mfy_cad_code,
        )

        if not result["success"]:
            return Response(
                {
                    "success": False,
                    "message": "MFYlar ro‘yxatini olishda xatolik yuz berdi",
                    "error": result["error"],
                },
                status=result["status_code"],
            )

        payload = result["data"]
        items = payload.get("data", [])
        meta = payload.get("meta", {})

        serializer = GPSInspectorMFYSerializer(items, many=True, context={"request": request})

        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "meta": meta,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GPSInspectorByMFYView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, mfy_id, *args, **kwargs):
        minutes = request.query_params.get("minutes")

        if minutes is not None:
            try:
                minutes = int(minutes)
                if minutes < 1:
                    return Response(
                        {"success": False, "message": "minutes 1 dan kichik bo‘lmasligi kerak"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "message": "minutes butun son bo‘lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        result = GPSInspectorService.get_gps_inspectors_by_mfy(mfy_id=mfy_id, minutes=minutes)

        if not result["success"]:
            return Response(
                {
                    "success": False,
                    "message": "Inspectorlar GPS ma'lumotini olishda xatolik yuz berdi",
                    "error": result["error"],
                },
                status=result["status_code"],
            )

        payload = result["data"]
        items = payload.get("data", [])

        serializer = GPSInspectorItemSerializer(items, many=True, context={"request": request})

        return Response(
            {
                "success": True,
                "mfy_id": str(mfy_id),
                "count": len(serializer.data),
                "ts": payload.get("ts"),
                "request_id": payload.get("requestId"),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )