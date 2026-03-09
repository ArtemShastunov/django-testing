import pytest
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cannot_create_comment(client, news_factory):
    """Анонимный пользователь не может отправить комментарий."""
    news = news_factory()
    comment_count_before = Comment.objects.count()
    url = reverse('news:detail', kwargs={'pk': news.pk})

    response = client.post(
        url,
        data={'text': 'Тестовый комментарий'}
    )

    assert Comment.objects.count() == comment_count_before
    assert response.status_code == 302


@pytest.mark.django_db
def test_authorized_can_create_comment(client, news_factory, user):
    """Авторизованный пользователь может отправить комментарий."""
    news = news_factory()
    comment_count_before = Comment.objects.count()
    url = reverse('news:detail', kwargs={'pk': news.pk})

    client.force_login(user)
    response = client.post(
        url,
        data={'text': 'Тестовый комментарий'}
    )

    assert Comment.objects.count() == comment_count_before + 1
    assert response.status_code == 302


@pytest.mark.django_db
def test_bad_words_in_comment(client, news_factory, user):
    """Комментарий с запрещёнными словами не публикуется."""
    news = news_factory()
    comment_count_before = Comment.objects.count()
    bad_word = BAD_WORDS[0]
    url = reverse('news:detail', kwargs={'pk': news.pk})

    client.force_login(user)
    response = client.post(
        url,
        data={'text': f'Тестовый комментарий с словом {bad_word}'}
    )

    assert Comment.objects.count() == comment_count_before
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_edit_delete_own_comment(client, user, comment_factory):
    """Пользователь может редактировать и удалять свои комментарии."""
    comment = comment_factory(author=user, text='Старый текст')
    client.force_login(user)

    # Редактирование
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.post(
        edit_url,
        data={'text': 'Новый текст'}
    )
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'
    assert response.status_code == 302

    # Удаление
    comment_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.post(delete_url)
    assert Comment.objects.count() == comment_count_before - 1


@pytest.mark.django_db
def test_user_cannot_edit_delete_other_comment(
        client, user, another_user, comment_factory):
    """Пользователь не может редактировать или удалять чужие комментарии."""
    comment = comment_factory(author=another_user, text='Старый текст')
    client.force_login(user)

    # Попытка редактирования
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.post(
        edit_url,
        data={'text': 'Новый текст'}
    )
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == 'Старый текст'

    # Попытка удаления
    comment_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.post(delete_url)
    assert response.status_code == 404
    assert Comment.objects.count() == comment_count_before
