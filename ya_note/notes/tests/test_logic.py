from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.config import (
    BaseClass,
    SUCCESS_URL,
    ADD_URL,
    EDIT_URL,
    DELETE_URL,
)

User = get_user_model()


class TestNoteCreation(BaseClass, TestCase):

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.author_client.post(ADD_URL, data=self.form_data)
        notes_cout = Note.objects.count()
        self.assertEqual(notes_cout, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_notes(self):
        notes_count_before = Note.objects.count()
        self.client.post(ADD_URL, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_empty_slug(self):
        Note.objects.all().delete()
        del self.form_data['slug']
        self.author_client.post(ADD_URL, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_not_unique_slug(self):
        self.author_client.post(ADD_URL, data=self.form_data)
        notes_count = Note.objects.count()
        response = self.author_client.post(
            ADD_URL,
            data=self.form_data
        )
        slug_warning = self.form_data['slug'] + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=slug_warning
        )
        self.assertEqual(notes_count, Note.objects.count())


class TestNoteEditDelete(BaseClass, TestCase):

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_after = Note.objects.count()
        expected_notes_count_after = notes_count_before - 1
        self.assertEqual(notes_count_after, expected_notes_count_after)

    def test_user_cannot_delete_note_of_another_user(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cannot_edit_notes_of_another_user(self):
        response = self.reader_client.post(
            EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
