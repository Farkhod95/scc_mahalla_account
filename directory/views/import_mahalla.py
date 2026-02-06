import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from directory.models import Region, District, Mahalla


class MahallaImportAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'Fayl yuborilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
            # df.columns = df.columns.str.strip().str.lower()  # Ustun nomlarini kichik harflarda va tozalab olish

            errors = []
            created_count = 0

            for index, row in df.iterrows():
                row_number = index + 2  # Excel faylida 1-based index + sarlavha
                print(row)
                region_id = row['Region']
                district_id = row['District']
                name_uz = row['nameUzLat']
                name_en = row['nameEn']
                name_ru = row['nameRu']
                print(region_id, district_id, name_uz, name_en, name_ru)

                if not all([region_id, district_id, name_uz, name_en, name_ru]):
                    errors.append(f"{row_number}-qatorda majburiy maydonlar to‘ldirilmagan")
                    continue

                try:
                    region = Region.objects.get(id=int(region_id))
                except Region.DoesNotExist:
                    errors.append(f"{row_number}-qatorda Region topilmadi: {region_id}")
                    continue

                try:
                    district = District.objects.get(id=int(district_id))
                except District.DoesNotExist:
                    errors.append(f"{row_number}-qatorda District topilmadi: {district_id}")
                    continue

                try:
                    Mahalla.objects.create(
                        code=f"{region.code}{district.code}{index+1}",
                        name=name_uz,
                        name_uz=name_uz,
                        name_en=name_en,
                        name_ru=name_ru,
                        region=region,
                        district=district,
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"{row_number}-qatorda Mahalla yaratishda xatolik: {str(e)}")
                    continue

            return Response({
                'created': created_count,
                'errors': errors,
                'total_rows': len(df),
                'skipped': len(errors),
            }, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
