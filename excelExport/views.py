from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from auswertung.models import Handzettel, Seite, Referenzartikel, Kategorie, Aktionstyp, Artikel, Auslobungnormalpreis
from auswertung.models import Haendler, Branche, CustomUser, Unternehmensgruppe, Loyalty, Artikelart, Seitentyp, KategorieArtikel, Oberkategorie
from django.db.models import Avg, Q, F
from .filters import ArtikelFilter, SeitenFilter
import xlwt
import datetime 


@login_required
def ergebnisse(request):
    return render(request, 'auswertung/ergebnisse.html', {'title': 'Ergebnisse'})

# global variable artikel qs
qs = None
# global variable which contains product categories as a dictionary
kat_dict = None

# calculate the number of Handzettel which going to be exported
def anzahlHandzettelBerechnung(var, var2, var3, var4, anzahlH):
    # var equals the user selected 'Branche'
    # var2 equals the user selected 'Unternehmensgruppe'
    # var3 equals the user selected 'Haendler'
    # var4 equals the user selected 'Handzettel'
    anzahlHandzettel = anzahlH 
    if var4 != '': # if a specific 'Handzettel' got selected
        anzahlHandzettel = 1
    elif var3 != '':
        haendler = Haendler.objects.get(name = var3)  
        # status = 1 means that the 'Handzettel' already got evaluated 
        anzahlHandzettel = len(haendler.handzettel_set.filter(Q(status = 1) | Q(SeitenAusgewertet = True)))
    elif var2 != '':
        unternehmensgruppe = Unternehmensgruppe.objects.get(name = var2)
        haendlerset = unternehmensgruppe.haendler_set.all()
        anzahlHandzettel = 0
        for haendler in haendlerset:
            anzahlHandzettel += len(haendler.handzettel_set.filter(Q(status = 1) | Q(SeitenAusgewertet = True)))
    elif var != '':
        branche = Branche.objects.get(name = var)
        haendler = branche.haendler_set.all()
        anzahlHandzettel = 0
        for haendler in haendler:
            anzahlHandzettel += len(haendler.handzettel_set.filter(Q(status = 1) | Q(SeitenAusgewertet = True)))
    return anzahlHandzettel

