from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author
        )

    def test_home_page_available_anonymous(self):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_authenticated(self):
        """Страницы доступны авторизованному пользователю."""
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_anonymous(self):
        """Аноним перенаправляется на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_edit_delete_404_for_other_user(self):
        """Пользователь не может редактировать/удалять чужие заметки (404)."""
        self.client.force_login(self.reader)
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auth_pages_available_anonymous(self):
        """Страницы регистрации, входа и выхода доступны анонимным."""
        urls = [
            ('users:signup', None),
            ('users:login', None),
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Logout требует POST
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
