from http import HTTPStatus

from django.test import Client, TestCase

from ..urls import app_name


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages(self):
        urls = {
            f'/{app_name}/author/',
            f'/{app_name}/tech/',
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(HTTPStatus.OK.value, response.status_code)
