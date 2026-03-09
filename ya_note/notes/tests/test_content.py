from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.note_author = Note.objects.create(
            title='Заметка автора',
            text='Текст автора',
            author=cls.author
        )
        cls.note_reader = Note.objects.create(
            title='Заметка читателя',
            text='Текст читателя',
            author=cls.reader
        )

    def test_note_in_object_list(self):
        """Заметка передаётся в списке object_list."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note_author, response.context['object_list'])

    def test_other_user_notes_not_in_list(self):
        """В список заметок не попадают заметки другого пользователя."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.note_reader, response.context['object_list'])

    def test_form_in_create_and_edit_pages(self):
        """На страницы создания и редактирования передаются формы."""
        self.client.force_login(self.author)

        # Страница создания: без аргументов
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

        # Страница редактирования
        url = reverse('notes:edit', args=(self.note_author.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
