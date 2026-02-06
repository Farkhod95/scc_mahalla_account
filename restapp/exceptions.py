from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotAuthenticated, AuthenticationFailed
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        response.data = {
            'errorCode': status.HTTP_404_NOT_FOUND,
            'errorMessage': 'Not Found'
        }

    if isinstance(exc, ValidationError):
        response.data = {
            'message': exc.detail,
            'errorCode': status.HTTP_400_BAD_REQUEST,
            'errorMessage': 'Bad Request'
        }

    if isinstance(exc, NotAuthenticated) or isinstance(exc, AuthenticationFailed):
        response.data = {
            'message': {'password': 'Wrong Email or Password'}
        }

    return response
