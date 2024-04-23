from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

ADD_URL = 'notes:add'
DELETE_URL = 'notes:delete'
EDIT_URL = 'notes:edit'
DETAIL_URL = 'notes:detail'
SUCCESS_URL = 'notes:success'


class TestNoteCreation(TestCase):
    NEW_NOTE_TITLE = 'Новый текст заголовка'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.url_add = reverse(ADD_URL)
        cls.url = reverse(ADD_URL)
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_user_can_create_note(self):
        self.author_client.post(self.url, data=self.form_data)
        notes_cout = Note.objects.count()
        self.assertEqual(notes_cout, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_notes(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        del self.form_data['slug']
        self.author_client.post(self.url_add, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_unique_slug1(self):
        self.author_client.post(self.url, data=self.form_data)
        response = self.author_client.post(self.url, data=self.form_data)
        slug_warning = self.form_data['slug'] + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=slug_warning
        )


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug'

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'new_slug'

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
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )
        cls.url_success = reverse(SUCCESS_URL)
        cls.url = reverse(DETAIL_URL, args=(cls.note.slug,))
        cls.url_edit = reverse(EDIT_URL, args=(cls.note.slug,))
        cls.url_delete = reverse(DELETE_URL, args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NEW_NOTE_TEXT,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 1)
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, 0)

    def test_user_cannot_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cannot_edit_notes_of_another_user(self):
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
