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


def safe_int(value):
    try:
        if pd.isna(value):
            return 0
        return int(value)
    except:
        return 0


def clean_coordinate_text(text):
    return re.sub(r'[^\d.,\-]', '', str(text)).strip()


def is_valid_coordinate(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


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

        errors = []

        # Cache all necessary foreign objects
        device_type_map = {
            'face_soni': DeviceType.objects.filter(key='face_soni').first(),
            'yonaltirilgan_soni': DeviceType.objects.filter(key='yonaltirilgan_soni').first(),
            'drb_soni': DeviceType.objects.filter(key='drb_soni').first(),
            'ptz_soni': DeviceType.objects.filter(key='ptz_soni').first(),
        }

        # tekshirish
        missing_device_types = [k for k, v in device_type_map.items() if v is None]
        if missing_device_types:
            return Response({
                'success': False,
                'error': f'Quyidagi DeviceType key(lar)i topilmadi: {missing_device_types}'
            }, status=400)

        projects_map = {p.number: p for p in Project.objects.all()}
        device_years_map = {d.number: d for d in DeviceYear.objects.all()}
        users_map = {u.employee_number: u for u in User.objects.all()}

        # Step 1: VALIDATION LOOP
        for idx, row in df.iterrows():
            try:
                cleaned = clean_coordinate_text(row['kordinata'])
                coords = cleaned.split(',')
                coordinate_x = coords[0].strip() if len(coords) > 0 else None
                coordinate_y = coords[1].strip() if len(coords) > 1 else None

                if not is_valid_coordinate(coordinate_x, coordinate_y):
                    errors.append({'row': idx + 2, 'error': f'Noto‘g‘ri koordinata: {coordinate_x}, {coordinate_y}'})
                    continue

                project_id = safe_int(row.get('loyiha_id'))
                device_year_id = safe_int(row.get('yillar_id'))
                responsible_person_id = safe_int(row.get('masul_id'))

                if project_id not in projects_map:
                    errors.append({'row': idx + 2, 'error': f'Project ID {project_id} mavjud emas yoki noto‘g‘ri'})
                    continue

                if device_year_id not in device_years_map:
                    errors.append({'row': idx + 2, 'error': f'Device Year ID {device_year_id} mavjud emas yoki noto‘g‘ri'})
                    continue

                if responsible_person_id not in users_map:
                    errors.append({'row': idx + 2, 'error': f'Foydalanuvchi ID {responsible_person_id} mavjud emas yoki noto‘g‘ri'})
                    continue

            except Exception as e:
                errors.append({'row': idx + 2, 'error': str(e)})
                continue

        # Step 2: Check if any errors
        if errors:
            return Response({'success': False, 'errors': errors}, status=400)

        # Step 3: If validation passed — save
        try:
            with transaction.atomic():
                for idx, row in df.iterrows():
                    cleaned = clean_coordinate_text(row['kordinata'])
                    coords = cleaned.split(',')
                    coordinate_x = coords[0].strip() if len(coords) > 0 else None
                    coordinate_y = coords[1].strip() if len(coords) > 1 else None

                    project_id = safe_int(row.get('loyiha_id'))
                    device_year_id = safe_int(row.get('yillar_id'))
                    responsible_person_id = safe_int(row.get('masul_id'))

                    project = projects_map[project_id]
                    device_year = device_years_map[device_year_id]
                    responsible_person = users_map[responsible_person_id]

                    obj = Object.objects.create(
                        coordinate_x=coordinate_x,
                        coordinate_y=coordinate_y,
                        number_of_faces=safe_int(row.get('face_soni')),
                        directed_number=safe_int(row.get('yonaltirilgan_soni')),
                        number_of_drb=safe_int(row.get('drb_soni')),
                        number_of_ptz=safe_int(row.get('ptz_soni')),
                        project=project,
                        device_year=device_year,
                        responsible_person=responsible_person,
                        address=row.get('manzil') or '',
                        region=region,
                    )

                    face_soni = safe_int(row.get('face_soni'))
                    device_type = device_type_map['face_soni']
                    for i in range(face_soni):
                        Device.objects.create(
                            device_type=device_type,
                            coordinate_x=coordinate_x,
                            coordinate_y=coordinate_y,
                            object=obj,
                            project=project,
                            device_year=device_year,
                            address=row.get('manzil') or '',
                            region=region,
                        )

                    yonaltirilgan_soni = safe_int(row.get('yonaltirilgan_soni'))
                    device_type = device_type_map['yonaltirilgan_soni']
                    for i in range(yonaltirilgan_soni):
                        Device.objects.create(
                            device_type=device_type,
                            coordinate_x=coordinate_x,
                            coordinate_y=coordinate_y,
                            object=obj,
                            project=project,
                            device_year=device_year,
                            address=row.get('manzil') or '',
                            region=region,
                        )

                    drb_soni = safe_int(row.get('drb_soni'))
                    device_type = device_type_map['drb_soni']
                    for i in range(drb_soni):
                        Device.objects.create(
                            device_type=device_type,
                            coordinate_x=coordinate_x,
                            coordinate_y=coordinate_y,
                            object=obj,
                            project=project,
                            device_year=device_year,
                            address=row.get('manzil') or '',
                            region=region,
                        )

                    ptz_soni = safe_int(row.get('ptz_soni'))
                    device_type = device_type_map['ptz_soni']
                    for i in range(ptz_soni):
                        Device.objects.create(
                            device_type=device_type,
                            coordinate_x=coordinate_x,
                            coordinate_y=coordinate_y,
                            object=obj,
                            project=project,
                            device_year=device_year,
                            address=row.get('manzil') or '',
                            region=region,
                        )

            return Response({'success': True, 'message': 'Barcha qurilmalar muvaffaqiyatli saqlandi'}, status=201)

        except Exception as e:
            return Response({'success': False, 'error': f'Saqlashda xatolik: {e}'}, status=500)
