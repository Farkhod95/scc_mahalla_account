# monitoring/services/patrol_car_sync.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests
from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from monitoring.models import PatrolCar
from monitoring.serializers import PatrolCarGPSSerializer


@dataclass
class SyncStats:
    fetched: int = 0
    created: int = 0
    updated: int = 0
    skipped_no_imei: int = 0
    errors: int = 0


def _safe_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _extract_coords(item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    # API: lat, lon
    lat = item.get("lat")
    lon = item.get("lon")

    # lat/lon null bo'lsa None qaytaradi
    if lat is None or lon is None:
        return None, None

    # string ko'rinishida saqlaymiz (model CharField)
    return _safe_str(lon), _safe_str(lat)  # coordinate_x=lon, coordinate_y=lat


def fetch_last_data(api_url: str, timeout: int = 20, token: Optional[str] = None) -> List[Dict[str, Any]]:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get(api_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("result") or []
    if not isinstance(result, list):
        return []
    return result


@transaction.atomic
def upsert_patrol_cars_by_imei(items: List[Dict[str, Any]]) -> SyncStats:
    stats = SyncStats(fetched=len(items))

    # IMEI larni yig'ib olamiz
    imeis: List[str] = []
    normalized_items: List[Dict[str, Any]] = []

    for item in items:
        imei = _safe_str(item.get("imei"))
        if not imei:
            stats.skipped_no_imei += 1
            continue
        imeis.append(imei)
        normalized_items.append(item)

    existing_map = {
        pc.imei: pc
        for pc in PatrolCar.objects.select_for_update().filter(imei__in=imeis)
    }

    now = timezone.now().date()

    for item in normalized_items:
        try:
            imei = _safe_str(item.get("imei"))
            if not imei:
                continue

            mobject_id = item.get("mobjectId")
            mobject_name = _safe_str(item.get("mobjectName"))
            plate_number = _safe_str(item.get("plateNumber"))
            brand_name = _safe_str(item.get("brandName"))
            group_name = _safe_str(item.get("groupName"))

            coord_x_new, coord_y_new = _extract_coords(item)  # lon, lat (string)
            # lat/lon null bo'lsa coord_x_new/coord_y_new None bo'ladi

            obj = existing_map.get(imei)

            if obj is None:
                # CREATE: agar koordinata null bo'lsa ham create qilamiz (coord null qoladi)
                patrolCar = PatrolCar.objects.create(
                    imei=imei,
                    mobjectId=mobject_id,
                    mobject_name=mobject_name,
                    plate_number=plate_number,
                    brand_name=brand_name,
                    group_name=group_name,
                    last_date=now,
                    coordinate_x=coord_x_new,  # lon
                    coordinate_y=coord_y_new,  # lat
                )
                stats.created += 1

                serializer = PatrolCarGPSSerializer(patrolCar, many=False)
                send_data = serializer.data

                # ✅ coordinate_x/coordinate_y bo'lmasa websocketga yubormaymiz
                cx = _safe_str(send_data.get("coordinate_x"))
                cy = _safe_str(send_data.get("coordinate_y"))
                if cx and cy:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "notif_get_zag_pass_child_group",
                        {
                            'type': 'notif_get_zag_pass_child_metric',
                            'metric': send_data,
                        }
                    )

                continue

            # UPDATE: koordinata null bo'lsa eskisini qoldiramiz
            obj.mobjectId = mobject_id if mobject_id is not None else obj.mobjectId
            obj.mobject_name = mobject_name if mobject_name is not None else obj.mobject_name
            obj.plate_number = plate_number if plate_number is not None else obj.plate_number
            obj.brand_name = brand_name if brand_name is not None else obj.brand_name
            obj.group_name = group_name if group_name is not None else obj.group_name
            obj.last_date = now

            if coord_x_new is not None and coord_y_new is not None:
                obj.coordinate_x = coord_x_new
                obj.coordinate_y = coord_y_new
            # aks holda o'zgarmaydi

            obj.save(update_fields=[
                "mobjectId", "mobject_name", "plate_number", "brand_name", "group_name",
                "last_date", "coordinate_x", "coordinate_y"
            ])

            serializer = PatrolCarGPSSerializer(obj, many=False)
            send_data = serializer.data

            # ✅ coordinate_x/coordinate_y bo'lmasa websocketga yubormaymiz
            cx = _safe_str(send_data.get("coordinate_x"))
            cy = _safe_str(send_data.get("coordinate_y"))
            if cx and cy:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "metrics_group",
                    {
                        'type': 'metric',
                        'metric': send_data,
                    }
                )

            stats.updated += 1

        except Exception:
            stats.errors += 1

    return stats


def sync_patrol_cars_from_api(api_url: str, timeout: int = 20, token: Optional[str] = None) -> SyncStats:
    items = fetch_last_data(api_url=api_url, timeout=timeout, token=token)
    return upsert_patrol_cars_by_imei(items)
