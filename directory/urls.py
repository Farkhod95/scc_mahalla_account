from django.urls import re_path, path
from .views.department import DepartmentView, DepartmentDetailView, DepartmentFieldInfoView

from .views.district import DistrictView, DistrictDetailView, DistrictViewList
from .views.import_mahalla import MahallaImportAPIView
from .views.mahalla import MahallaView, MahallaDetailView
from .views.organization import OrganizationView, OrganizationDetailView, OrganizationFieldInfoView
from .views.position import PositionView, PositionDetailView, PositionFieldInfoView
from .views.region import RegionView, RegionDetailView, RegionViewList

urlpatterns = [
    re_path(r'^region/$', RegionView.as_view(), name='regions_view'),
    path('region/<int:pk>', RegionDetailView.as_view(), name='region_detail_view'),
    # path('region/list', RegionViewList.as_view(), name='regions_list'),

    re_path(r'^district/$', DistrictView.as_view(), name='districts_view'),
    path('district/<int:pk>', DistrictDetailView.as_view(), name='districts_detail_view'),
    # path('district/list', DistrictViewList.as_view(), name='district_list'),

    re_path(r'^mahalla/$', MahallaView.as_view(), name='mahalla_view'),
    path('mahalla/<int:pk>', MahallaDetailView.as_view(), name='mahalla_detail_view'),
    path('import-mahalla/', MahallaImportAPIView.as_view(), name='import-mahalla'),

    re_path(r'^organization/$', OrganizationView.as_view(), name='organization_view'),
    path('organization/<int:pk>', OrganizationDetailView.as_view(), name='organization_detail_view'),
    path('organization/fields/', OrganizationFieldInfoView.as_view(), name='organization_fields_info'),

    re_path(r'^department/$', DepartmentView.as_view(), name='department_view'),
    path('department/<int:pk>', DepartmentDetailView.as_view(), name='department_detail_view'),
    path('department/fields/', DepartmentFieldInfoView.as_view(), name='department_fields_info'),

    re_path(r'^position/$', PositionView.as_view(), name='position_view'),
    path('position/<int:pk>', PositionDetailView.as_view(), name='position_detail_view'),
    path('position/fields/', PositionFieldInfoView.as_view(), name='position_fields_info'),
]