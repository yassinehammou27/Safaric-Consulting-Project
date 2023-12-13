from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [
    path('', permission_required('auswertung.view_import', raise_exception=True)(views.crawl_handout), name = 'crawlerstart'),
    path('crawlerclassify/', permission_required('auswertung.view_import', raise_exception=True)(views.crawl_classify), name = 'crawlerclassify'),
    path('crawlerrename/', permission_required('auswertung.view_import', raise_exception=True)(views.crawl_rename), name = 'crawlerrename'),
    path('crawlerdone/', permission_required('auswertung.view_import', raise_exception=True)(views.crawl_done), name ='crawlerdone'),
]
