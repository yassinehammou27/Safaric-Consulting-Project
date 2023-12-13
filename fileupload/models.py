from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UploadedFiles (models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    name = models.CharField(max_length=200, null = True, blank = True)
    def __str__(self):
        return self.name