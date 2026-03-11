import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db

# Константы вместо фикстур
BAD_WORDS_LIST = BAD_WORDS
FORM_DATA = {'text': 'Тестовый комментарий'}


@pytest.fixture
def user(db):
    """Фикстура: тестовый пользователь."""
    return User.objects.create_user(
        username='TestUser',
        password='password'
    )


@pytest.fixture
def another_user(db):
    """Фикстура: второй тестовый пользователь."""
    return User.objects.create_user(
        username='AnotherUser',
        password='password'
    )


@pytest.fixture
def author_client(user):
    """Фикстура: клиент с авторизованным пользователем."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def not_author_client(another_user):
    """Фикстура: клиент с другим пользователем."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def news(db):
    """Фикстура: тестовая новость."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
        date=timezone.now().date()
    )


@pytest.fixture
def news_for_count(db):
    """Фикстура: новости для теста пагинации."""
    count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    now = timezone.now().date()
    for i in range(count):
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
            date=now - timezone.timedelta(days=i)
        )


@pytest.fixture
def comment(db, user, news):
    """Фикстура: комментарий от автора."""
    return Comment.objects.create(
        author=user,
        news=news,
        text='Тестовый комментарий'
    )


@pytest.fixture
def comments_for_sort(db, user, news):
    """Фикстура: комментарии с разным временем для сортировки."""
    now = timezone.now()
    for i in range(3):
        c = Comment.objects.create(
            author=user,
            news=news,
            text=f'Комментарий {i}',
        )
        c.created = now - timezone.timedelta(hours=2 - i)
        c.save()


@pytest.fixture
def home_url():
    """Фикстура: URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Фикстура: URL страницы логина."""
    return reverse('users:login')


@pytest.fixture
def detail_url(news):
    """Фикстура: URL страницы новости."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def edit_url(comment):
    """Фикстура: URL редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def delete_url(comment):
    """Фикстура: URL удаления комментария."""
    return reverse('news:delete', kwargs={'pk': comment.pk})
