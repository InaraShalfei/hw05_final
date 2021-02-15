from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Bash',
                                         slug='bash', description='bash group')
        cls.user = User.objects.create_user('Mike', 'admin@test.com', 'pass')
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст, превышающий пятнадцать символов на любом языке.',
            group=cls.group,
        )

        cls.post = Post.objects.get(author=cls.user)

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор поста',
            'group': 'Группа поста',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Написать текст поста',
            'author': 'Указать автора поста',
            'group': 'Выбрать группу поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_text_max_length_not_exceed(self):
        post = PostModelTest.post
        max_length_text = post.text[:15]
        self.assertEqual(max_length_text, str(post))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Vsem privet',
            slug='vsem-privet',
            description='Gruppa chtoby govorit privet',
        )
        cls.group = Group.objects.get(slug='vsem-privet')

    def test_verbose_name(self):
        group = PostModelTest.group
        field_verboses = {
            'description': 'Описание группы',
            'slug': 'Адрес группы',
            'title': 'Название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = PostModelTest.group
        field_help_texts = {
            'description': 'Дать описание группе',
            'slug': 'Указать адрес для страницы',
            'title': 'Дать название группе',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(group._meta.get_field(value).help_text, expected)

    def group_str_method(self):
        group = PostModelTest.group
        expected_name = "Bash"
        self.assertEqual(expected_name, str(group))
