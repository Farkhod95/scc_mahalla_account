from django.urls import re_path, path

from monitoring.views.all_count_by_mahalla import AllCountByMahallaView
from monitoring.views.car_flow import CarFlowView
from monitoring.views.damafon import (
    DamafonListCreateView, DamafonDetailView, DamafonSnapshotView,
    DamafonWebrtcView, DamafonDoorbellView, DamafonCallListView,
)
from monitoring.views.bazar_camera import BazarCameraView, BazarCameraDetailView, BazarCameraFieldInfoView
from monitoring.views.camera_information import CameraInformationView, CameraInformationDetailView, \
    CameraInformationFieldInfoView, CameraInformationForMapView
from monitoring.views.center_of_civilization import CenterOfCivilizationView, CenterOfCivilizationDetailView, \
    CenterOfCivilizationFieldInfoView
from monitoring.views.crime_category import CrimeCategoryView, CrimeCategoryDetailView, CrimeCategoryFieldInfoView
from monitoring.views.employee import EmployeeView, EmployeeDetailView, EmployeeFieldInfoView
from monitoring.views.gps_inspector import GPSInspectorDistrictListView, GPSInspectorMFYListView, GPSInspectorByMFYView
from monitoring.views.import_by_mahalla_id import CameraInformationImportInfoView
from monitoring.views.import_excel_shop import ShopExcelImportView, ShopExcelImportStatusView
from monitoring.views.mahalla_crime import MahallaCrimeView, MahallaCrimeDetailView, MahallaCrimeFieldInfoView, \
    MahallaCrimeForMapView
from monitoring.views.mahalla_information import MahallaInformationView, MahallaInformationDetailView, \
    MahallaInformationFieldInfoView
from monitoring.views.mahalla_information_category import MahallaInformationCategoryView, \
    MahallaInformationCategoryDetailView, MahallaInformationCategoryFieldInfoView
from monitoring.views.mfy_citizen import MFYCitizenView, MFYCitizenDetailView, MFYCitizenFieldInfoView
from monitoring.views.objec_category import ObjectCategoryView, ObjectCategoryDetailView, ObjectCategoryFieldInfoView
from monitoring.views.object import ObjectView, ObjectDetailView, ObjectFieldInfoView, ObjectForMapView, \
    ObjectExcelImportView
from monitoring.views.object_category_dashboard import ObjectCategoryForDashboardView
from monitoring.views.office_camera import OfficeCameraView, OfficeCameraDetailView, OfficeCameraFieldInfoView
from monitoring.views.patrol_car import PatrolCarView, PatrolCarDetailView, PatrolCarFieldInfoView
from monitoring.views.shop import ShopView, ShopDetailView, ShopFieldInfoView
from monitoring.views.shop_cash_status import ShopCashStatusView, TenantCashStatusSummaryView
from monitoring.views.shop_crime import ShopCrimeListCreateView, ShopCrimeDetailView
from monitoring.views.shop_and_tenant_avatars import SyncShopOwnerAvatarAPIView, SyncShopOwnerAvatarStatusAPIView, \
    SyncShopTenantLeaderAvatarAPIView, SyncShopTenantLeaderAvatarStatusAPIView
