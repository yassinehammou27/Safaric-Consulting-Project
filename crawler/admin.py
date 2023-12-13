from django.contrib import admin
from .models import (UploadedFiles2,
                    crawlURL)

from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(UploadedFiles2)
admin.site.register(crawlURL)