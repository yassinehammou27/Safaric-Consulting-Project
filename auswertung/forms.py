from django import forms
from django.forms import ModelForm
from .models import Handzettel, Seite, Artikel, CustomUser, ArtikelDictionary
from django.forms import ClearableFileInput

class HandzettelForm(ModelForm):
    class Meta:
        model = Handzettel
        fields = ['haendler', 'kw', 'jahr', 'seitenanzahl', 'bemerkung']
        labels = {
            'kw' : 'Kalenderwoche',
        }
    def __init__(self, *args, **kwargs):
        super(HandzettelForm, self).__init__(*args, **kwargs)
        self.fields['seitenanzahl'].widget.attrs['readonly'] = True

class SeitenForm(ModelForm):
    class Meta:
        model = Seite
        fields = ['seitentyp','oberkategorie', 'hauptkategorie', 'artikelanzahl', 'artikelanzahlnichthk','themenwelt', 'bemerkung']
        labels = {
            'seitentyp' : 'Seitentyp',
            'hauptkategorie': 'Hauptkategorie',
            'artikelanzahl': 'Artikelanzahl',
            'artikelanzahlnichthk': 'Anzahl Artikel nicht in Hauptkategorie'
        }

class SeitenForm2(ModelForm):
    # this form is used, when the page evaluation was already executed at least once
    # so the article instances of this page have been created and only an admin can change it
    class Meta:
        model = Seite
        fields = ['seitentyp','oberkategorie', 'hauptkategorie', 'artikelanzahl', 'artikelanzahlnichthk','themenwelt', 'bemerkung']
        labels = {
            'seitentyp' : 'Seitentyp',
            'hauptkategorie': 'Hauptkategorie',
            'artikelanzahl': 'Artikelanzahl',
            'artikelanzahlnichthk': 'Anzahl Artikel nicht in Hauptkategorie'
        }
    def __init__(self, *args, **kwargs):
        super(SeitenForm2, self).__init__(*args, **kwargs)
        self.fields['artikelanzahl'].widget.attrs['readonly'] = True


class ArtikelForm(ModelForm):
    class Meta:
        model = Artikel
        fields = ['ocr_output',  'name', 'preis','oberkategorie', 'kategorie', 'seitenbereich','auslobungnormalpreis', 'loyalty', 'artikelart','coupon', 'heroartikel', 'bemerkung','fertig']
        labels={
            'auslobungnormalpreis': 'Auslobung Normalpreis',
            'ocr_output': 'OCR-Output',
            
        }
        widgets = {
            'ocr_output': forms.Textarea(attrs={'rows':5, 'cols':1}),
        }
        
class dictForm(ModelForm):
    class Meta:
        model = ArtikelDictionary
        fields = ['content']
        labels={
            'content': 'Wörterbucheintrag',
        }
class dictFormGrey(ModelForm):
    class Meta:
        model = ArtikelDictionary
        fields = ['content']
        labels={
            'content': 'Wörterbucheintrag',
        }
    # def __init__(self, *args, **kwargs):
    #     super(dictFormGrey, self).__init__(*args, **kwargs)
    #     self.fields['content'].widget.attrs['readonly'] = True    

class HandzettelForm_Upload(ModelForm):
    class Meta:
        model = Handzettel
        fields = ['handzetteldatei']     
        widgets = {
            'handzetteldatei': ClearableFileInput(attrs={'multiple': True}),
            }
      