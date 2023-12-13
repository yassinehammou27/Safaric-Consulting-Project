from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required, login_required
    
    
urlpatterns = [ 
    path('ergebnisse/', permission_required('auswertung.view_ergebnisse', raise_exception=True)(views.ergebnisse), name='auswertung-ergebnisse'),
    path('excelExport/', permission_required('auswertung.view_ergebnisse', raise_exception=True)(views.excelExport), name='auswertung-excelexport'),
    path('ergebnisseSeite/', permission_required('auswertung.view_ergebnisse', raise_exception=True)(views.ergebnisseSeite), name = 'auswertung-ergebnisseSeite'),
    path('ergebnisseArtikel/', permission_required('auswertung.view_ergebnisse', raise_exception=True)(views.ergebnisseArtikel), name='auswertung-ergebnisseArtikel'),
    path('excelExportSeite/', permission_required('auswertung.view_ergebnisse', raise_exception=True)(views.excelExportSeite), name = 'auswertung-excelexportSeite')
]