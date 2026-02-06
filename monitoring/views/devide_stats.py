from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from monitoring.models import Device, Project, DeviceType


class ProjectDeviceTypeStatsAPIView(APIView):
    def get(self, request):
        # Barcha device turlarini olish
        all_device_types = list(DeviceType.objects.all().values('id', 'name'))

        # Qurilma hisobini olish (borlarini)
        counts = (
            Device.objects
            .filter(project__isnull=False, device_type__isnull=False)
            .values('project_id', 'project__name', 'device_type_id')
            .annotate(count=Count('id'))
        )

        # Project x DeviceType ko‘rinishida tashkil qilish
        project_map = {}
        for count in counts:
            project_id = count['project_id']
            device_type_id = count['device_type_id']

            if project_id not in project_map:
                project_map[project_id] = {
                    'project_id': project_id,
                    'project_name': count['project__name'],
                    'device_types': {}
                }

            project_map[project_id]['device_types'][device_type_id] = count['count']

        # Har bir loyihaga 0-count bo‘lgan device_type larni ham qo‘shish
        result = []
        for project_id, project_data in project_map.items():
            device_type_list = []
            for dt in all_device_types:
                count = project_data['device_types'].get(dt['id'], 0)
                device_type_list.append({
                    'device_type_id': dt['id'],
                    'device_type_name': dt['name'],
                    'count': count
                })
            result.append({
                'project_id': project_data['project_id'],
                'project_name': project_data['project_name'],
                'device_types': device_type_list
            })

        # Ehtimoliy loyiha bo‘lgan, lekin qurilmalar yo‘q bo‘lgan projectlar ham kiritilishi mumkin
        # Agar shunaqasi kerak bo‘lsa, ayting

        return Response(result)
