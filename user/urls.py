from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [
            path('neues_passwort/', login_required(views.change_password), name='change_password')
]