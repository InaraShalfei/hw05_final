from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, Follow

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
        self.assertRedirects(response, "%s?next=%s" %
                             (resolve_url(settings.LOGIN_URL), reverse('new_post')))

    def test_profile_at_desired_location(self):
        username = self.user.username
        response = self.authorized_client.get(reverse('profile',
                                                      kwargs={'username': username}))
        self.assertEqual(response.status_code, 200)

    def test_profile_404_for_missed_username(self):
        response = self.authorized_client.get('/Ja/')
        self.assertEqual(response.status_code, 404)

    def test_post_view_at_desired_location(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.authorized_client.get(reverse('post',
                                                      kwargs={'username': username,
                                                              'post_id': post.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_view_404_for_wrong_author(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.authorized_client.get(reverse('post',
                                                      kwargs={'username': f'{username}wrong',
                                                              'post_id': post.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_edit_redirect_for_anonymous(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.guest_client.get(reverse('post_edit',
                                                 kwargs={'username': username,
                                                         'post_id': post.id}))
        self.assertRedirects(response, reverse('post',
                                               kwargs={'username': username,
                                                       'post_id': post.id}))

    def test_post_edit_redirect_for_authorized_user(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.authorized_client.get(reverse('post_edit',
                                                      kwargs={'username': username,
                                                              'post_id': post.id}))
        self.assertRedirects(response, reverse('post',
                                               kwargs={'username': username,
                                                       'post_id': post.id}))

    def test_post_edit_at_desired_location_for_post_author(self):
        post = PostUrlTests.post
        username = post.author.username
        author_client = Client()
        author_client.force_login(post.author)
        response = author_client.get(reverse('post_edit',
                                             kwargs={'username': username,
                                                     'post_id': post.id}))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template_for_post_edit(self):
        post = PostUrlTests.post
        username = post.author.username
        author_client = Client()
        author_client.force_login(post.author)
        template = 'new.html'
        reverse_name = reverse('post_edit', kwargs={'username': username,
                                                    'post_id': post.id})
        response = author_client.get(reverse_name)
        self.assertTemplateUsed(response, template)

    def test_return_404_if_page_not_found(self):
        post = PostUrlTests.post
        username = post.author.username
        response = self.authorized_client.get(reverse('profile',
                                                      kwargs={'username': f'{username}wrong'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')

    def test_add_comment_redirect_for_anonymous(self):
        post = PostUrlTests.post
        url = reverse('add_comment', kwargs={'username': post.author.username,
                                             "post_id": post.id})
        response = self.guest_client.get(url)
        self.assertRedirects(response, "%s?next=%s" %
                             (resolve_url(settings.LOGIN_URL), url))

    def test_follow_redirect_for_anonymous(self):
        username = PostUrlTests.post.author.username
        url = reverse('profile_follow', kwargs={'username': username})
        response = self.guest_client.get(url)
        self.assertRedirects(response, "%s?next=%s" %
                             (resolve_url(settings.LOGIN_URL), url))

    def test_unfollow_redirect_for_anonymous(self):
        username = PostUrlTests.post.author.username
        url = reverse('profile_unfollow', kwargs={'username': username})
        response = self.guest_client.get(url)
        self.assertRedirects(response, "%s?next=%s" %
                             (resolve_url(settings.LOGIN_URL), url))

    def test_follow_redirect_for_authorized_client(self):
        username = PostUrlTests.post.author.username
        url = reverse('profile_follow', kwargs={'username': username})
        response = self.authorized_client.get(url)
        self.assertRedirects(response, reverse('profile',
                                               kwargs={'username': username}))
        self.assertEqual(response.status_code, 302)

    def test_unfollow_redirect_for_authorized_client(self):
        Follow.objects.create(author=PostUrlTests.post.author, user=self.user)
        username = PostUrlTests.post.author.username
        url = reverse('profile_unfollow', kwargs={'username': username})
        response = self.authorized_client.get(url)
        self.assertRedirects(response, reverse('profile',
                                               kwargs={'username': username}))
        self.assertEqual(response.status_code, 302)
