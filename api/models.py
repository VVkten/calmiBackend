import uuid

from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Кастомний менеджер для моделі User без username"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Користувач повинен мати email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Створює суперюзера"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомний користувач Django без username, з авторизацією через email"""

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # EmailField замість CharField
    password = models.CharField(max_length=255)
    username = None
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.emai


class Exercise(models.Model):
    """ Вправа """
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exercise_images/')
    description = models.TextField()
    video = models.FileField(upload_to='exercise_videos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    """ Модель категорії як для статей так і для вправ чи тестів """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Article(models.Model):
    """ Стаття """
    title = models.CharField(max_length=255)
    description = models.TextField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, default=uuid.uuid4, editable=False)
    # author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    certificate = models.BooleanField(default=False)
    certificate_type = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tests')

    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    text = models.CharField(max_length=255)
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return f"{self.text} ({self.score} балів)"


class ResultTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    result_data = JSONField()

    def __str__(self):
        return f"Result for {self.test.title}"
