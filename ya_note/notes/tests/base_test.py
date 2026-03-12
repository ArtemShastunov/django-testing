from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='Автор',
            password='pass'
        )
        cls.reader = User.objects.create_user(
            username='Читатель',
            password='pass'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            slug='other-slug',
            author=cls.reader
        )
        cls.urls = {
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
            'success': reverse('notes:success'),
            'login': reverse('users:login'),
            'signup': reverse('users:signup'),
            'logout': reverse('users:logout'),
        }
        cls.NEW_TITLE = 'Новый заголовок'
        cls.NEW_TEXT = 'Новый текст'
        cls.NEW_SLUG = 'new-slug'

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
