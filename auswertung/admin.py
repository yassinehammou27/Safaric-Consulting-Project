from django.contrib import admin
from .models import (Haendler,
                    Unternehmensgruppe, 
                    Branche, 
                    Referenzartikel, 
                    Handzettel, 
                    Seite, 
                    Artikel, 
                    Aktionstyp,
                    Oberkategorie, 
                    Kategorie,
                    KategorieArtikel, 
                    Loyalty,
                    Artikelart,
                    CustomUser,
                    Auslobungnormalpreis,
                    Seitentyp,
                    ArtikelDictionary)

from django.contrib.auth.admin import UserAdmin

# used for permission managing in the admin panel
from django.contrib.auth.models import Permission



# name of admin site
admin.site.site_header = "Administration der Handzettelauswertungsanwendung"
# to change the order of the fields in the admin panel

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (None, 
        {'fields': ('haendler', 'branchen', 'unternehmensgruppe'),
        },
        ),
    )

# Register your models here.

admin.site.register(Haendler)
admin.site.register(Unternehmensgruppe)
admin.site.register(Branche)
admin.site.register(Referenzartikel)
admin.site.register(Handzettel)
admin.site.register(Seite)
admin.site.register(Artikel)
admin.site.register(Aktionstyp)
admin.site.register(Oberkategorie)
admin.site.register(Kategorie)
admin.site.register(KategorieArtikel)
admin.site.register(Loyalty)
admin.site.register(Artikelart)
admin.site.register(Auslobungnormalpreis)
admin.site.register(Seitentyp)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Permission)
admin.site.register(ArtikelDictionary)




