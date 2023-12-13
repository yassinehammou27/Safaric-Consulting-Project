from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_delete
import os
from django import forms


# Create your models here.
class Branche(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "[2.3] Branchen"
    def __str__(self):
        return self.name
        
class Unternehmensgruppe(models.Model):
    name = models.CharField(max_length=100)
    branche = models.ForeignKey(Branche, on_delete=models.RESTRICT)

    class Meta:
        verbose_name_plural = "[2.2] Unternehmensgruppen"

    def __str__(self):
        return self.name

class Referenzartikel (models.Model):
    name = models.CharField(max_length=100) 

    class Meta:
        verbose_name_plural = "[4.4] Referenzartikel"

    def __str__(self):
        return self.name
    
class Haendler (models.Model):
    name = models.CharField(max_length=100)
    land = models.CharField(max_length=100, null=True, blank=True)
    branche = models.ForeignKey(Branche, on_delete = models.RESTRICT)
    unternehmensgruppe = models.ForeignKey(Unternehmensgruppe, on_delete = models.RESTRICT)
    frequenzhandzettel = models.CharField(max_length=100, null=True, blank=True)
    subkategorie = models.CharField(max_length=100, null=True, blank = True)

    class Meta:
        verbose_name_plural = "[2.1] Händler"

    def __str__(self):
        return self.name

class Handzettel (models.Model):
    haendler = models.ForeignKey(Haendler, on_delete = models.CASCADE, null = True, blank = True)
    jahr = models.PositiveIntegerField(validators=[MinValueValidator(1950), MaxValueValidator(2050)], null = True, blank=True)
    seitenanzahl = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null= True, blank = True)
    status = models.PositiveIntegerField(default = 0)
    SeitenAusgewertet = models.BooleanField(default=False)
    artikelAnzahl = models.PositiveIntegerField(default = 0)
    fertigeArtikel = models.PositiveIntegerField(default = 0)
    # letzte Seite contains the last page that has been evaluated, so if you want to continue the evaluation you will start with this page again
    letzteSeite = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null= True, blank = True, default = 1)
    kw = models.PositiveIntegerField(default = 0, validators=[MinValueValidator(0), MaxValueValidator(53)], null=True, blank = True)
    bemerkung = models.CharField(max_length = 999, null = True, blank = True)
    # fileupload
    handzetteldatei = models.FileField(null=True, blank=True)
    

    class Meta:
        verbose_name_plural = "[1.1] Handzettel"

    def __str__(self):
        if str(self.handzetteldatei) == "":
            return str(">kein PDF hinterlegt")
        else:     
            return str(self.handzetteldatei)


class Aktionstyp (models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "[4.1] Aktionstypen"
    
    def __str__(self):
        return self.name
        
class Kategorie (models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="aktiv")

    class Meta:
        verbose_name = "Kategorie Seite"
        verbose_name_plural = "[3.1] Seitenkategorien "

    def __str__(self):
        return self.name

class Oberkategorie (models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="aktiv")

    class Meta:
        verbose_name = "Oberkategorie"
        verbose_name_plural = "[3.3] Oberkategorien "

    def __str__(self):
        return self.name

class KategorieArtikel (models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="aktiv")

    class Meta:
        verbose_name = "Kategorie Artikel"
        verbose_name_plural = "[4.6] Artikelkategorien "

    def __str__(self):
        return self.name



class Seitentyp(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "[3.2] Seitentypen"

    def __str__(self):
        return self.name

class Seite (models.Model):
    handzettel = models.ForeignKey(Handzettel, on_delete = models.CASCADE)
    seitenzahl = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True, blank=True)
    seitentyp = models.ForeignKey(Seitentyp,on_delete= models.RESTRICT, null=True, blank=True)
    themenwelt = models.CharField(max_length=100, null = False, blank = False, default = "keine Themenwelt" )
    oberkategorie = models.ForeignKey(Oberkategorie, on_delete = models.RESTRICT,  null=True, blank=True)
    hauptkategorie = models.ForeignKey(Kategorie, on_delete = models.RESTRICT,  null=True, blank=True)
    artikelanzahl = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)], default = 0)
    artikelanzahlnichthk = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)],  null=True, blank=True)
    bild = models.ImageField(default=None, null=True, blank = True)
    status = models.PositiveIntegerField(default = 0)
    kategorisiert =  models.BooleanField(default=False)
    artikelerstellt = models.BooleanField(default=False)
    bemerkung = models.CharField(max_length = 999, null = True, blank = True)

    class Meta:
        verbose_name_plural = "[1.2] Seiten"

    def __str__(self):
        return "{handzettel}, {seitenzahl}".format(handzettel=self.handzettel, seitenzahl=self.seitenzahl)



