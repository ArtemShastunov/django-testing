import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_main_page(client, news_for_count, home_url):
    """На главной странице ровно лимит новостей."""
    response = client.get(home_url)
    news_list = response.context['object_list']
    assert news_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_newest_first(client, news_for_count, home_url):
    """Новости отсортированы от новой к старой."""
    response = client.get(home_url)
    news_list = list(response.context['object_list'])
    dates = [n.date for n in news_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


def test_comments_sorted_chronologically(
        client, comments_for_sort, news, detail_url):
    """Комментарии отсортированы от старого к новому."""
    response = client.get(detail_url)
    comments = list(response.context['object'].comment_set.all())
    timestamps = [c.created for c in comments]
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
    """Форма комментария: анониму нет, авторизованному есть."""
    client = request.getfixturevalue(client_fixture)
    response = client.get(detail_url)
    has_form = 'form' in response.context
    assert has_form is should_have_form
    if should_have_form:
        assert isinstance(
            response.context['form'],
            CommentForm
        )