@login_required
def ergebnisseArtikel(request):
    # get the user who wants to export
    username = request.user
    us = CustomUser.objects.get(username = username)
    # get the selected filter options
    unternehmensgruppeFilter = request.GET.get('unternehmensgruppe')
    brancheFilter = request.GET.get('branche')
    haendlerFilter = request.GET.get('haendler')

    unternehmensgruppeListe = []
    haendlerListe = [] 
    branchenListe = []
    isAdminOrStaff = request.user.is_staff or request.user.is_superuser

    # check if user has an admin or staff status
    if isAdminOrStaff:
        # if user has admin or staff status he has access to all 'Branchen', 'Unternehmensgruppen' and 'Haendler'
        branchen = Branche.objects.all()
        unternehmensgruppen = Unternehmensgruppe.objects.all()
        haendler = Haendler.objects.all()
    else:
        # if user does not have admin or staff stauts, he has only access to the 'Branchen', 'Unternehmensgruppen' 
        # and 'Haendler' assigned to him 
        branchen = us.branchen.all() 
        ugruppe = us.unternehmensgruppe.all()
        haendler = us.haendler.all()
    
    # generate a list of all 'Branchen' the user has access to
    for b in branchen:
        branchenListe.append(b.name)

   # generate a list of all 'Unternehmensgruppen' the user has access to
    if not isAdminOrStaff:
        unternehmensgruppen = ugruppe
        # if the user has no 'Unternehmensgruppe' assigned to him 
        # he has only access to the 'Unternehmensgruppen' which are part of the 'Branchen'
        # the user is allowed to access
        if not ugruppe.exists():
            unternehmensgruppen = Unternehmensgruppe.objects.filter(branche__name__in = branchenListe)

    for u in unternehmensgruppen:
        unternehmensgruppeListe.append(u.name)
    
    # generate a list of all 'Haendler' the user has access to
    if not isAdminOrStaff:
        if not haendler.exists():
            if not ugruppe.exists():
                haendler = Haendler.objects.filter(branche__name__in = branchenListe)
            else:
                haendler = Haendler.objects.filter(unternehmensgruppe__name__in = unternehmensgruppeListe)

    for h in haendler: 
        haendlerListe.append(h.name)
     
    # get all products which are assigned to a 'Handezettel' which got evaluated
    artikel = Artikel.objects.filter(Q(seite__handzettel__artikelAnzahl = F('seite__handzettel__fertigeArtikel')) & Q(seite__handzettel__status = 1))
    # get the products which are assigned to a 'Branche' which is contained in the branchenListe
    artikel = artikel.filter(seite__handzettel__haendler__branche__name__in = branchenListe)
    # get the products which are assigned to a 'Unternehmensgruppe' contained in the unternehmensgruppenliste
    artikel = artikel.filter(seite__handzettel__haendler__unternehmensgruppe__name__in = unternehmensgruppeListe)
    # get the products which are assigned to a 'Haendler' contained in the haendlerliste
    artikel = artikel.filter(seite__handzettel__haendler__name__in = haendlerListe)
    
    # filter the remaining products through the filteroptions defined in the ArtikelFilter
    myfilter = ArtikelFilter(request.GET, queryset=artikel)
    global qs
    # contains a queryset of the filter products
    qs = myfilter.qs

    # calculate the number of 'Handzettel' which the user has access to 
    # based on the 'Branchen', 'Haendler', 'Unternehmensgruppe' he has access to
    handzettel = Handzettel.objects.filter(Q(status = 1) & Q(artikelAnzahl = F('fertigeArtikel')))
    handzettel = handzettel.filter(haendler__branche__name__in = branchenListe)
    handzettel = handzettel.filter(haendler__name__in = haendlerListe)
    handzettel = handzettel.filter(haendler__unternehmensgruppe__name__in = unternehmensgruppeListe)
    anzahlHandzettel = len(handzettel)
    

    #filter the remaining products through the user-selected 'Branche', 'Unternehmensgruppe' and 'Haendler'
    if is_valid_queryparam(brancheFilter) and brancheFilter != "":
        qs = qs.filter(seite__handzettel__haendler__branche__name = brancheFilter)
    if is_valid_queryparam(unternehmensgruppeFilter) and unternehmensgruppeFilter != "":
        qs = qs.filter(seite__handzettel__haendler__unternehmensgruppe__name = unternehmensgruppeFilter)
    if is_valid_queryparam(haendlerFilter) and haendlerFilter != "":
        qs = qs.filter(seite__handzettel__haendler__name = haendlerFilter)
    
    #calculate number of 'Handzettel' which the filterd products are placed in
    if not request.GET.get('seite__handzettel') == None:
        anzahlHandzettel = anzahlHandzettelBerechnung(brancheFilter,
                                                unternehmensgruppeFilter,
                                                haendlerFilter,
                                                request.GET.get('seite__handzettel'),
                                                anzahlHandzettel)
    else:
        anzahlHandzettel = anzahlHandzettelBerechnung('','','', '', anzahlHandzettel)


    # number of products
    anzahlArtikel = len(qs)
    # average price
    dic = qs.aggregate(average_price = Avg('preis'))
    durchschnittspreis = 0
    if dic['average_price']:
        durchschnittspreis = round(dic['average_price'], 2)

    # number of products foreach category 
    if anzahlHandzettel > 0:
        k_dict = { k.name :  (len(qs.filter(kategorie = k)), len(qs.filter(kategorie = k))/anzahlHandzettel)   for k in KategorieArtikel.objects.all()}
    else:
         k_dict = { k.name :  (len(qs.filter(kategorie = k)), len(qs.filter(kategorie = k)))   for k in KategorieArtikel.objects.all()}
    
    global kat_dict
    # dictonary which contains the different product-categories with the different 
    kat_dict = k_dict
    context = {'myFilter': myfilter,
            'title': 'Ergebnisse',
            'artikel': qs,
            'durchschnittspreis': durchschnittspreis,
            'anzahlArtikel': anzahlArtikel,
            'Kategorie': k_dict,
            'anzahlHandzettel': anzahlHandzettel,
            'branchen': branchen,
            'haendler': haendler,
            'unternehmensgruppen': unternehmensgruppen,
            'unternehmensgruppeFilter': unternehmensgruppeFilter,
            'brancheFilter': brancheFilter,
            'haendlerFilter': haendlerFilter,
            'anzahlHandzettel': anzahlHandzettel}
    return render(request, 'auswertung/artikel_ergebnisse.html', context)


