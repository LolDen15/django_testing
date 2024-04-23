from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

HOME_URL = 'notes:home'
LIST_URL = 'notes:list'
ADD_URL = 'notes:add'
DELETE_URL = 'notes:delete'
EDIT_URL = 'notes:edit'
DETAIL_URL = 'notes:detail'
SUCCESS_URL = 'notes:success'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='slug'
        )

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
                    url = reverse(name, args=(self.note.slug,))
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
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_list_success_add(self):
        login_url = reverse(LOGIN_URL)
        urls = (
            LIST_URL,
            SUCCESS_URL,
            ADD_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_edit_delete(self):
        login_url = reverse(LOGIN_URL)
        urls = (
            DELETE_URL,
            EDIT_URL,
            DETAIL_URL
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
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
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
