import pytest
from django.conf import settings


pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, news_for_count, home_url):
    """На главной странице не более NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(home_url)
    news_list = response.context['object_list']
    assert len(news_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_newest_first(client, news_for_count, home_url):
    """Новости отсортированы от свежей к старой."""
    response = client.get(home_url)
    news_list = response.context['object_list']

    dates = [news.date for news in news_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


def test_comments_sorted_chronologically(
        client, news, comments_for_sort, detail_url):
    """Комментарии отсортированы от старых к новым."""
    response = client.get(detail_url)
    comments = response.context['object'].comment_set.all()

    timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(timestamps)
    assert timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'client_fixture, should_have_form',
    [
        ('client', False),
        ('author_client', True),
    ]
)
def test_comment_form_availability(
        client_fixture, should_have_form, request, news, detail_url):
    """Анониму форма недоступна, авторизованному доступна."""
    client = request.getfixturevalue(client_fixture)
    response = client.get(detail_url)

    if should_have_form:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context
