import logging
from celery import shared_task
from typing import Optional, Tuple, Dict, Any, List

from monitoring.models import TenantEmployee
from monitoring.services.citizen_avatar import fetch_citizen_avatar_file
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


@shared_task(bind=True, name="celery_task.sync_employee_avatars_from_long_term")
def sync_employee_avatars_from_long_term(self) -> Dict[str, Any]:
    """
    Background task:
    LongTermDepartedChild -> employee.pinfl -> external API -> image(file) -> employee.avatar
    """
    qs = TenantEmployee.objects.all()


    results: List[Dict[str, Any]] = []
    saved = 0
    failed = 0

    # Katta transaction shart emas. Har bir yozuvni alohida saqlash xavfsizroq.
    idx = 0
    for employee in qs:
        idx += 1
        pinfl = employee.jshshir
        if employee.avatar:
            print(f"[SYNC_AVATAR] ({idx}) SKIPda allaqachon avatar boremployee_id={employee.id}", flush=True)
            continue

        try:
            fetched = fetch_citizen_avatar_file(pinfl)
            if not fetched:
                failed += 1
                results.append({
                    "jshshir": pinfl,
                    "employee_id": employee.id,
                    "ok": False,
                    "avatar": None,
                    "detail": "Rasm topilmadi yoki servis xato qaytardi",
                })
                continue

            filename, file_obj = fetched

            # faqat avatarni saqlaymiz (DB save bo‘ladi)
            employee.avatar.save(filename, file_obj, save=True)

            saved += 1
            print(f"[SYNC_AVATAR] ({idx}) SAVE ok avatar={employee.avatar.name} employee_id={employee.id}", flush=True)
            results.append({
                "pinfl": pinfl,
                "employee_id": employee.id,
                "ok": True,
                "avatar": employee.avatar.name,
                "detail": "Saqlandi",
            })

        except Exception as e:
            failed += 1
            print(f"[SYNC_AVATAR] ({idx}) ERROR pinfl={pinfl} employee_id={employee.id} err={type(e).__name__}: {e}",
                  flush=True)
            results.append({
                "pinfl": pinfl,
                "employee_id": employee.id,
                "ok": False,
                "avatar": None,
                "detail": f"Xatolik: {type(e).__name__}: {e}",
            })

    return {
        "ok": True,
        "saved": saved,
        "failed": failed,
        "results": results,
    }