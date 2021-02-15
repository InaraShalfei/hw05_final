from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.tech_url = reverse('about:tech')
        self.about_url = reverse('about:author')

    def test_about_author_page_accessible_for_user(self):
        response = self.guest_client.get(self.about_url)
        self.assertEqual(response.status_code, 200)

    def test_about_author_page_uses_correct_template(self):
        response = self.guest_client.get(self.about_url)
        self.assertTemplateUsed(response, 'about/about.html')

    def test_about_tech_page_accessible_for_user(self):

        response = self.guest_client.get(self.tech_url)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page_uses_correct_template(self):
        response = self.guest_client.get(self.tech_url)
        self.assertTemplateUsed(response, 'about/about.html')
