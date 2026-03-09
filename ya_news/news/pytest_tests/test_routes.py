import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_main_page_available_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    response = client.get(reverse('news:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_available_anonymous(client, news_factory):
    """Страница отдельной новости доступна анонимному пользователю."""
    news = news_factory()
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_available_to_author(
        client, user, comment_factory):
    """Страницы удаления и редактирования комментария доступны автору."""
    comment = comment_factory(author=user)
    client.force_login(user)

    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.get(edit_url)
    assert response.status_code == 200

    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.get(delete_url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_redirect_anonymous(client, comment_factory):
    """Аноним перенаправляется на страницу авторизации."""
    comment = comment_factory()

    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.get(edit_url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('users:login'))

    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.get(delete_url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_comment_edit_delete_404_for_other_user(
        client, user, another_user, comment_factory):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment = comment_factory(author=another_user)
    client.force_login(user)

    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.get(edit_url)
    assert response.status_code == 404

    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.get(delete_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_available_anonymous(client):
    """Страницы регистрации, входа и выхода доступны анонимным."""
    urls = [
        reverse('users:signup'),
        reverse('users:login'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, f'Страница {url} недоступна'

    response = client.post(reverse('users:logout'))
    assert response.status_code == 200
