from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.tests.config import (
    BaseClass,
    HOME_URL,
    LIST_URL,
    ADD_URL,
    DELETE_URL,
    EDIT_URL,
    DETAIL_URL,
    SUCCESS_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL
)

User = get_user_model()


class TestRoutes(BaseClass, TestCase):

    def test_availability_for_note_edit_and_delete(self):
        users_notes = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_notes:
            urls = (
                DETAIL_URL,
                EDIT_URL,
                DELETE_URL,
            )
            for name in urls:
                with self.subTest(user=user, status=status, name=name):
                    url = name
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        urls = (
            HOME_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_list_success_add(self):
        urls = (
            LIST_URL,
            SUCCESS_URL,
            ADD_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_edit_delete(self):
        urls = (
            DELETE_URL,
            EDIT_URL,
            DETAIL_URL
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_author_notes_done_add(self):
        urls = (
            LIST_URL,
            SUCCESS_URL,
            ADD_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
