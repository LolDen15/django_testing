from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.url_note_list = reverse('notes:list')
        cls.url_note_add = reverse('notes:add')
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_not_in_list_for_another_user(self):
        users_notes = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, notes_list in users_notes:
            with self.subTest(user=user, notes_list=notes_list):
                response = user.get(reverse('notes:list'))
                notes_object = self.note in response.context['object_list']
                self.assertEqual(notes_object, notes_list)

    def test_create_note_page_have_form(self):
        response = self.author_client.get(self.url_note_add)
        self.assertIn('form', response.context)
        form = response.context.get('form')
        self.assertIsInstance(form, NoteForm)

    def test_edit_note_page_have_form(self):
        response = self.author_client.get(self.url_note_edit)
        self.assertIn('form', response.context)
