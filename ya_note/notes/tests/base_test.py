from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    """Базовый класс для тестов с общими фикстурами."""

    @classmethod
    def setUpTestData(cls):
        """Создаём общие объекты для всех тестов."""
        cls.author = User.objects.create_user(
            username='Автор',
            password='pass'
        )
        cls.reader = User.objects.create_user(
            username='Читатель',
            password='pass'
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )

        cls.urls = {
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
            'login': reverse('users:login'),
            'signup': reverse('users:signup'),
            'logout': reverse('users:logout'),
        }

        cls.NEW_TITLE = 'Новый заголовок'
        cls.NEW_TEXT = 'Новый текст'
        cls.NEW_SLUG = 'new-slug'
