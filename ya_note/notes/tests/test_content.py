from notes.forms import NoteForm
from notes.models import Note

from .base_test import BaseTest


class TestContent(BaseTest):

    def test_note_in_object_list(self):
        """Заметка автора в списке его заметок."""
        response = self.author_client.get(self.urls['list'])
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_notes_not_in_list(self):
        """Чужие заметки не в списке."""
        response = self.author_client.get(self.urls['list'])
        object_list = response.context['object_list']
        other = Note.objects.create(
            title='Чужая',
            text='Текст',
            slug='other',
            author=self.reader
        )
        self.assertNotIn(other, object_list)

    def test_form_in_create_and_edit_pages(self):
        """Форма есть на страницах создания и редактирования."""
        for url in [self.urls['add'], self.urls['edit']]:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm
                )
