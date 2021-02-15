from django.http import HttpResponse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class HomepageURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage_exists_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        response = self.guest_client.get('/')
        self.assertTemplateUsed(response, 'index.html')


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Vsem privet',
            slug='test-slug',
            description='Gruppa chtoby govorit privet',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user('Mike', 'admin@test.com', 'pass'),
            text='Тестовый текст, превышающий пятнадцать символов на любом языке.',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Slava')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'group.html': '/group/test-slug/',
            'new.html': '/new/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_slug_exists_at_desired_location(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new_exists_at_desired_location(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_redirect_anonymous_on_auth_login(self):
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_profile_at_desired_location(self):
        username = self.user.username
        response = self.authorized_client.get(f'/{username}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_404_for_missed_username(self):
        response = self.authorized_client.get('/Ja/')
        self.assertEqual(response.status_code, 404)

    def test_post_view_at_desired_location(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        response = self.authorized_client.get(f'/{username}/{post_id}/')
        self.assertEqual(response.status_code, 200)

    def test_post_view_404_for_wrong_author(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        response = self.authorized_client.get(f'/{username}wrong/{post_id}/')
        self.assertEqual(response.status_code, 404)

    def test_post_edit_redirect_for_anonymous(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        response = self.guest_client.get(f'/{username}/{post_id}/edit/')
        self.assertRedirects(response, f'/{username}/{post_id}/')

    def test_post_edit_redirect_for_authorized_user(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        response = self.authorized_client.get(f'/{username}/{post_id}/edit/')
        self.assertRedirects(response, f'/{username}/{post_id}/')

    def test_post_edit_at_desired_location_for_post_author(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        author_client = Client()
        author_client.force_login(post.author)
        response = author_client.get(f'/{username}/{post_id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template_for_post_edit(self):
        post = PostUrlTests.post
        post_id = post.id
        username = post.author.username
        author_client = Client()
        author_client.force_login(post.author)
        template = 'new.html'
        reverse_name = f'/{username}/{post_id}/edit/'
        response = author_client.get(reverse_name)
        self.assertTemplateUsed(response, template)

    def test_return_404_if_page_not_found(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.authorized_client.get(f'/{username}wrong/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')
