import pandas as pd
import re
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from directory.models import Region
from monitoring.models import Device, Project, DeviceYear, DeviceType, Object
from monitoring.serializers import DeviceImportSerializer
from users.models import User

UZBEKISTAN_BOUNDS = {
    'min_lat': 37.0,
    'max_lat': 45.0,
    'min_lon': 56.0,
    'max_lon': 73.3,
}

def is_valid_coordinate_uz(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return (
            UZBEKISTAN_BOUNDS['min_lat'] <= lat <= UZBEKISTAN_BOUNDS['max_lat'] and
            UZBEKISTAN_BOUNDS['min_lon'] <= lon <= UZBEKISTAN_BOUNDS['max_lon']
        )
    except:
        return False


def safe_int(value):
    try:
        return 0 if pd.isna(value) else int(value)
    except:
        return 0


def clean_coordinate_text(text):
    return re.sub(r'[^\d.,\-]', '', str(text)).strip()


def is_valid_coordinate(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False


def parse_coordinates(raw):
    cleaned = clean_coordinate_text(raw)
    coords = cleaned.split(',')
    return (coords[0].strip() if len(coords) > 0 else None,
            coords[1].strip() if len(coords) > 1 else None)


class DeviceImportAPIView(APIView):
    def post(self, request):
        serializer = DeviceImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        region_id = serializer.validated_data['region_id']

        try:
            region = Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return Response({'error': 'Region topilmadi'}, status=404)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({'error': f'Excel faylni o‘qishda xatolik: {e}'}, status=400)

        df.columns = [
            str(c).strip().replace('\n', '').replace(' ', '_').replace('"', '').replace("'", '').lower()
            for c in df.columns
        ]

        required_columns = [
            'kordinata', 'masul_id', 'face_soni', 'yonaltirilgan_soni',
            'drb_soni', 'ptz_soni', 'loyiha_id', 'yillar_id', 'manzil',
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return Response({'error': f'Ustunlar topilmadi: {missing}', 'columns': df.columns.tolist()}, status=400)

        # Foreign key cache
        device_type_map = {
            k: DeviceType.objects.filter(key=k).first()
            for k in ['face_soni', 'yonaltirilgan_soni', 'drb_soni', 'ptz_soni']
        }
        if missing_types := [k for k, v in device_type_map.items() if v is None]:
            return Response({'error': f'DeviceType topilmadi: {missing_types}'}, status=400)

        projects_map = {p.number: p for p in Project.objects.all()}
        device_years_map = {d.number: d for d in DeviceYear.objects.all()}
        users_map = {u.employee_number: u for u in User.objects.all()}

        errors = []

        # Step 1: validation loop
        for idx, row in df.iterrows():
            try:
                coordinate_x, coordinate_y = parse_coordinates(row['kordinata'])
                if not is_valid_coordinate(coordinate_x, coordinate_y):
                    errors.append({'row': idx + 2, 'error': f'Koordinatalar noto‘g‘ri:[{coordinate_x}, {coordinate_y}]'})
                    continue

                project_id = safe_int(row.get('loyiha_id'))
                year_id = safe_int(row.get('yillar_id'))
                user_id = safe_int(row.get('masul_id'))

                if project_id not in projects_map:
                    errors.append({'row': idx + 2, 'error': f'Project ID {project_id} topilmadi'})
                    continue
                if year_id not in device_years_map:
                    errors.append({'row': idx + 2, 'error': f'Device Year ID {year_id} topilmadi'})
                    continue
                if user_id not in users_map:
                    errors.append({'row': idx + 2, 'error': f'Masul ID {user_id} topilmadi'})
                    continue
            except Exception as e:
                errors.append({'row': idx + 2, 'error': str(e)})

        if errors:
            return Response({'success': False, 'errors': errors}, status=400)

        def create_devices(device_type_key, count, object_ref, common_kwargs):
            device_type = device_type_map[device_type_key]
            print(f"device_type_key: {device_type_key}, count: {count}, object_ref: {object_ref}, common_kwargs: {common_kwargs}")
            for _ in range(count):
                Device.objects.create(device_type=device_type, object=object_ref, **common_kwargs)

        # Step 2: save to DB
        skipped_rows = []
        try:
            with transaction.atomic():
                object_count = 0
                for idx, row in df.iterrows():
                    coordinate_x, coordinate_y = parse_coordinates(row['kordinata'])
                    if not is_valid_coordinate_uz(coordinate_x, coordinate_y):
                        skipped_rows.append({
                            'row': idx + 2,
                            'reason': f'[{coordinate_x}, {coordinate_y}]'
                        })
                        continue
                    project = projects_map[safe_int(row['loyiha_id'])]
                    year = device_years_map[safe_int(row['yillar_id'])]
                    user = users_map[safe_int(row['masul_id'])]
                    address = row.get('manzil') or ''

                    obj = Object.objects.create(
                        coordinate_x=coordinate_x,
                        coordinate_y=coordinate_y,
                        number_of_faces=safe_int(row['face_soni']),
                        directed_number=safe_int(row['yonaltirilgan_soni']),
                        number_of_drb=safe_int(row['drb_soni']),
                        number_of_ptz=safe_int(row['ptz_soni']),
                        project=project,
                        device_year=year,
                        responsible_person=user,
                        address=address,
                        region=region,
                    )
                    object_count += 1

                    common = {
                        'coordinate_x': coordinate_x,
                        'coordinate_y': coordinate_y,
                        'project': project,
                        'device_year': year,
                        'address': address,
                        'region': region,
                    }

                    create_devices('face_soni', safe_int(row['face_soni']), obj, common)
                    create_devices('yonaltirilgan_soni', safe_int(row['yonaltirilgan_soni']), obj, common)
                    create_devices('drb_soni', safe_int(row['drb_soni']), obj, common)
                    create_devices('ptz_soni', safe_int(row['ptz_soni']), obj, common)

            return Response({'success': True, 'message': f'Import muvaffaqiyatli yakunlandi. Obyekt Soni: {object_count}. Chegaradan tashqaridagilar ({len(skipped_rows)}): {skipped_rows}'}, status=201)
        except Exception as e:
            return Response({'success': False, 'error': f'Saqlashda xatolik: {str(e)}'}, status=500)
