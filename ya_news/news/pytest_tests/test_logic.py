from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'client_fixture, should_create',
    [
        ('client', False),
        ('author_client', True),
    ]
)
def test_create_comment(
        client_fixture, should_create, request, news, detail_url):
    """Создание комментария: аноним не может, автор может."""
    client = request.getfixturevalue(client_fixture)
    before = Comment.objects.count()

    response = client.post(detail_url, data={'text': 'Тестовый комментарий'})

    after = Comment.objects.count()
    assert (after - before) == should_create

    if should_create:
        comment = Comment.objects.get()
        assert comment.author.username == 'TestUser'
        assert comment.news == news
        redirect_url = f'{detail_url}#comments'
        assertRedirects(response, redirect_url)
    else:
        assert response.status_code == HTTPStatus.FOUND


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_bad_words_in_comment(bad_word, author_client, news, detail_url):
    """Комментарий с запрещённым словом не публикуется."""
    before = Comment.objects.count()

    response = author_client.post(
        detail_url,
        data={'text': f'Текст с {bad_word}'}
    )

    assert Comment.objects.count() == before
    assert response.status_code == HTTPStatus.OK

    form = response.context['form']
    assertFormError(form, 'text', WARNING)


def test_author_can_edit_comment(author_client, comment, edit_url):
    """Автор может редактировать свой комментарий."""
    new_text = 'Новый текст комментария'

    response = author_client.post(edit_url, data={'text': new_text})

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == new_text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
    detail = reverse('news:detail', kwargs={'pk': comment.news.pk})
    assertRedirects(response, f'{detail}#comments')


def test_other_user_cannot_edit_comment(
        not_author_client, comment, edit_url):
    """Другой пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(edit_url, data={'text': 'Взлом'})

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_delete_comment(
        author_client, comment, delete_url, news):
    """Автор может удалить свой комментарий."""
    before = Comment.objects.count()

    response = author_client.post(delete_url)

    assert Comment.objects.count() == before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()
    detail = reverse('news:detail', kwargs={'pk': news.pk})
    assertRedirects(response, f'{detail}#comments')


def test_other_user_cannot_delete_comment(
        not_author_client, comment, delete_url):
    """Другой пользователь не может удалить чужой комментарий."""
    before = Comment.objects.count()

    response = not_author_client.post(delete_url)

    assert Comment.objects.count() == before
    assert Comment.objects.filter(pk=comment.pk).exists()
    assert response.status_code == HTTPStatus.NOT_FOUND
