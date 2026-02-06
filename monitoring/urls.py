from django.urls import re_path, path
from monitoring.views.camera_information import CameraInformationView, CameraInformationDetailView, \
    CameraInformationFieldInfoView
from monitoring.views.crime_category import CrimeCategoryView, CrimeCategoryDetailView, CrimeCategoryFieldInfoView
from monitoring.views.employee import EmployeeView, EmployeeDetailView, EmployeeFieldInfoView
from monitoring.views.import_by_mahalla_id import CameraInformationImportInfoView
from monitoring.views.mahalla_crime import MahallaCrimeView, MahallaCrimeDetailView, MahallaCrimeFieldInfoView
from monitoring.views.mahalla_information import MahallaInformationView, MahallaInformationDetailView, \
    MahallaInformationFieldInfoView
from monitoring.views.objec_category import ObjectCategoryView, ObjectCategoryDetailView, ObjectCategoryFieldInfoView
from monitoring.views.object import ObjectView, ObjectDetailView, ObjectFieldInfoView
from monitoring.views.patrol_car import PatrolCarView, PatrolCarDetailView, PatrolCarFieldInfoView

urlpatterns = [
    re_path(r'^employee/$', EmployeeView.as_view(), name='employee_view'),
    path('employee/<int:pk>', EmployeeDetailView.as_view(), name='employee_detail_view'),
    path('employee/fields/', EmployeeFieldInfoView.as_view(), name='employee_fields_info'),

    re_path(r'^mahalla-information/$', MahallaInformationView.as_view(), name='mahalla_information_view'),
    path('mahalla-information/<int:pk>', MahallaInformationDetailView.as_view(),
         name='mahalla_information_detail_view'),
    path('mahalla-information/fields/', MahallaInformationFieldInfoView.as_view(),
         name='mahalla_information_fields_info'),

    re_path(r'^object-category/$', ObjectCategoryView.as_view(), name='object_category_view'),
    path('object-category/<int:pk>', ObjectCategoryDetailView.as_view(), name='object_category_detail_view'),
    path('object-category/fields/', ObjectCategoryFieldInfoView.as_view(), name='object_category_fields_info'),

    re_path(r'^object/$', ObjectView.as_view(), name='object_view'),
    path('object/<int:pk>', ObjectDetailView.as_view(), name='object_detail_view'),
    path('object/fields/', ObjectFieldInfoView.as_view(), name='object_fields_info'),

    re_path(r'^crime-category/$', CrimeCategoryView.as_view(), name='crime_category_view'),
    path('crime-category/<int:pk>', CrimeCategoryDetailView.as_view(), name='crime_category_detail_view'),
    path('crime-category/fields/', CrimeCategoryFieldInfoView.as_view(), name='crime_category_fields_info'),

    re_path(r'^mahalla-crime/$', MahallaCrimeView.as_view(), name='mahalla_crime_view'),
    path('mahalla-crime/<int:pk>', MahallaCrimeDetailView.as_view(), name='mahalla_crime_detail_view'),
    path('mahalla-crime/fields/', MahallaCrimeFieldInfoView.as_view(), name='mahalla_crime_fields_info'),

    re_path(r'^patrol-car/$', PatrolCarView.as_view(), name='patrol_car_view'),
    path('patrol-car/<int:pk>', PatrolCarDetailView.as_view(), name='patrol_car_detail_view'),
    path('patrol-car/fields/', PatrolCarFieldInfoView.as_view(), name='patrol_car_fields_info'),

    re_path(r'^camera-information/$', CameraInformationView.as_view(), name='camera_information_view'),
    path('camera-information/<int:pk>', CameraInformationDetailView.as_view(), name='camera_information_detail_view'),
    path('camera-information/fields/', CameraInformationFieldInfoView.as_view(), name='camera_information_fields_info'),
    path('camera-information/fields/import-by-mahalla-id/', CameraInformationImportInfoView.as_view(), name='camera_information_fields_info'),
]