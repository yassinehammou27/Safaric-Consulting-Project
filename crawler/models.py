from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from auswertung.models import Haendler


# Create your models here.
class UploadedFiles2 (models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    name = models.CharField(max_length=200, null = True, blank = True)
    datei = models.FileField(null=True, blank=True)
    handout = models.BooleanField(default= False)
    uniqueDir = models.CharField(max_length=200, null = True, blank = True)

    class Meta:
        verbose_name_plural = "Uploaded Files 2"
        verbose_name = "Uploaded File 2"

    def __str__(self):
        return self.name

class crawlURL (models.Model):
    haendler = models.ForeignKey(Haendler, on_delete = models.CASCADE, null = True, blank = True)
    url = models.CharField(max_length=400, null= True, blank = True)
    crawlTiefe = models.PositiveIntegerField(default=2, null= True, blank=True)

    class Meta:
        verbose_name_plural = "Crawl URLs"
        verbose_name = "Crawl URL"

    def __str__(self):
        return str(self.haendler) + '  -   ' + self.url
    
