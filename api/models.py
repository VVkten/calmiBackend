from django.db import models
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
    REQUIRED_FIELDS = []  # Не вимагаємо нічого крім email і пароля

    objects = UserManager()  # Призначаємо кастомний менеджер

    def __str__(self):
        return self.email  # Для зручного виводу користувача


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exercise_images/')
    description = models.TextField()
    video = models.FileField(upload_to='exercise_videos/', null=True, blank=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    """Модель тесту"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='test_images/', blank=True, null=True)
    category = models.CharField(max_length=255)
    tags = models.TextField(help_text="Введіть теги через кому")
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Question(models.Model):
    """Модель питання для тесту"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return self.text


class Answer(models.Model):
    """Модель відповіді на питання"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    points = models.IntegerField(default=1)  # Від 1 до 5

    def __str__(self):
        return f"{self.text} ({self.points} балів)"


class TestResult(models.Model):
    """Модель результатів тесту залежно від суми балів"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    result_text = models.TextField()

    def __str__(self):
        return f"{self.test.name}: {self.min_score} - {self.max_score} балів"
