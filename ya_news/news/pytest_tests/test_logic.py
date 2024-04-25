from http import HTTPStatus

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
        news,
        news_detail_url):
    initial_comment_count = Comment.objects.count()
    url = news_detail_url
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == initial_comment_count + 1
    new_comment = Comment.objects.latest('id')
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_anonymous_user_cannot_create_note(client, news, news_detail_url):
    count = Comment.objects.count()
    url = news_detail_url
    response = client.post(url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == count


def test_user_cannot_use_bad_words(
        author_client,
        news,
        news_detail_url):
    count = Comment.objects.count()
    url = news_detail_url
    response = author_client.post(url, data=BAD_WORDS_DATA)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == count


def test_author_can_edit_comment(
        author,
        author_client,
        news,
        comment,
        edit_url,
        url_to_comments):
    response = author_client.post(
        edit_url,
        data=FORM_DATA
    )
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_other_user_cannot_edit_comment(
        reader_client,
        comment,
        edit_url):
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
        author_client,
        delete_url,
        url_to_comments):
    count = Comment.objects.count() - 1
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == count


def test_other_user_cannot_delete_comment(reader_client, delete_url):
    count = Comment.objects.count()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count
