from django.urls import re_path, path

from monitoring.views.all_count_by_mahalla import AllCountByMahallaView
from monitoring.views.camera_information import CameraInformationView, CameraInformationDetailView, \
    CameraInformationFieldInfoView, CameraInformationForMapView
from monitoring.views.crime_category import CrimeCategoryView, CrimeCategoryDetailView, CrimeCategoryFieldInfoView
from monitoring.views.employee import EmployeeView, EmployeeDetailView, EmployeeFieldInfoView
from monitoring.views.import_by_mahalla_id import CameraInformationImportInfoView
from monitoring.views.mahalla_crime import MahallaCrimeView, MahallaCrimeDetailView, MahallaCrimeFieldInfoView, \
    MahallaCrimeForMapView
from monitoring.views.mahalla_information import MahallaInformationView, MahallaInformationDetailView, \
    MahallaInformationFieldInfoView
from monitoring.views.mahalla_information_category import MahallaInformationCategoryView, \
    MahallaInformationCategoryDetailView, MahallaInformationCategoryFieldInfoView
from monitoring.views.objec_category import ObjectCategoryView, ObjectCategoryDetailView, ObjectCategoryFieldInfoView
from monitoring.views.object import ObjectView, ObjectDetailView, ObjectFieldInfoView, ObjectForMapView, \
    ObjectExcelImportView
from monitoring.views.object_category_dashboard import ObjectCategoryForDashboardView
from monitoring.views.office_camera import OfficeCameraView, OfficeCameraDetailView, OfficeCameraFieldInfoView
from monitoring.views.patrol_car import PatrolCarView, PatrolCarDetailView, PatrolCarFieldInfoView
from monitoring.views.shop import ShopView, ShopDetailView, ShopFieldInfoView
from monitoring.views.shop_camera import ShopCameraView, ShopCameraDetailView, ShopCameraFieldInfoView
from monitoring.views.shop_tenant import ShopTenantView, ShopTenantDetailView, ShopTenantFieldInfoView
from monitoring.views.shop_trade_stats import ShopTradeStatsView, ShopTradeStatsDetailView, ShopTradeStatsFieldInfoView
from monitoring.views.tenant_employee import TenantEmployeeView, TenantEmployeeDetailView, TenantEmployeeFieldInfoView

