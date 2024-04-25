from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.forms import NoteForm
from notes.tests.config import (
    BaseClass,
    LIST_URL,
    ADD_URL,
    EDIT_URL,
)

User = get_user_model()


class TestContent(BaseClass, TestCase):

    def test_note_not_in_list_for_another_user(self):
        users_notes = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, notes_list in users_notes:
            with self.subTest(user=user, notes_list=notes_list):
                response = user.get(LIST_URL)
                notes_object = self.note in response.context['object_list']
                self.assertIs(notes_object, notes_list)

    def test_note_pages_have_form(self):
        urls = [ADD_URL, EDIT_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context.get('form')
                self.assertIsInstance(form, NoteForm)
