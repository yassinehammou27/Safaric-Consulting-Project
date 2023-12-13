import django_filters 
from auswertung.models import Artikel, Seite

# define the filteroptions for the products which should be exported
class ArtikelFilter(django_filters.FilterSet):
    jahr = django_filters.RangeFilter(field_name='seite__handzettel__jahr', label = 'Jahre von - bis')
    kw = django_filters.RangeFilter(field_name = 'seite__handzettel__kw', label = 'Kalenderwoche von - bis')
    class Meta:
        model = Artikel
        fields = [#'seite__handzettel__haendler__branche',
                #'seite__handzettel__haendler',
                #'seite__handzettel__jahr',
                #'seite__handzettel__kw',
                'seite__handzettel'
                ]      
    def __init__(self, *args, **kwargs):
        super(ArtikelFilter, self).__init__(*args, **kwargs)
        self.filters['seite__handzettel'].label="Handzettel"
        #self.filters['seite__handzettel__haendler'].label="Händler"
        #self.filters['seite__handzettel__haendler__branche'].label="Branche"
        
# define the filteroptions for the pages which should be exported
class SeitenFilter(django_filters.FilterSet):
    jahr = django_filters.RangeFilter(field_name='handzettel__jahr', label = 'Jahre von - bis')
    kw = django_filters.RangeFilter(field_name = 'handzettel__kw', label = 'Kalenderwoche von - bis')
    class Meta:
        model = Seite
        fields = [#'handzettel__haendler__branche',
                #'handzettel__haendler',
                #'seite__handzettel__jahr',
                #'seite__handzettel__kw',
                'handzettel'
                ]      
    def __init__(self, *args, **kwargs):
        super(SeitenFilter, self).__init__(*args, **kwargs)
        self.filters['handzettel'].label="Handzettel"
        #self.filters['handzettel__haendler'].label="Händler"
        #self.filters['handzettel__haendler__branche'].label="Branche"
        