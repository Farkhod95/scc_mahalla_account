import os
import uuid

from celery.result import AsyncResult
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.serializers import ShopExcelImportSerializer
from monitoring.tasks import import_shop_excel_task


class ShopExcelImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ShopExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        excel_file = serializer.validated_data["file"]

        ext = os.path.splitext(excel_file.name)[1]
        filename = f"shop_imports/{uuid.uuid4().hex}{ext}"

        saved_path = default_storage.save(filename, excel_file)
        absolute_file_path = default_storage.path(saved_path)

        task = import_shop_excel_task.delay(absolute_file_path)

        return Response(
            {
                "message": "Excel import background taskga yuborildi.",
                "task_id": task.id,
                "status_url": f"/api/v1/shops/import-excel/status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED
        )


class ShopExcelImportStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)

        data = {
            "task_id": task_id,
            "state": result.state,
        }

        if result.state == "PENDING":
            data["message"] = "Task navbatda."
        elif result.state == "STARTED":
            data["message"] = "Task ishlayapti."
        elif result.state == "SUCCESS":
            data["message"] = "Task muvaffaqiyatli tugadi."
            data["result"] = result.result
        elif result.state == "FAILURE":
            data["message"] = "Task xatolik bilan tugadi."
            data["error"] = str(result.result)
        else:
            data["message"] = result.state

        return Response(data, status=status.HTTP_200_OK)