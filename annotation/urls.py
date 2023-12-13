from django.urls import path 
from . import views
from django.contrib.auth.decorators import permission_required

# path was commented out because this approach for selecting boxes in a page is not used anymore
# if you want to use it again you have to uncomment it and comment out the jcrop url

#urlpatterns = [
#    path('<str:id>', permission_required('auswertung.view_auswerten', raise_exception=True)(views.annotation), name='annotation-annotation')
#]
