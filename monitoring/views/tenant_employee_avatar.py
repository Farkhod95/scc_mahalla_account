from celery.result import AsyncResult
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.tasks import sync_employee_avatars_from_long_term


class SyncTenantEmployeeAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task = sync_employee_avatars_from_long_term.delay()

        return Response(
            {
                "ok": True,
                "message": "TenantEmployee avatar sync task ishga tushirildi",
                "task_id": task.id,
                "status_url": f"/api/v1/tenant-employee/sync-avatars/status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED
        )


class SyncTenantEmployeeAvatarStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)

        data = {
            "ok": True,
            "task_id": task_id,
            "state": result.state,
        }

        if result.state == "PENDING":
            data["message"] = "Task navbatda"
        elif result.state == "STARTED":
            data["message"] = "Task ishlayapti"
        elif result.state == "SUCCESS":
            data["message"] = "Task muvaffaqiyatli tugadi"
            data["result"] = result.result
        elif result.state == "FAILURE":
            data["ok"] = False
            data["message"] = "Task xatolik bilan tugadi"
            data["error"] = str(result.result)
        else:
            data["message"] = result.state

        return Response(data, status=status.HTTP_200_OK)