from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status, method',
    [
        ('home_url', 'client', HTTPStatus.OK, 'get'),
        ('home_url', 'author_client', HTTPStatus.OK, 'get'),
        ('home_url', 'not_author_client', HTTPStatus.OK, 'get'),
        ('edit_url', 'client', HTTPStatus.FOUND, 'get'),
        ('edit_url', 'author_client', HTTPStatus.OK, 'get'),
        ('edit_url', 'not_author_client', HTTPStatus.NOT_FOUND, 'get'),
        ('delete_url', 'client', HTTPStatus.FOUND, 'get'),
        ('delete_url', 'author_client', HTTPStatus.OK, 'get'),
        ('delete_url', 'not_author_client', HTTPStatus.NOT_FOUND, 'get'),
        ('login_url', 'client', HTTPStatus.OK, 'get'),
        ('login_url', 'client', HTTPStatus.OK, 'post'),
    ]
)
def test_page_status(
        url_fixture, client_fixture, expected_status, method, request):
    """Проверка статус-кодов страниц."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)

    if method == 'get':
        response = client.get(url)
    else:
        response = client.post(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name',
    ['users:signup', 'users:login']
)
def test_auth_pages_get_status(url_name, client):
    """Страницы auth доступны GET запросом."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_page_post_status(client):
    """Страница logout доступна POST запросом."""
    response = client.post(reverse('users:logout'))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    ['edit_url', 'delete_url']
)
def test_redirect_anonymous_to_login(
        url_fixture, client, request, login_url):
    """Аноним перенаправляется на страницу логина."""
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
