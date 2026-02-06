# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from restapp.models import Attachment, Documents
# from restapp.utils.enumserialize import enum_serialize
#
#
# class AttachmentStageList(APIView):
#
#     def get(self, request):
#         return Response(enum_serialize(Attachment.Stage.choices))
#
#
# class AttachmentStatusList(APIView):
#
#     def get(self, request):
#         return Response(enum_serialize(Attachment.Status.choices))
#
#
# class DocumentTypeList(APIView):
#
#     def get(self, request):
#         return Response(enum_serialize(Documents.Type.choices))