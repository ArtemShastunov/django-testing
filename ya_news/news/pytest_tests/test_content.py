import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_news_count_on_main_page(client, news_factory):
    """На главной странице не более NEWS_COUNT_ON_HOME_PAGE новостей."""
    for _ in range(15):
        news_factory()

    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']

    assert len(news_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_newest_first(client, news_factory):
    """Новости отсортированы от свежей к старой."""
    now = timezone.now().date()
    news_old = news_factory(date=now - timedelta(days=5))
    news_middle = news_factory(date=now - timedelta(days=2))
    news_new = news_factory(date=now - timedelta(days=1))

    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']

    assert news_list[0] == news_new
    assert news_list[1] == news_middle
    assert news_list[2] == news_old


@pytest.mark.django_db
def test_comments_sorted_chronologically(
        client, news_factory, comment_factory):
    """Комментарии отсортированы от старых к новым."""
    news = news_factory()
    now = timezone.now()

    comment_old = comment_factory(
        news=news,
        created=now - timedelta(hours=2)
    )
    comment_middle = comment_factory(
        news=news,
        created=now - timedelta(hours=1)
    )
    comment_new = comment_factory(news=news, created=now)

    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    comments = response.context['object'].comment_set.all()

    assert comments[0] == comment_old
    assert comments[1] == comment_middle
    assert comments[2] == comment_new


@pytest.mark.django_db
def test_comment_form_availability(client, news_factory, user):
    """Анониму форма недоступна, авторизованному доступна."""
    news = news_factory()
    url = reverse('news:detail', kwargs={'pk': news.pk})

    # Анонимный пользователь
    response = client.get(url)
    assert 'form' not in response.context

    # Авторизованный пользователь
    client.force_login(user)
    response = client.get(url)
    assert 'form' in response.context
