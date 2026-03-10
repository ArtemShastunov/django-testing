from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'client_fixture, should_create',
    [
        ('client', False),
        ('author_client', True),
    ]
)
def test_anonymous_cannot_create_comment(
        client_fixture, should_create, request, form_data, news):
    """Анонимный пользователь не может создать комментарий."""
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:detail', kwargs={'pk': news.pk})
    before = Comment.objects.count()

    response = client.post(url, data=form_data)

    if should_create:
        assert Comment.objects.count() == before + 1
        comment = Comment.objects.get(text=form_data['text'])
        assert comment.author.username == 'TestUser'
        assert comment.news == news
        assertRedirects(response, f'{url}#comments')
    else:
        assert Comment.objects.count() == before
        assert response.status_code == HTTPStatus.FOUND


@pytest.mark.parametrize('bad_word', ['редиска', 'негодяй'])
def test_bad_words_in_comment(
        bad_word, author_client, form_data, news):
    """Комментарий с запрещённым словом не публикуется."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data['text'] = f'Текст с {bad_word}'
    response = author_client.post(url, data=form_data)

    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.OK

    form = response.context['form']
    assertFormError(form, 'text', WARNING)


def test_author_can_edit_comment(
        author_client, comment, form_data):
    """Автор может редактировать свой комментарий."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Новый текст комментария'
    form_data['text'] = new_text

    response = author_client.post(url, data=form_data)

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == new_text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
    assertRedirects(response, f'/news/{comment.news.pk}/#comments')


def test_other_user_cannot_edit_comment(
        not_author_client, comment, form_data):
    """Другой пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    original_text = comment.text

    response = not_author_client.post(url, data=form_data)

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == original_text
    assert comment_from_db.author == comment.author
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_delete_comment(author_client, comment):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    before = Comment.objects.count()

    response = author_client.post(url)

    assert Comment.objects.count() == before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assertRedirects(response, f'/news/{comment.news.pk}/#comments')


def test_other_user_cannot_delete_comment(
        not_author_client, comment):
    """Другой пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    before = Comment.objects.count()

    response = not_author_client.post(url)

    assert Comment.objects.count() == before
    assert Comment.objects.filter(pk=comment.pk).exists()
    assert response.status_code == HTTPStatus.NOT_FOUND
