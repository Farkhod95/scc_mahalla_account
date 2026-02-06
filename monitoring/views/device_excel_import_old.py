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

        objects_to_create = []
        devices_to_create = []
        errors = []

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

                if not project_id or not Project.objects.filter(number=project_id).exists():
                    errors.append({'row': idx + 2, 'error': f'Project ID {project_id} mavjud emas yoki noto‘g‘ri'})
                    continue

                if not device_year_id or not DeviceYear.objects.filter(number=device_year_id).exists():
                    errors.append({'row': idx + 2, 'error': f'Device Year ID {device_year_id} mavjud emas yoki noto‘g‘ri'})
                    continue

                if not responsible_person_id or not User.objects.filter(employee_number=responsible_person_id).exists():
                    errors.append({'row': idx + 2, 'error': f'Foydalanuvchi ID {responsible_person_id} mavjud emas yoki noto‘g‘ri'})
                    continue

                # object = Device(
                #     coordinate_x=coordinate_x,
                #     coordinate_y=coordinate_y,
                #     number_of_faces=safe_int(row.get('face_soni')),
                #     directed_number=safe_int(row.get('yonaltirilgan_soni')),
                #     number_of_drb=safe_int(row.get('drb_soni')),
                #     number_of_ptz=safe_int(row.get('ptz_soni')),
                #     project=Project.objects.get(number=project_id),
                #     device_year=DeviceYear.objects.get(number=device_year_id),
                #     responsible_person=User.objects.get(employee_number=responsible_person_id),
                #     address=row.get('manzil') or '',
                #     region=region,
                # )
                # objects_to_create.append(object)
                face_soni = safe_int(row.get('face_soni'))
                if not face_soni or not DeviceType.objects.filter(key="face_soni").exists():
                    errors.append({'row': idx + 2,
                                   'error': f'Device Type "face_soni" Key mavjud emas yoki noto‘g‘ri'})
                    continue

                yonaltirilgan_soni = safe_int(row.get('yonaltirilgan_soni'))
                if not yonaltirilgan_soni or not DeviceType.objects.filter(key="yonaltirilgan_soni").exists():
                    errors.append({'row': idx + 2,
                                   'error': f'Device Type "yonaltirilgan_soni" Key mavjud emas yoki noto‘g‘ri'})
                    continue

                drb_soni = safe_int(row.get('drb_soni'))
                if not drb_soni or not DeviceType.objects.filter(key="drb_soni").exists():
                    errors.append({'row': idx + 2,
                                   'error': f'Device Type "drb_soni" Key mavjud emas yoki noto‘g‘ri'})
                    continue

                ptz_soni = safe_int(row.get('ptz_soni'))
                if not ptz_soni or not DeviceType.objects.filter(key="ptz_soni").exists():
                    errors.append({'row': idx + 2,
                                   'error': f'Device Type "ptz_soni" Key mavjud emas yoki noto‘g‘ri'})
                    continue

                # device = Device(
                #     coordinate_x=coordinate_x,
                #     coordinate_y=coordinate_y,
                #     device_type=DeviceType.objects.get(number=device_type_id),
                #     # number_of_faces=face_soni,
                #     # directed_number=safe_int(row.get('yonaltirilgan_soni')),
                #     # number_of_drb=safe_int(row.get('drb_soni')),
                #     # number_of_ptz=safe_int(row.get('ptz_soni')),
                #     project=Project.objects.get(number=project_id),
                #     device_year=DeviceYear.objects.get(number=device_year_id),
                #     responsible_person=User.objects.get(employee_number=responsible_person_id),
                #     address=row.get('manzil') or '',
                #     region=region,
                # )
                # devices_to_create.append(device)

            except Exception as e:
                errors.append({'row': idx + 2, 'error': str(e)})

        if errors:
            return Response({'success': False, 'errors': errors}, status=400)

        try:
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        cleaned = clean_coordinate_text(row['kordinata'])
                        coords = cleaned.split(',')
                        coordinate_x = coords[0].strip() if len(coords) > 0 else None
                        coordinate_y = coords[1].strip() if len(coords) > 1 else None

                        project_id = safe_int(row.get('loyiha_id'))
                        device_year_id = safe_int(row.get('yillar_id'))
                        responsible_person_id = safe_int(row.get('masul_id'))

                        face_soni = safe_int(row.get('face_soni'))
                        if face_soni:
                            for i in range(face_soni):
                                device_type = DeviceType.objects.filter(key="face_soni").first()
                                obj = Object.objects.create(
                                    coordinate_x=coordinate_x,
                                    coordinate_y=coordinate_y,
                                    device_type=device_type,
                                    number_of_faces=face_soni,
                                    directed_number=safe_int(row.get('yonaltirilgan_soni')),
                                    number_of_drb=safe_int(row.get('drb_soni')),
                                    number_of_ptz=safe_int(row.get('ptz_soni')),
                                    project=Project.objects.get(number=project_id),
                                    device_year=DeviceYear.objects.get(number=device_year_id),
                                    responsible_person=User.objects.get(employee_number=responsible_person_id),
                                    address=row.get('manzil') or '',
                                    region=region,
                                )
                                Device.objects.create(
                                    coordinate_x=coordinate_x,
                                    coordinate_y=coordinate_y,
                                    object=obj,
                                    project=Project.objects.get(number=project_id),
                                    device_year=DeviceYear.objects.get(number=device_year_id),
                                    responsible_person=User.objects.get(employee_number=responsible_person_id),
                                    address=row.get('manzil') or '',
                                    region=region,
                                )


                    except Exception as e:
                        errors.append({'row': idx + 2, 'error': str(e)})

            return Response({'success': True, 'created': len(devices_to_create)}, status=201)
        except Exception as e:
            return Response({'success': False, 'error': f'Saqlashda xatolik: {e}'}, status=500)
