from django.urls import re_path, path

from reports.views.center_of_civilization import CenterOfCivilizationReportView
from reports.views.detection_count_api import DetectionCountProxyView
from reports.views.face_detection_count_api import FaceDetectionCountProxyView
from reports.views.malika_dashboard import MalikaDashboardReportView
from reports.views.malika_flow import MalikaFlowReportView
from reports.views.sales_revenue_excel import SalesRevenueExcelView
from reports.views.tax_revenue import TaxRevenueReportView

urlpatterns = [
    path("reports/drb/detection-count", DetectionCountProxyView.as_view(), name="drf-detection-count"),
    path("reports/face/detection-count", FaceDetectionCountProxyView.as_view(),
        name="face-detection-count-proxy",),
    path("reports/malika-flow", MalikaFlowReportView.as_view(), name="malika-flow-report"),
    path("reports/center-of-civilization", CenterOfCivilizationReportView.as_view(), name="civilization-report"),
    path("reports/dashboard", MalikaDashboardReportView.as_view(), name="malika-dashboard-report"),
    path("reports/tax-revenue", TaxRevenueReportView.as_view(), name="tax-revenue-report"),
    path("reports/sales-revenue/excel", SalesRevenueExcelView.as_view(), name="sales-revenue-excel"),

]