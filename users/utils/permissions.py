from itertools import groupby
from operator import itemgetter


def get_user_permissions(groups):
    permissions, result = [], []
    for group in groups:
        for permission in group.permissions.all():
            code_name = permission.codename.split('_')
            permissions.append({
                "model": code_name[1].upper(),
                "permission": code_name[0].upper()
            })

    permissions = sorted(permissions, key=itemgetter('model'))

    for key, value in groupby(permissions, key=itemgetter('model')):
        result.append({key: [val["permission"] for val in value]})

    return result
