import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def user(db):
    """Создаёт тестового пользователя."""
    return User.objects.create_user(
        username='TestUser',
        password='password'
    )


@pytest.fixture
def another_user(db):
    """Создаёт второго тестового пользователя."""
    return User.objects.create_user(
        username='AnotherUser',
        password='password'
    )


@pytest.fixture
def news_factory(db):
    """Фабрика для создания новостей."""
    def create_news(**kwargs):
        defaults = {
            'title': 'Тестовая новость',
            'text': 'Текст тестовой новости',
            'date': timezone.now().date(),
        }
        defaults.update(kwargs)
        return News.objects.create(**defaults)
    return create_news


@pytest.fixture
def comment_factory(db, user, news_factory):
    """Фабрика для создания комментариев."""
    def create_comment(**kwargs):
        defaults = {
            'author': user,
            'news': news_factory(),
            'text': 'Тестовый комментарий',
        }
        defaults.update(kwargs)
        return Comment.objects.create(**defaults)
    return create_comment
