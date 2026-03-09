from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author
        )

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        note_count_before = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data={
            'title': 'Новая заметка',
            'text': 'Текст'
        })
        self.assertEqual(Note.objects.count(), note_count_before)
        self.assertEqual(response.status_code, 302)

    def test_authorized_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.author)
        note_count_before = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data={
            'title': 'Новая заметка',
            'text': 'Текст'
        })
        self.assertEqual(Note.objects.count(), note_count_before + 1)
        self.assertEqual(response.status_code, 302)

    def test_slug_unique(self):
        """Нельзя создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        # Первая заметка создаётся успешно
        response = self.client.post(url, data={
            'title': 'Одинаковый заголовок',
            'text': 'Текст 1'
        })
        self.assertEqual(response.status_code, 302)
        # Вторая с таким же title (и slug) должна вернуть форму с ошибкой
        response = self.client.post(url, data={
            'title': 'Одинаковый заголовок',
            'text': 'Текст 2'
        })
        self.assertEqual(response.status_code, 200)

    def test_slug_auto_generated(self):
        """Если slug не заполнен, он формируется автоматически."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data={
            'title': 'Тест для слага',
            'text': 'Текст'
        })
        note = Note.objects.get(title='Тест для слага')
        expected_slug = slugify('Тест для слага')
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_delete_own_note(self):
        """Пользователь может редактировать и удалять свои заметки."""
        self.client.force_login(self.author)
        # Редактирование
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(edit_url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст'
        })
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Новый заголовок')
        self.assertEqual(response.status_code, 302)
        # Удаление
        note_count_before = Note.objects.count()
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(delete_url)
        self.assertEqual(Note.objects.count(), note_count_before - 1)

    def test_user_cannot_edit_delete_other_note(self):
        """Пользователь не может редактировать или удалять чужие заметки."""
        self.client.force_login(self.reader)
        # Попытка редактирования
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(edit_url, data={
            'title': 'Взломанный заголовок',
            'text': 'Взломанный текст'
        })
        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Тестовая заметка')
        # Попытка удаления
        note_count_before = Note.objects.count()
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), note_count_before)
