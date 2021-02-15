import datetime
import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Vsem privet',
            slug='test-slug',
            description='Gruppa chtoby govorit privet',
        )

        cls.group_2 = Group.objects.create(
            title='Vsem privet_2',
            slug='test-slug-2',
            description='Gruppa chtoby govorit privet_2',
        )
        cls.user = User.objects.create_user('Dike', 'admin@test.com', 'pass')
        for i in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Текст{i}',
                group=cls.group,
            )
            cls.post.pub_date -= datetime.timedelta(minutes=20 - i)
            cls.post.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Mike')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-slug'}),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        context = response.context
        self.assertIsInstance(context.get('form'), PostForm)

        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            form_field = context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_homepage_context(self):
        response = self.authorized_client.get(reverse('index'))
        page = response.context.get('page')
        page_posts = page.object_list
        first_post = page_posts[0]
        first_post_text = first_post.text
        last_post = page_posts[9]
        last_post_text = last_post.text
        self.assertEqual(first_post_text, 'Текст14')
        self.assertEqual(last_post_text, 'Текст5')

    def test_homepage_first_page_has_10_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_homepage_second_page_has_5_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 5)

    def test_group_page_context(self):
        response = self.authorized_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context.get('group').title, 'Vsem privet')
        self.assertEqual(response.context.get('group').description, 'Gruppa chtoby govorit privet')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_group_first_page_has_10_records(self):
        response = self.authorized_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_post_group_is_ok(self):
        post = Post.objects.create(
            author=PostPagesTests.user,
            text='New post',
            group=PostPagesTests.group,
        )

        response = self.authorized_client.get(reverse('index'))
        page = response.context.get('page')
        page_posts = page.object_list
        self.assertIn(post, page_posts)

        response_group = self.authorized_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        page = response_group.context.get('page')
        group_all_posts = page.object_list
        self.assertIn(post, group_all_posts)

        response_group_2 = self.authorized_client.get(reverse('group', kwargs={'slug': 'test-slug-2'}))
        page = response_group_2.context.get('page')
        group_all_posts_2 = page.object_list
        self.assertNotIn(post, group_all_posts_2)

    def test_profile_page_context(self):
        post = PostPagesTests.post
        user = post.author
        response = self.authorized_client.get(reverse('profile', kwargs={'username': user}))
        self.assertEqual(response.context.get('author'), user)
        self.assertEqual(response.context.get('paginator').count, 15)

    def test_profile_first_page_has_10_records(self):
        post = PostPagesTests.post
        user = post.author
        response = self.authorized_client.get(reverse('profile', kwargs={'username': user}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_post_view_page_context(self):
        post = PostPagesTests.post
        user = post.author
        post_id = post.id
        response = self.authorized_client.get(reverse('post', kwargs={'username': user, 'post_id': post_id}))
        self.assertEqual(response.context.get('author'), user)
        self.assertEqual(response.context.get('post').id, post.id)

    def test_post_edit_page_context(self):
        post = Post.objects.create(
            author=self.user,
            text='New post',
            group=PostPagesTests.group,
        )
        username = post.author.username
        author_client = Client()
        author_client.force_login(post.author)
        post_id = post.id
        response = author_client.get(reverse('post_edit', kwargs={'username': username, 'post_id': post_id}))
        self.assertEqual(response.context.get('username'), username)
        self.assertEqual(response.context.get('post').id, post.id)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_image_in_context(self):
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
        post = Post.objects.create(
                author=PostPagesTests.user,
                text='Текст',
                group=PostPagesTests.group,
                image=uploaded,
            )
        user = post.author
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-slug'}),
            'profile.html': reverse('profile', kwargs={'username': user}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                latest_post = response.context.get('page')[0]
                self.assertIsNotNone(latest_post.image.url, template)

    def test_image_in_post_view_context(self):
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
        post = Post.objects.create(
            author=PostPagesTests.user,
            text='Текст',
            group=PostPagesTests.group,
            image=uploaded,
        )
        user = post.author
        post_id = post.id
        response = self.authorized_client.get(reverse('post', kwargs={'username': user, 'post_id': post_id}))
        post = response.context.get('post')
        self.assertIsNotNone(post.image.url)

    def test_cache_on_homepage(self):
        new_post_text = 'Text for cached post'
        response = self.authorized_client.get(reverse('index'))
        self.assertNotContains(response, new_post_text)
        Post.objects.create(
            author=self.user,
            text=new_post_text,
            group=PostPagesTests.group,
        )
        response = self.authorized_client.get(reverse('index'))
        self.assertNotContains(response, new_post_text)
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.assertContains(response, new_post_text)
