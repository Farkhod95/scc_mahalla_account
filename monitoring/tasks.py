import logging
from celery import shared_task
from django.conf import settings

from monitoring.services.patrol_car_sync import sync_patrol_cars_from_api


@shared_task
def sync_patrol_cars_task():
    api_url = "http://25.1.1.217:80/api/mobject/lastData"
    token = "6bq6kimsmhniuothjbkai715n2"
    timeout = 20

    if not api_url:
        return {"ok": False, "error": "PATROL_CAR_LASTDATA_URL is not set"}

    stats = sync_patrol_cars_from_api(api_url=api_url, timeout=timeout, token=token)
    return {
        "ok": True,
        "fetched": stats.fetched,
        "created": stats.created,
        "updated": stats.updated,
        "skipped_no_imei": stats.skipped_no_imei,
        "errors": stats.errors,
    }
