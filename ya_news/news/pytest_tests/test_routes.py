from http import HTTPStatus

import pytest
from django.urls import reverse

from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('home_url', 'author_client', HTTPStatus.OK),
        ('home_url', 'not_author_client', HTTPStatus.OK),
    ]
)
def test_home_page_status(
        url_fixture, client_fixture, expected_status, request):
    """Главная страница доступна всем."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        ('client', HTTPStatus.FOUND),
        ('author_client', HTTPStatus.OK),
        ('not_author_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_edit_page_status(
        client_fixture, expected_status, request, comment):
    """Страница редактирования комментария."""
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        ('client', HTTPStatus.FOUND),
        ('author_client', HTTPStatus.OK),
        ('not_author_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_delete_page_status(
        client_fixture, expected_status, request, comment):
    """Страница удаления комментария."""
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name, expected_status',
    [
        ('users:signup', HTTPStatus.OK),
        ('users:login', HTTPStatus.OK),
    ]
)
def test_auth_pages_get_status(url_name, expected_status, client):
    """Страницы auth доступны GET запросом."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == expected_status


def test_logout_page_post_status(client):
    """Страница logout доступна POST запросом."""
    url = reverse('users:logout')
    response = client.post(url)
    # Logout с template_name возвращает 200 в Django 5.x
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    [
        'news:edit',
        'news:delete',
    ]
)
def test_redirect_anonymous_to_login(url_name, client, comment, login_url):
    """Аноним перенаправляется на страницу логина."""
    url = reverse(url_name, kwargs={'pk': comment.pk})
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
