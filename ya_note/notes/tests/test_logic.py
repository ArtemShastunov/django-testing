from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from pytest_django.asserts import assertFormError

from .base_test import BaseTest


class TestLogic(BaseTest):

    def test_anonymous_cannot_create_note(self):
        """Аноним не может создать заметку."""
        before = Note.objects.count()
        response = self.client.post(self.urls['add'], data={
            'title': self.NEW_TITLE,
            'text': self.NEW_TEXT,
            'slug': self.NEW_SLUG,
        })
        self.assertEqual(Note.objects.count(), before)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_can_create_note(self):
        """Авторизованный может создать заметку."""
        Note.objects.all().delete()
        before = Note.objects.count()

        response = self.author_client.post(self.urls['add'], data={
            'title': self.NEW_TITLE,
            'text': self.NEW_TEXT,
        })

        self.assertEqual(Note.objects.count(), before + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NEW_TITLE)
        self.assertEqual(new_note.text, self.NEW_TEXT)
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_slug_unique(self):
        """Нельзя создать две заметки с одинаковым slug."""
        before = Note.objects.count()
        response = self.author_client.post(self.urls['add'], data={
            'title': 'Дубликат',
            'text': 'Текст',
            'slug': self.note.slug,
        })
        self.assertEqual(Note.objects.count(), before)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context['form']
        assertFormError(form, 'slug', self.note.slug + WARNING)

    def test_slug_auto_generated(self):
        """Slug генерируется автоматически, если не указан."""
        Note.objects.all().delete()
        test_title = 'Тест для слага'

        self.author_client.post(self.urls['add'], data={
            'title': test_title,
            'text': 'Текст',
        })

        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(test_title)
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.urls['edit'], data={
            'title': self.NEW_TITLE,
            'text': self.NEW_TEXT,
            'slug': self.NEW_SLUG,
        })
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.NEW_TITLE)
        self.assertEqual(note.text, self.NEW_TEXT)
        self.assertEqual(note.slug, self.NEW_SLUG)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_cannot_edit_other_note(self):
        """Нельзя редактировать чужую заметку."""
        response = self.reader_client.post(self.urls['edit'], data={
            'title': 'Взлом',
            'text': 'Взлом',
            'slug': 'hacked',
        })

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_note(self):
        """Автор может удалить свою заметку."""
        before = Note.objects.count()
        response = self.author_client.post(self.urls['delete'])
        self.assertEqual(Note.objects.count(), before - 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_cannot_delete_other_note(self):
        """Нельзя удалить чужую заметку."""
        before = Note.objects.count()
        response = self.reader_client.post(self.urls['delete'])
        self.assertEqual(Note.objects.count(), before)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
