import os

from celery.result import AsyncResult
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.tasks import import_shop_excel_task


class ShopExcelImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Papkadagi tayyor excel faylni olib background taskga yuboradi.
        Request body yuborish shart emas.

        Ixtiyoriy:
        {
            "file_name": "malika_shablon.xlsx"
        }
        """

        file_name = request.data.get("file_name") or "malika_shablon.xlsx"

        # monitoring/uploads ichidan oladi
        absolute_file_path = os.path.join(
            settings.BASE_DIR,
            "monitoring",
            "uploads",
            file_name
        )

        if not os.path.exists(absolute_file_path):
            return Response(
                {
                    "status": "error",
                    "message": "Fayl topilmadi.",
                    "file_name": file_name,
                    "file_path": absolute_file_path,
                },
                status=status.HTTP_404_NOT_FOUND
            )

        task = import_shop_excel_task.delay(absolute_file_path)

        return Response(
            {
                "message": "Excel import background taskga yuborildi.",
                "task_id": task.id,
                "file_name": file_name,
                "file_path": absolute_file_path,
                "status_url": f"http://192.168.168.149:8080/api/v1/shops/import-excel/status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED
        )


class ShopExcelImportStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "state": result.state,
        }

        if result.state == "PENDING":
            response_data["message"] = "Task navbatda."
        elif result.state == "STARTED":
            response_data["message"] = "Task ishlayapti."
        elif result.state == "SUCCESS":
            response_data["message"] = "Task muvaffaqiyatli tugadi."
            response_data["result"] = result.result
        elif result.state == "FAILURE":
            response_data["message"] = "Task xatolik bilan tugadi."
            response_data["error"] = str(result.result)
        else:
            response_data["message"] = result.state

        return Response(response_data, status=status.HTTP_200_OK)