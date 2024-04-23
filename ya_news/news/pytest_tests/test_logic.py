from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {
    'text': 'Новый текст',
}
BAD_WORDS_DATA = {
    'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
}


def test_user_can_create_note(
        author_client,
        author,
        news):
    initial_comment_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == initial_comment_count + 1
    new_comment = Comment.objects.latest('id')
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cannot_create_note(client, news):
    count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == count


def test_user_cannot_use_bad_words(
        author_client,
        news):
    count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=BAD_WORDS_DATA)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == count


def test_author_can_edit_comment(
        author_client,
        comment,
        edit_url,
        url_to_comments):
    response = author_client.post(
        edit_url,
        data=FORM_DATA
    )
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_other_user_cannot_edit_comment(
        admin_client,
        comment,
        edit_url):
    response = admin_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
        author_client,
        delete_url,
        url_to_comments):
    count = Comment.objects.count() - 1
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == count


def test_other_user_cannot_delete_comment(admin_client, delete_url):
    count = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count
