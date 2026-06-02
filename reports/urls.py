from django.urls import re_path, path

from reports.views.center_of_civilization import CenterOfCivilizationReportView
from reports.views.detection_count_api import DetectionCountProxyView
from reports.views.face_detection_count_api import FaceDetectionCountProxyView
from reports.views.malika_dashboard import MalikaDashboardReportView
from reports.views.malika_flow import MalikaFlowReportView
from reports.views.revenue_chart import RevenueChartView

urlpatterns = [
    path("reports/drb/detection-count", DetectionCountProxyView.as_view(), name="drf-detection-count"),
    path("reports/face/detection-count", FaceDetectionCountProxyView.as_view(),
        name="face-detection-count-proxy",),
    path("reports/malika-flow", MalikaFlowReportView.as_view(), name="malika-flow-report"),
    path("reports/center-of-civilization", CenterOfCivilizationReportView.as_view(), name="civilization-report"),
    path("reports/dashboard", MalikaDashboardReportView.as_view(), name="malika-dashboard-report"),
    path("reports/revenue-chart", RevenueChartView.as_view(), name="revenue-chart"),

]