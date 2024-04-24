from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')
DELETE_URL = pytest.lazy_fixture('delete_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')


@pytest.mark.parametrize(
    'url',
    (HOME_URL, LOGOUT_URL, SIGNUP_URL)
)
def test_pages_availability_for_anonymous_user(client, url, login_url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_pages_availability_for_author(author_client, url, comment):
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (READER_CLIENT, HTTPStatus.NOT_FOUND),
        (AUTHOR_CLIENT, HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_pages_availability_for_different_users(
        parametrized_client,
        url,
        comment,
        expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, news_object',
    (
        (EDIT_URL, pytest.lazy_fixture('news')),
        (DELETE_URL, pytest.lazy_fixture('news')),
    ),
)
def test_redirects(client, name, news_object, login_url):
    expected_url = f'{login_url}?next={name}'
    response = client.get(name, args=(news_object.id,))
    assertRedirects(response, expected_url)
