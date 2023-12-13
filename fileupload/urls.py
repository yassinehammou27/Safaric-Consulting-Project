from django.urls import path 
from . import views
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [  
    path('', permission_required('auswertung.view_import', raise_exception=True)(views.upload_handout), name = 'uploadstart'),  
]
