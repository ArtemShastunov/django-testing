import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(username='TestUser', password='pass')


@pytest.fixture
def not_author(db):
    return User.objects.create_user(username='NotAuthor', password='pass')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Тест', text='Текст')


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Коммент'
    )


# Фикстуры для тестов контента
@pytest.fixture
def news_for_count(db):
    """Создаёт 11 новостей для проверки пагинации."""
    now = timezone.now()
    return [
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
            date=now - timedelta(days=i)
        )
        for i in range(11)
    ]


@pytest.fixture
def comments_for_sort(db, news, author):
    """Создаёт комментарии с разными датами для проверки сортировки."""
    now = timezone.now()
    return [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Коммент {i}',
            created=now - timedelta(hours=i)
        )
        for i in range(10)
    ]


# Фикстуры для URL (чтобы не использовать reverse в тестах)
@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})
