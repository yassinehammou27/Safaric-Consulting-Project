from django.urls import path 
from . import views
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [
    path('<str:id>', permission_required('auswertung.view_auswerten', raise_exception=True)(views.aiKategorisierungView), name ='ai-kategorisierung'),
    path('uebersicht/<str:id>', permission_required('auswertung.view_auswerten', raise_exception=True)(views.uebersicht), name ='kategorisierung-uebersicht'),
]
