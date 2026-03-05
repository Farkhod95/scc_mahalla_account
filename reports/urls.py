from django.urls import re_path, path

from reports.views.detection_count_api import DetectionCountProxyView
from reports.views.face_detection_count_api import FaceDetectionCountProxyView
from reports.views.malika_flow import MalikaFlowProxy

urlpatterns = [
    path("reports/drb/detection-count/", DetectionCountProxyView.as_view(), name="drf-detection-count"),
    path("reports/face/detection-count", FaceDetectionCountProxyView.as_view(),
        name="face-detection-count-proxy",),
    path("reports/malika-flow", MalikaFlowProxy.as_view(), name="malika-flow-report"),
]