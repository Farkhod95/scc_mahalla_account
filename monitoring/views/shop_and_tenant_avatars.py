from celery.result import AsyncResult
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.tasks import (
    sync_shop_owner_avatars_task,
    sync_shop_tenant_leader_avatars_task,
)


class SyncShopOwnerAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task = sync_shop_owner_avatars_task.delay()
        return Response(
            {
                "ok": True,
                "message": "Shop owner avatar sync task ishga tushirildi",
                "task_id": task.id,
                "status_url": f"/api/v1/shop/sync-owner-avatars/status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED
        )


class SyncShopOwnerAvatarStatusAPIView(APIView):
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


class SyncShopTenantLeaderAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task = sync_shop_tenant_leader_avatars_task.delay()
        return Response(
            {
                "ok": True,
                "message": "ShopTenant leader avatar sync task ishga tushirildi",
                "task_id": task.id,
                "status_url": f"/api/v1/shop-tenant/sync-leader-avatars/status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED
        )


class SyncShopTenantLeaderAvatarStatusAPIView(APIView):
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