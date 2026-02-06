from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from restapp.pagination import ResultsSetPagination
from users.models import Role, AppModule
from users.serializers import RoleSerializer, AppModuleSerializer


class RoleView(ListCreateAPIView):
    serializer_class = RoleSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        return Role.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, 201)


class RoleDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.all()


class RolePermissionGridView(APIView):

    def get(self, request):
        modules = AppModule.objects.filter(on_dashboard=True).order_by('sorting')
        serializer = AppModuleSerializer(modules, many=True)

        return Response(serializer.data)