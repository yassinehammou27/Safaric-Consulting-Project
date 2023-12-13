from django import forms
from django.forms import ModelForm
from auswertung.models import Handzettel, Haendler
from django.forms import ClearableFileInput

class crawlHandzettelForm(ModelForm):
    class Meta:
        model = Handzettel
        fields = ['haendler', 'kw', 'jahr']
        labels = {
            'kw' : 'Kalenderwoche',
        }