class Loyalty(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "[4.2] Loyalty"

    def __str__(self):
        return self.name

class Artikelart(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "[4.5] Artikelarten"

    def __str__(self):
        return self.name

class  Auslobungnormalpreis(models.Model):
    option = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "[4.3] Auslobung Normalpreise"
        verbose_name = "Auslobung Normalpreis"

    def __str__(self):
        return self.option


class CustomUser(AbstractUser):
    haendler = models.ManyToManyField(Haendler, blank=True)
    branchen = models.ManyToManyField(Branche, blank=True)
    unternehmensgruppe = models.ManyToManyField(Unternehmensgruppe, blank=True)

class Artikel (models.Model):
    seite = models.ForeignKey(Seite, on_delete = models.CASCADE)
    artikelnummer = models.PositiveIntegerField(default = 0)
    referenzartikel = models.ForeignKey(Referenzartikel, on_delete = models.RESTRICT, null = True, blank = True)
    name = models.CharField(max_length=200, null = True, blank = True)
    oberkategorie = models.ForeignKey(Oberkategorie, on_delete = models.RESTRICT,  null=True, blank=True)
    kategorie = models.ForeignKey(KategorieArtikel, on_delete = models.RESTRICT, null = True, blank = True)
    aktionsmechanik = models.ForeignKey(Aktionstyp, on_delete = models.RESTRICT, null = True, blank = True)
    preis = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)
    seitenbereich = models.CharField(max_length=200, null = True, blank = True)
    auslobungnormalpreis = models.ForeignKey(Auslobungnormalpreis, on_delete = models.RESTRICT, null = True, blank=True)
    coupon = models.BooleanField(default=False)
    loyalty = models.ForeignKey(Loyalty, on_delete = models.RESTRICT, null = True, blank=True)
    artikelart = models.ForeignKey(Artikelart, on_delete = models.RESTRICT, null=True, blank=True)
    heroartikel = models.BooleanField(default=False)
    bemerkung = models.CharField(max_length = 999,null = True, blank = True)
    startpunkt_x = models.PositiveIntegerField(default = 0, null= True, blank= True)
    startpunkt_y = models.PositiveIntegerField(default = 0, null=True, blank= True)
    endpunkt_x = models.PositiveIntegerField(default = 0, null=True, blank=True)
    endpunkt_y = models.PositiveIntegerField(default = 0, null=True, blank=True)
    fertig = models.BooleanField(default=False)
    ocr_output = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "[1.3] Artikel"
    
    def __str__(self):
        return "{name}, {seite}, {artikelnummer}".format(name=self.name, seite=self.seite, artikelnummer=self.artikelnummer)


class ArtikelDictionary(models.Model):
    key = models.ForeignKey(KategorieArtikel, on_delete = models.CASCADE,)
    content = models.CharField(max_length=100, default = None, null=True, blank=True)
    class Meta:
        verbose_name = "Artikel-Dictionary"
        verbose_name_plural = "[4.7] Artikel-Dictionary"

    def __str__(self):
        return str(self.key) +' -  '+ str(self.content)


class customPermissions(models.Model):
    class Meta:
        
        default_permissions = ()
        permissions =[
            ('view_handzettelliste','Zugang zur Handzettelliste'),
            ('view_ergebnisse', 'Zugang zu Ergebnissen'),
            ('view_auswerten', 'Zugang zum Auswertungsbereich'),
            ('view_import', 'Zugang zur Importseite')
        ]

@receiver(models.signals.post_delete, sender=Handzettel)
def auto_delete_handzettel_on_delete(sender, instance, **kwargs):
    if instance.handzetteldatei:
        if os.path.isfile(instance.handzetteldatei.path):
          
            # can be deleted if approach is working
            #
            # qs = Seite.objects.filter(handzettel__haendler__name=instance.haendler, handzettel__kw=instance.kw, handzettel__jahr=instance.jahr)
            # print(qs)
            # qs_list = list(qs.values())
            # print(qs_list)
            # for handzettel in qs_list:
            #     os.remove(Seite.bild.path)
            
            os.remove(instance.handzetteldatei.path)
         

@receiver(models.signals.post_delete, sender=Seite)
def auto_delete_seite_on_delete(sender, instance, **kwargs):
    if instance.bild:
        if os.path.isfile(instance.bild.path):
            os.remove(instance.bild.path)
       

