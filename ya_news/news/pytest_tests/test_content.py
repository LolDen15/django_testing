import pytest
from django.conf import settings

from news.forms import CommentForm

FORM_NAME = 'form'


@pytest.mark.django_db('news')
def test_authorized_client_has_form(author_client, news_detail_url):
    response = author_client.get(news_detail_url)
    assert FORM_NAME in response.context
    assert isinstance(response.context[FORM_NAME], CommentForm)


@pytest.mark.django_db('news')
def test_anonymous_client_has_no_form(client, news_detail_url):
    response = client.get(news_detail_url)
    assert FORM_NAME not in response.context
    assert not isinstance(response.context.get(FORM_NAME), CommentForm)


@pytest.mark.django_db
def test_comments_order(client, news_detail_url, comments):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert (all_comments[0].created < all_comments[1].created)


@pytest.mark.django_db
def test_news_count(client, news_home_url, news_list):
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_home_url, news_list):
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
