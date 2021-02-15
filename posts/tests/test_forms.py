import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group


User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class NewPostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user('Dike', 'admin@test.com', 'pass')

        cls.group = Group.objects.create(
            title='Vsem privet',
            slug='test-slug',
            description='Gruppa chtoby govorit privet',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='Mike')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_post_page_create(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {'group': NewPostFormTest.group.id,
                     'text': 'Текст, который мы заслужили',
                     'image': uploaded,
                     }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        latest_post = response.context.get('page')[0]
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(latest_post.text, 'Текст, который мы заслужили')
        self.assertEqual(latest_post.group, NewPostFormTest.group)
        self.assertIsNotNone(latest_post.image.url)

    def test_post_edit_form(self):
        post = Post.objects.create(
            author=self.user,
            text='Старый текст.',
            group=NewPostFormTest.group,
        )
        posts_count = Post.objects.count()
        data = {'group': NewPostFormTest.group.id,
                'text': 'Новый текст'}
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={"username": self.user.username, "post_id": post.id}),
            data=data,
            follow=True
        )
        post.refresh_from_db()
        self.assertRedirects(response, reverse('post',
                                               kwargs={"username": self.user.username,
                                                       "post_id": post.id}))
        self.assertEqual(post.text, 'Новый текст')
        self.assertEqual(Post.objects.count(), posts_count)
