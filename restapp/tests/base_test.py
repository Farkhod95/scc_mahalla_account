import json
from pprint import pprint
from django.urls import reverse
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        response = self.client.post(reverse('token_obtain_pair'), {"username": "api_user1", "password": "1Q9LPxyg"})
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def dump(self, response):
        print('-' * 40)
        print('Response:', response.status_code)
        pprint(json.loads(json.dumps(response.data)))
        print('-' * 40)
