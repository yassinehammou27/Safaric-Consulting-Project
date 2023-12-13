from django.urls import path 
from . import views
from .views import HandzettelListView, ausw_HandzettelListView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [
    path('', views.home, name ='auswertung-home'),
    path('handzettelliste/', permission_required('auswertung.view_handzettelliste', raise_exception=True)(HandzettelListView.as_view()) , name ='auswertung-handzettelliste'),
    path('ausw_handzettelliste/', permission_required('auswertung.view_auswerten', raise_exception=True)(ausw_HandzettelListView.as_view()) , name ='auswertung-ausw_handzettelliste'),
    path('handzettel/<str:pk>', permission_required('auswertung.view_auswerten', raise_exception=True)(views.handzettelAuswertung), name='auswertung-handzettel'),
    path('handzettel/<str:hz>/seite/<str:pn>', permission_required('auswertung.view_auswerten', raise_exception=True)(views.seiteAuswertung), name='auswertung-seite'),
    path('artikel/', permission_required('auswertung.view_auswerten', raise_exception=True)(views.artikelAuswertung), name='auswertung-artikel'),
]