from monitoring.views.shop_camera import ShopCameraView, ShopCameraDetailView, ShopCameraFieldInfoView
from monitoring.views.shop_tenant import ShopTenantView, ShopTenantDetailView, ShopTenantFieldInfoView
from monitoring.views.tenant_employee import TenantEmployeeView, TenantEmployeeDetailView, TenantEmployeeFieldInfoView
from monitoring.views.tenant_employee_avatar import SyncTenantEmployeeAvatarAPIView, \
    SyncTenantEmployeeAvatarStatusAPIView

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
    path('shop/cash-status/summary/', TenantCashStatusSummaryView.as_view(), name='tenant_cash_status_summary'),
    path('shop/cash-status/', ShopCashStatusView.as_view(), name='shop_cash_status'),
    path('shop/<int:pk>', ShopDetailView.as_view(), name='shop_detail_view'),
    path('shop/fields/', ShopFieldInfoView.as_view(), name='shop_fields_info'),
    path("shop/sync-owner-avatars/", SyncShopOwnerAvatarAPIView.as_view(), name="shop-sync-owner-avatars",),
    path("shop/sync-owner-avatars/status/<str:task_id>/", SyncShopOwnerAvatarStatusAPIView.as_view(), name="shop-sync-owner-avatars-status",),

    re_path(r'^shop-camera/$', ShopCameraView.as_view(), name='shop_camera_view'),
    path('shop-camera/<int:pk>', ShopCameraDetailView.as_view(), name='shop_camera_detail_view'),
    path('shop-camera/fields/', ShopCameraFieldInfoView.as_view(), name='shop_camera_fields_info'),

    re_path(r'^shop-tenant/$', ShopTenantView.as_view(), name='shop_tenant_view'),
    path('shop-tenant/<int:pk>', ShopTenantDetailView.as_view(), name='shop_tenant_detail_view'),
    path('shop-tenant/fields/', ShopTenantFieldInfoView.as_view(), name='shop_tenant_fields_info'),
    path("shop-tenant/sync-leader-avatars/", SyncShopTenantLeaderAvatarAPIView.as_view(),
        name="shop-tenant-sync-leader-avatars", ),
    path("shop-tenant/sync-leader-avatars/status/<str:task_id>/", SyncShopTenantLeaderAvatarStatusAPIView.as_view(),
        name="shop-tenant-sync-leader-avatars-status", ),

    re_path(r'^tenant-employee/$', TenantEmployeeView.as_view(), name='tenant_employee_view'),
    path('tenant-employee/<int:pk>', TenantEmployeeDetailView.as_view(), name='tenant_employee_detail_view'),
    path('tenant-employee/fields/', TenantEmployeeFieldInfoView.as_view(), name='tenant_employee_fields_info'),
    path("tenant-employee/sync-avatars/", SyncTenantEmployeeAvatarAPIView.as_view(), name="tenant-employee-sync-avatars",),
    path("tenant-employee/sync-avatars/status/<str:task_id>/", SyncTenantEmployeeAvatarStatusAPIView.as_view(), name="tenant-employee-sync-avatars-status",),

    re_path(r'^bazar-camera/$', BazarCameraView.as_view(), name='bazar_camera_view'),
    path('bazar-camera/<int:pk>', BazarCameraDetailView.as_view(), name='bazar_camera_detail_view'),
    path('bazar-camera/fields/', BazarCameraFieldInfoView.as_view(), name='bazar_camera_fields_info'),


    re_path(r'^center-of-civilization/$', CenterOfCivilizationView.as_view(), name='center_civilization_view'),
    path('center-of-civilization/<int:pk>', CenterOfCivilizationDetailView.as_view(), name='center_civilization_detail_view'),
    path('center-of-civilization/fields/', CenterOfCivilizationFieldInfoView.as_view(), name='center_civilization_fields_info'),

    re_path(r'^mfy-citizen/$', MFYCitizenView.as_view(), name='mfy_citizen_view'),
    path('mfy-citizen/<int:pk>', MFYCitizenDetailView.as_view(), name='mfy_citizen_detail_view'),
    path('mfy-citizen/fields/', MFYCitizenFieldInfoView.as_view(), name='mfy_citizen_fields_info'),

    path("import-excel/", ShopExcelImportView.as_view(), name="shop-excel-import"),
    path("import-excel/status/<str:task_id>/", ShopExcelImportStatusView.as_view(), name="shop-excel-import-status"),

    path("gps-inspector/districts/", GPSInspectorDistrictListView.as_view(), name="gps-inspector-districts"),
    path("gps-inspector/mfys/", GPSInspectorMFYListView.as_view(), name="gps-inspector-mfys"),
    path("gps-inspector/inspectors/<str:mfy_id>/", GPSInspectorByMFYView.as_view(), name="gps-inspector-by-mfy"),

    path('car-flow/', CarFlowView.as_view(), name='car_flow'),

    re_path(r'^shop-crime/$', ShopCrimeListCreateView.as_view(), name='shop_crime_list_create'),
    path('shop-crime/<int:pk>', ShopCrimeDetailView.as_view(), name='shop_crime_detail'),

    # Damafon (intercom): qurilmalar — mikroservis proxy; qo'ng'iroq tarixi — bizning DB.
    # WS: routing.py (ws/damafon/ jonli call, ws/damafon/talkback/ mikrofon).
    path('damafon/calls/', DamafonCallListView.as_view(), name='damafon_calls'),
    path('damafon/webrtc', DamafonWebrtcView.as_view(), name='damafon_webrtc'),
    path('damafon/doorbell', DamafonDoorbellView.as_view(), name='damafon_doorbell'),
    re_path(r'^damafon/$', DamafonListCreateView.as_view(), name='damafon_list_create'),
    path('damafon/<int:pk>', DamafonDetailView.as_view(), name='damafon_detail'),
    path('damafon/<int:pk>/snapshot', DamafonSnapshotView.as_view(), name='damafon_snapshot'),
]