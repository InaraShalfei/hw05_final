from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название группы",
                             max_length=200, help_text="Дать название группе")
    slug = models.SlugField("Адрес группы",
                            unique=True, help_text="Указать адрес для страницы")
    description = models.TextField("Описание группы",
                                   help_text="Дать описание группе")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста",
                            help_text="Написать текст поста")
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор поста",
                               help_text="Указать автора поста")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="posts",
                              blank=True,
                              verbose_name="Группа поста",
                              null=True, help_text="Выбрать группу поста")
    image = models.ImageField(upload_to="posts/", verbose_name="Изображение", blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments",
                             verbose_name="Ссылка на пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор комментария")
    text = models.TextField("Текст комментария",
                            help_text="Написать текст комментария")
    created = models.DateTimeField("Дата комментария",
                                   auto_now_add=True)