def excelExport(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="artikelliste.xls"'
    # create a excelfile (workbook)
    wb = xlwt.Workbook(encoding='utf-8')
    # create a excelsheet for the productlist
    ws = wb.add_sheet('Artikelliste')
    row_num = 0
    # define the Style of the excelsheet
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    # define the columns of the excelsheet
    columns = ['Haendler',
            'Jahr',
            'Kalenderwoche',
            'Seitenzahl',
            'Seite ID',
            'Referenzartikel',
            'Name',
            'Oberkategorie',
            'Kategorie',
            'Preis',
            'Seitenbereich',
            'Auslobungnormalpreis',
            'Coupon',
            'Loyalty',
            'Artikelart',
            'Heroartikel',
            'Bemerkung']
    
    # write the column headings in the excelsheet
    for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()
    # define which values of the product queryset we want to export
    rows = qs.values_list('seite',
                    'referenzartikel',
                    'name',
                    'kategorie',
                    'oberkategorie',
                    'preis',
                    'seitenbereich',
                    'auslobungnormalpreis',
                    'coupon',
                    'loyalty',
                    'artikelart',
                    'heroartikel',
                    'bemerkung')
    for row in rows:
        row = list(row)
        seite = Seite.objects.filter(pk = row[0]).first()
        handzettel = seite.handzettel
        # add values pagenumber, kw, year and retailer name
        # to the information we want to export
        row.insert(0, seite.seitenzahl)
        row.insert(0,handzettel.kw)
        row.insert(0, handzettel.jahr)
        row.insert(0, handzettel.haendler.name)

        # the values like 'referenzkategorie' which are foreign keys
        # only contain the  primary key values
        # we want to get the name of the objects and replace the ids
        row[5] = Referenzartikel.objects.filter(pk = row[5]).first()
        row[7] = Oberkategorie.objects.filter(pk = row[7]).first()
        row[8] = KategorieArtikel.objects.filter(pk = row[8]).first()
        row[11] = Auslobungnormalpreis.objects.filter(pk = row[11]).first()
        row[13] = Loyalty.objects.filter(pk = row[13]).first()
        row[14] = Artikelart.objects.filter(pk = row[14]).first()
        row_num+=1

        # write the information into the excelsheet
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    
    # add another excelsheet to the excelfile
    katsheet = wb.add_sheet('Kategorieliste')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    # define the values/ headings which should be contained in the excelsheet
    columns = ['Kategorie',
            'Anzahl Artikel',
            'Durchschnittliche Anzahl je Handzettel']
    # write the headings into the excelsheet
    for col_num in range(len(columns)):
        katsheet.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    spalte = 0
    # write the information (product categorie)
    # into excelsheet
    for key, value in kat_dict.items():
        row_num += 1
        katsheet.write(row_num, spalte , key , font_style)
    
    row_num = 0
    rows = kat_dict.values()

    # write the information (number of products)
    # into excelsheet
    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            katsheet.write(row_num, col_num+1, str(row[col_num]), font_style)

    # safe the excel sheet
    wb.save(response)
    return response

# queryset containing pages
qs_seite = None

# calculate number of products
def berechnungArtikelAnzahl():
    artikelAnzahl = 0
    for seite in qs_seite:
        artikelAnzahl += seite.artikelanzahl
    return artikelAnzahl

def is_valid_queryparam(param):
    return param != '' and param is not None

@login_required
def ergebnisseSeite(request):
    seitenAnzahl = 0
    anzahlHandzettel = 0
    meanSeitenanzahl = 0
    anzahlArtikelproSeite = 0
    username = request.user
    us = CustomUser.objects.get(username = username)
    unternehmensgruppeFilter = request.GET.get('unternehmensgruppe')
    brancheFilter = request.GET.get('branche')
    haendlerFilter = request.GET.get('haendler')
    unternehmensgruppeListe = []
    haendlerListe = [] 
    branchenListe = []
    isAdminOrStaff = request.user.is_staff or request.user.is_superuser
    
    # check if user has staff or admin status to define the filter options
    if isAdminOrStaff:
        branchen = Branche.objects.all()
        unternehmensgruppen = Unternehmensgruppe.objects.all()
        haendler = Haendler.objects.all()
    else:
        branchen = us.branchen.all() 
        ugruppe = us.unternehmensgruppe.all()
        haendler = us.haendler.all()
    
    # generate a list of 'Branchen' the user has access to
    for b in branchen:
        branchenListe.append(b.name)
    
    # generate a list of 'Unternehmensgruppen' the user has access to 
    if not isAdminOrStaff:
        unternehmensgruppen = ugruppe
        if not ugruppe.exists():
            unternehmensgruppen = Unternehmensgruppe.objects.filter(branche__name__in = branchenListe)

    for u in unternehmensgruppen:
        unternehmensgruppeListe.append(u.name)
    
    # generate a list of 'Haendler' the user has access to 
    if not isAdminOrStaff:
        if not haendler.exists():
            if not ugruppe.exists():
                haendler = Haendler.objects.filter(branche__name__in = branchenListe)
            else:
                haendler = Haendler.objects.filter(unternehmensgruppe__name__in = unternehmensgruppeListe)

    for h in haendler: 
        haendlerListe.append(h.name)
    
    # generate a queryset of pages the user has access to and which can be exported later
    seite = Seite.objects.filter((Q(handzettel__status = 1) & Q(handzettel__artikelAnzahl = F('handzettel__fertigeArtikel'))) | Q(handzettel__SeitenAusgewertet = True))
    seite = seite.filter(handzettel__haendler__branche__name__in = branchenListe)
    seite = seite.filter(handzettel__haendler__name__in = haendlerListe)
    seite = seite.filter(handzettel__haendler__unternehmensgruppe__name__in = unternehmensgruppeListe)
    
    # calulate the number of 'Handzettel' the user has access to 
    # only handzettel should be available to the user which got evaluated completly 
    # or where the pages got evaluated completly
    handzettel = Handzettel.objects.filter((Q(status = 1) & Q(artikelAnzahl = F('fertigeArtikel'))) | Q(SeitenAusgewertet = True))
    handzettel = handzettel.filter(haendler__branche__name__in = branchenListe)
    handzettel = handzettel.filter(haendler__name__in = haendlerListe)
    handzettel = handzettel.filter(haendler__unternehmensgruppe__name__in = unternehmensgruppeListe)
    anzahlHandzettel = len(handzettel)

    # filter the pages through the filteroptions defined in the 'SeitenFilter'
    myfilter = SeitenFilter(request.GET, queryset=seite)
    global qs_seite 
    qs_seite = myfilter.qs
    
    # filter the remaining pages through the user-selected 'Branche', 'Unternehmensgruppe' and 'Haendler'
    if is_valid_queryparam(brancheFilter) and brancheFilter != "":
        qs_seite = qs_seite.filter(handzettel__haendler__branche__name = brancheFilter)
    if is_valid_queryparam(unternehmensgruppeFilter) and unternehmensgruppeFilter != "":
        qs_seite = qs_seite.filter(handzettel__haendler__unternehmensgruppe__name = unternehmensgruppeFilter)
    if is_valid_queryparam(haendlerFilter) and haendlerFilter != "":
        qs_seite = qs_seite.filter(handzettel__haendler__name = haendlerFilter)

    
    #number of pages
    seitenAnzahl = len(qs_seite)
    
    
    # calculate number of 'Handzettel' which the filterd pages are placed in
    if not request.GET.get('handzettel') == None:
        anzahlHandzettel = anzahlHandzettelBerechnung(brancheFilter,
                                                unternehmensgruppeFilter,
                                                haendlerFilter,
                                                request.GET.get('handzettel'),
                                                anzahlHandzettel)
    else:
        anzahlHandzettel = anzahlHandzettelBerechnung('','','', '', anzahlHandzettel)
    
    #mean number of pages
    if anzahlHandzettel != 0:
        meanSeitenanzahl = round(seitenAnzahl/anzahlHandzettel, 2)
    
    #mean number of product on each page
    anzahlArtikel = berechnungArtikelAnzahl()
    if seitenAnzahl != 0:
        anzahlArtikelproSeite = round(anzahlArtikel/seitenAnzahl, 2)
    
    
    context = {'myFilter': myfilter,
            'title': 'Ergebnisse',
            'seiten': qs_seite,
            'seitenanzahl': seitenAnzahl,
            'durchschnittlicheSeitenanzahl': meanSeitenanzahl,
            'anzahlArtikelproSeite': anzahlArtikelproSeite,
            'haendler': haendler,
            'branchen': branchen,
            'unternehmensgruppen': unternehmensgruppen,
            'unternehmensgruppeFilter': unternehmensgruppeFilter,
            'brancheFilter': brancheFilter,
            'haendlerFilter': haendlerFilter,
            'anzahlHandzettel': anzahlHandzettel}
    return render(request, 'auswertung/seite_ergebnisse.html', context)

def excelExportSeite(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="seitenliste.xls"'
    # create a excelfile (workbook)
    wb = xlwt.Workbook(encoding='utf-8')
    # create a excelsheet for the pagelist
    ws = wb.add_sheet('Seitenliste')
    row_num = 0
    # define the Style of the excelsheet
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    # define the columns of the excelsheet
    columns = ['Haendler',
            'Jahr',
            'Kalenderwoche',
            'Handzettel ID',
            'Seitenzahl',
            'Seitentyp',
            'Hauptkategorie',
            'Artikelanzahl',
            'Anzahl Artikel nicht in HK',
            'Bemerkung'
            ]
    # write the column headings in the excelsheet        
    for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    # define which values of the page queryset we want to export
    rows = qs_seite.values_list('handzettel',
                    'seitenzahl',
                    'seitentyp',
                    'hauptkategorie',
                    'artikelanzahl',
                    'artikelanzahlnichthk',
                    'bemerkung'
                    )
    
    for row in rows:
        row = list(row)
        handzettel = Handzettel.objects.filter(pk = row[0]).first()
        # add values kw, year and retailer name
        # to the information we want to export
        row.insert(0,handzettel.kw)
        row.insert(0, handzettel.jahr)
        row.insert(0, handzettel.haendler.name)

        # the values like 'seitentyp' which are foreign keys
        # only contain the  primary key values
        # we want to get the name of the objects and replace the ids
        row[5] = Seitentyp.objects.filter(pk = row[5]).first()
        row[6] = Kategorie.objects.filter(pk = row[6]).first()
        row_num+=1
        
        # write the information into the excelsheet
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    # safe the excelsheet
    wb.save(response)
    return response