urlpatterns = [
    re_path(r'^employee/$', EmployeeView.as_view(), name='employee_view'),
    path('employee/<int:pk>', EmployeeDetailView.as_view(), name='employee_detail_view'),
    path('employee/fields/', EmployeeFieldInfoView.as_view(), name='employee_fields_info'),

    re_path(r'^mahalla-information-category/$', MahallaInformationCategoryView.as_view(),
            name='mahalla_information_category_view'),
    path('mahalla-information-category/<int:pk>', MahallaInformationCategoryDetailView.as_view(),
         name='mahalla_information_category_detail_view'),
    path('mahalla-information-category/fields/', MahallaInformationCategoryFieldInfoView.as_view(),
         name='mahalla_information_category_fields_info'),

    re_path(r'^mahalla-information/$', MahallaInformationView.as_view(), name='mahalla_information_view'),
    path('mahalla-information/<int:pk>', MahallaInformationDetailView.as_view(),
         name='mahalla_information_detail_view'),
    path('mahalla-information/fields/', MahallaInformationFieldInfoView.as_view(),
         name='mahalla_information_fields_info'),

    re_path(r'^object-category/$', ObjectCategoryView.as_view(), name='object_category_view'),
    path('object-category/<int:pk>', ObjectCategoryDetailView.as_view(), name='object_category_detail_view'),
    path('object-category/fields/', ObjectCategoryFieldInfoView.as_view(), name='object_category_fields_info'),
    path('object-category/for-dashboard/', ObjectCategoryForDashboardView.as_view(), name='for_dashboard_info'),

    re_path(r'^object/$', ObjectView.as_view(), name='object_view'),
    path('object/for-map/', ObjectForMapView.as_view(), name='object_map_view'),
    path('object/<int:pk>', ObjectDetailView.as_view(), name='object_detail_view'),
    path('object/fields/', ObjectFieldInfoView.as_view(), name='object_fields_info'),
    path('object/import-from-excel/', ObjectExcelImportView.as_view(), name='object-import-excel'),

    re_path(r'^crime-category/$', CrimeCategoryView.as_view(), name='crime_category_view'),
    path('crime-category/<int:pk>', CrimeCategoryDetailView.as_view(), name='crime_category_detail_view'),
    path('crime-category/fields/', CrimeCategoryFieldInfoView.as_view(), name='crime_category_fields_info'),

    re_path(r'^mahalla-crime/$', MahallaCrimeView.as_view(), name='mahalla_crime_view'),
    path('mahalla-crime/for-map/', MahallaCrimeForMapView.as_view(), name='mahalla_crime_map_view'),
    path('mahalla-crime/<int:pk>', MahallaCrimeDetailView.as_view(), name='mahalla_crime_detail_view'),
    path('mahalla-crime/fields/', MahallaCrimeFieldInfoView.as_view(), name='mahalla_crime_fields_info'),

    re_path(r'^patrol-car/$', PatrolCarView.as_view(), name='patrol_car_view'),
    path('patrol-car/<int:pk>', PatrolCarDetailView.as_view(), name='patrol_car_detail_view'),
    path('patrol-car/fields/', PatrolCarFieldInfoView.as_view(), name='patrol_car_fields_info'),

    re_path(r'^camera-information/$', CameraInformationView.as_view(), name='camera_information_view'),
    path('camera-information/for-map/', CameraInformationForMapView.as_view(), name='camera_information_map_view'),
    path('camera-information/<int:pk>', CameraInformationDetailView.as_view(), name='camera_information_detail_view'),
    path('camera-information/fields/', CameraInformationFieldInfoView.as_view(), name='camera_information_fields_info'),
    path('camera-information/fields/import-by-mahalla-id/', CameraInformationImportInfoView.as_view(), name='camera_information_fields_info'),

    re_path(r'^office-camera/$', OfficeCameraView.as_view(), name='office_camera_view'),
    path('office-camera/<int:pk>', OfficeCameraDetailView.as_view(), name='office_camera_detail_view'),
    path('office-camera/fields/', OfficeCameraFieldInfoView.as_view(), name='office_camera_fields_info'),

    path('stats/all-count-by-mahalla/', AllCountByMahallaView.as_view(), name='all-count-by-mahalla'),


    re_path(r'^shop/$', ShopView.as_view(), name='shop_view'),
    path('shop/<int:pk>', ShopDetailView.as_view(), name='shop_detail_view'),
    path('shop/fields/', ShopFieldInfoView.as_view(), name='shop_fields_info'),

    re_path(r'^shop-camera/$', ShopCameraView.as_view(), name='shop_camera_view'),
    path('shop-camera/<int:pk>', ShopCameraDetailView.as_view(), name='shop_camera_detail_view'),
    path('shop-camera/fields/', ShopCameraFieldInfoView.as_view(), name='shop_camera_fields_info'),

    re_path(r'^shop-tenant/$', ShopTenantView.as_view(), name='shop_tenant_view'),
    path('shop-tenant/<int:pk>', ShopTenantDetailView.as_view(), name='shop_tenant_detail_view'),
    path('shop-tenant/fields/', ShopTenantFieldInfoView.as_view(), name='shop_tenant_fields_info'),

    re_path(r'^tenant-employee/$', TenantEmployeeView.as_view(), name='tenant_employee_view'),
    path('tenant-employee/<int:pk>', TenantEmployeeDetailView.as_view(), name='tenant_employee_detail_view'),
    path('tenant-employee/fields/', TenantEmployeeFieldInfoView.as_view(), name='tenant_employee_fields_info'),


    re_path(r'^shop-trade-stats/$', ShopTradeStatsView.as_view(), name='shop_trade_stats_view'),
    path('shop-trade-stats/<int:pk>', ShopTradeStatsDetailView.as_view(), name='shop_trade_stats_detail_view'),
    path('shop-trade-stats/fields/', ShopTradeStatsFieldInfoView.as_view(), name='shop_trade_stats_fields_info'),
]