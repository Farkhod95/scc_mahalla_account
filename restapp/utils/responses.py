from rest_framework import status


def content(data):
    return {'data': data, 'statusCode': status.HTTP_201_CREATED}


def nonContent():
    return {'statusCode': status.HTTP_204_NO_CONTENT}
