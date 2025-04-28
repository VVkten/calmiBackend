import uuid
from django.apps import AppConfig
from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


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

    GENDER_CHOICES = [
        ('M', 'Чоловіча'),
        ('F', 'Жіноча'),
        ('O', 'Інша'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата народження")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Стать")

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    """ Модель категорії як для статей так і для вправ чи тестів """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Exercise(models.Model):
    """ Вправа """
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='exercise')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True)
    breathing_pattern = models.JSONField(null=True, blank=True)
    emoji = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='exercise_images/', default='exercise_images/default.png')

    def __str__(self):
        return self.name


class Article(models.Model):
    """ Стаття """

    GENDER_CHOICES_ART = [
        ('M', 'Чоловіча'),
        ('F', 'Жіноча'),
        ('A', 'Всі'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sex_rec = models.CharField(max_length=1, choices=GENDER_CHOICES_ART, blank=True, null=True, verbose_name="Рекомендовано для певної статі")

    def __str__(self):
        return self.title


class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='test_images/', default=None)
    tags = models.CharField(max_length=255, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
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


class ResultTestUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results_user')
    result_data = models.CharField(max_length=255, blank=True)
    passed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Result {self.user.name} for {self.test.title} at {self.passed_at.strftime('%Y-%m-%d %H:%M')}"


class Quotes(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"Цитата {self.text}"