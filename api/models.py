from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Exercise(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exercise_images/')
    description = models.TextField()
    video = models.FileField(upload_to='exercise_videos/', null=True, blank=True)

    def __str__(self):
        return self.name


