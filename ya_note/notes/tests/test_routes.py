from http import HTTPStatus

from .base_test import BaseTest


class TestRoutes(BaseTest):

    def test_home_page_available_anonymous(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get(self.urls['home'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_authenticated(self):
        """Страницы доступны авторизованному пользователю."""
        urls_to_test = [
            self.urls['list'],
            self.urls['success'],
            self.urls['add'],
            self.urls['detail'],
            self.urls['edit'],
            self.urls['delete'],
        ]
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_pages_redirect_anonymous(self):
        """Аноним перенаправляется на страницу логина."""
        urls_to_test = [
            self.urls['list'],
            self.urls['success'],
            self.urls['add'],
            self.urls['detail'],
            self.urls['edit'],
            self.urls['delete'],
        ]
        for url in urls_to_test:
            with self.subTest(url=url):
                expected = f'{self.urls["login"]}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected)

    def test_edit_delete_404_for_other_user(self):
        """Пользователь не может редактировать/удалять чужие заметки."""
        urls = [
            self.urls['detail'],
            self.urls['edit'],
            self.urls['delete'],
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND
                )

    def test_auth_pages_available_anonymous(self):
        """Страницы auth доступны анонимным."""
        for url in [self.urls['signup'], self.urls['login']]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

        response = self.client.post(self.urls['logout'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
