import os
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import update_session_auth_hash

from django.conf import settings

from django.views.generic import ListView
from .models import Handzettel, Seite, Referenzartikel, Kategorie, Aktionstyp, Artikel, Auslobungnormalpreis
from .models import Haendler, Branche, CustomUser, Unternehmensgruppe, Loyalty, Artikelart, Seitentyp, KategorieArtikel, Oberkategorie, ArtikelDictionary
from django.utils.datastructures import MultiValueDictKeyError

from .forms import HandzettelForm, SeitenForm, SeitenForm2, ArtikelForm, HandzettelForm_Upload, dictForm, dictFormGrey
from django.db.models import Avg
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
#from .filters import ArtikelFilter, SeitenFilter
import xlwt
import datetime 
#um den Fehler bei einem leeren Form abzufangen
from django.utils.datastructures import MultiValueDictKeyError

import sys # Enables the passing of arguments
import numpy as np
# needed for the crawler
import urllib3
import crawler
import shutil

# Create your views here.

import cv2 
import pytesseract
from pytesseract import Output

# handler403 is the name of the custom 403 permission denied view
def handler403(request, exception, template_name="403.html"): 
    return render(request, 'auswertung/403.html', {'title': 'Keinen Zugriff'})

@login_required
def home(request):
    return render(request, 'auswertung/home.html', {'title' : 'Home'})

@method_decorator(login_required, name='dispatch')
class HandzettelListView(ListView):
    model = Handzettel
    template_name = 'auswertung/handzettelliste.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'handzettel'

@method_decorator(login_required, name='dispatch')  
class ausw_HandzettelListView(ListView):
    model = Handzettel
    #queryset = Handzettel.objects.filter(status = 0) | Handzettel.objects.filter(status = 2)
    template_name = 'auswertung/ausw_handzettelliste.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'handzettel'

@login_required
def handzettelAuswertung(request, pk): # pk - handzettelid
    

    # status explanation
    #   status 0 = default
    #   status 1 = handzettel is done
    #   status 2 = handzettel evaluation was started

    # getting handzettel from database
    handzettel = Handzettel.objects.get(id=pk)
    form = HandzettelForm(instance=handzettel)

    # getting first page of handzettel, which should be displayed
    seite = Seite.objects.get(handzettel = handzettel, seitenzahl = 1)
    if request.method == 'POST':
        form = HandzettelForm(request.POST, instance=handzettel)
        if form.is_valid():
            form.save()
            handzettel.status = 2 
            handzettel.save()
            return redirect('auswertung-seite',hz = pk , pn= 1)
    return render(request, 'auswertung/ausw_handzettel.html', {'form': form, 'handzettel' : handzettel, 'seite': seite})


@login_required
def seiteAuswertung(request, hz, pn):
    # hz - handzettelid
    # pn - pagenumber 

    # status attribute for page - explanation
    # status 0 - page has not yet been touched
    # status 1 - page is done
    # status 2 - page is in progress
        
    # getting the handzettel from database which we are evaluating
    handzettel = Handzettel.objects.get(id=hz)
    # getting page from database which we want to evaluate
    tmp = Seite.objects.get(handzettel = handzettel, seitenzahl = pn)

    # set Seitentyp according to pagenumber
    if int(pn) == 1:
        tmp.seitentyp = Seitentyp.objects.get(name='Titelseite')
    elif int(pn) == handzettel.seitenanzahl:
        tmp.seitentyp = Seitentyp.objects.get(name='Rückseite')
    else:
        tmp.seitentyp = Seitentyp.objects.get(name='Innenseite')
    tmp.save()


    # check if artikelanzahl was already set, if so it can not be changed therefore we use a special form
    if tmp.artikelerstellt == False:
        form = SeitenForm(instance=tmp)
    else: # in case the number of articles has already been set
        form = SeitenForm2(instance=tmp)

    if request.method == 'POST':
        form = SeitenForm(request.POST, instance=tmp)
        if form.is_valid():
            # we store the evaluted page in seite but we do not store it in the database yet
            seite = form.save(commit = False)
            seite.save()
        
            # set letzteSeite (last used page) to find page again if evaluation is continued
            handzettel.letzteSeite = seite.seitenzahl
            handzettel.save()
            
            # store values in session variables for artikelauswertung
            request.session['handzettelid'] = hz
            request.session['seitennummer'] = pn
            request.session['artikelnummer'] = 1

            # we create a product-counter-variable to store how many products still need to be evaluated
            artikelzaehler = 1
            
            # if this is the last page, seitenauswertung is done
            if  handzettel.seitenanzahl <= int(pn):
                handzettel.SeitenAusgewertet = True
                handzettel.save()


            if seite.artikelerstellt == False and seite.artikelanzahl > 0: # if not done we first have to generate the instaces for the articles
                for i in range(seite.artikelanzahl): 
                   tmp = Artikel(seite=seite, artikelnummer = i+1)
                   tmp.save()
                   handzettel.artikelAnzahl += 1
                   handzettel.save()
                seite.artikelerstellt = True
                seite.save()
            if seite.artikelanzahl < artikelzaehler: # case: no products on page left
                seite.status = 1 # page is done
                seite.save()
                if  handzettel.seitenanzahl <= int(pn): # case: no products on page left and last page
                    handzettel.status = 1 
                    handzettel.SeitenAusgewertet = True
                    handzettel.save()
                    messages.success(request, f'Handzettel wurde erfolgreich ausgewertet!')
                    return redirect('auswertung-ausw_handzettelliste')
                else:  # case no products on page and there are more pages to evaluate
                    # page counter is incremented by one, because the page evalutation has been completed
                    
                    pn = str(int(pn) +1)
                    messages.success(request, f'Seite wurde erfolgreich ausgewertet!')
                    return redirect('auswertung-seite', hz = hz,pn = pn)
            # return redirect('auswertung-artikel')  # case products on page
            if request.POST.get('überspringen'):
                pn = seite.seitenzahl +1
                if pn > handzettel.seitenanzahl:
                    messages.warning(request, f'Es gibt keine weitere Seite.')
                    return render(request, 'auswertung/ausw_seite.html', {'form' : form, 'handzettel':handzettel, 'seite':tmp})
                else:
                    return redirect('auswertung-seite', hz = handzettel.id,pn = pn)

            if seite.kategorisiert:
                return redirect('auswertung-artikel')
            return redirect('kategorisierung-uebersicht', id=seite.id) ##############return redirect('annotation-annotation', id = seite.id)
            
    return render(request, 'auswertung/ausw_seite.html', {'form' : form, 'handzettel':handzettel, 'seite':tmp})

@login_required
def artikelAuswertung(request):
    # getting the handzettel from database which we are evaluating
    handzettel = Handzettel.objects.get(id=request.session['handzettelid'])
    # getting page from database which we want to evaluate
    seite = Seite.objects.get(handzettel = handzettel, seitenzahl = request.session['seitennummer'])
    # getting the article which we want to evaluate
    artikelanzahl = seite.artikelanzahl
    seitenzaehler = seite.seitenzahl
    artikelzaehler = request.session['artikelnummer']
    tmp = Artikel.objects.get(seite=seite, artikelnummer = artikelzaehler)
    x1 = tmp.startpunkt_x
    y1 = tmp.startpunkt_y
    x2 = tmp.endpunkt_x
    y2 = tmp.endpunkt_y

    img_path=seite.bild.url
    img_path_clean=img_path[1:]

    # read image
    img_raw = cv2.imread(img_path_clean)
    img_crop = img_raw[y1:y2, x1:x2]
    path = os.path.join(settings.MEDIA_URL,'artikeltmpimg.jpeg')
    storepath = os.path.join(settings.MEDIA_ROOT, 'artikeltmpimg.jpeg')
    
    ## ocr with tesseract and image processing with opencv
    # get grayscale image
    def get_grayscale(img_crop):
        return cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(img_crop):
        return cv2.medianBlur(img_crop,5)
    
    # thresholding
    def thresholding(img_crop):
        return cv2.threshold(img_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation
    def dilate(img_crop):
        kernel = np.ones((5,5),np.uint8)
        return cv2.dilate(img_crop, kernel, iterations = 1)
        
    # erosion
    def erode(img_crop):
        kernel = np.ones((5,5),np.uint8)
        return cv2.erode(img_crop, kernel, iterations = 1)

    # opening - erosion followed by dilation
    def opening(img_crop):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(img_crop, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    def canny(img_crop):
        return cv2.Canny(img_crop, 100, 200)
    
    # skew correction
    def deskew(img_crop):
        coords = np.column_stack(np.where(img_crop > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = img_crop.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img_crop, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    # template matching
    def match_template(img_crop, template):
        return cv2.matchTemplate(img_crop, template, cv2.TM_CCOEFF_NORMED) 

    # image processing
    resize = cv2.resize(img_crop,(0,0),fx=2,fy=2)
    gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    kernel = np.ones((5,5),np.uint8)
    canny = cv2.Canny(thresh, 100, 200)
    invert = cv2.bitwise_not(canny)
  
    # ocr with tesseract
    ocr_output_string = pytesseract.image_to_string(img_crop)
    tmp.ocr_output = ocr_output_string
    cv2.imwrite(storepath, img_crop)

    # # output of intermediate steps 
    # cv2.imshow('image window0',resize)
    # cv2.imshow('image window1',gray)
    # cv2.imshow('image window2',thresh)
    # cv2.imshow('image window3',canny)
    # cv2.imshow('image window4',invert)
    # cv2.waitKey(3000000)
    # cv2.destroyAllWindows()   

    # check if artikel is already done
    if tmp.fertig:
        articlewasnotdone = False
    else:
        articlewasnotdone = True

    # article gets oberkategorie from page
    tmp.oberkategorie = seite.oberkategorie
    tmp.save()
    # article gets other information from last article if it is not the first on the page
    if artikelzaehler > 1:
        lastarticle = Artikel.objects.get(seite=seite, artikelnummer = artikelzaehler-1)
        # tmp.aktionsmechanik = lastarticle.aktionsmechanik
        tmp.auslobungnormalpreis = lastarticle.auslobungnormalpreis
        tmp.kategorie = lastarticle.kategorie
        tmp.loyalty = lastarticle.loyalty
        tmp.artikelart = lastarticle.artikelart
        tmp.heroartikel = lastarticle.heroartikel
        tmp.coupon = lastarticle.coupon
        tmp.save()

    form = ArtikelForm(instance=tmp) # contains majority of the formfields for the Artikelauswertung
    
    form2 = dictForm() # contains formfield for the ArtikelDictionary

    dictList = ArtikelDictionary.objects.all() # get a list of all objects in our dictionary
    inDictionary = None # define this helper variable
  
    for entry in dictList: # loop through all objects in our list
        if tmp.ocr_output != None and entry.content != None:
            if entry.content in tmp.ocr_output: # check if the content attribute of our objects is contained in the output of the OCR
                tmp.kategorie = entry.key # change the connected kategorie in this case
                tmp.save() # save it
                form = ArtikelForm(instance = tmp) # update display of the kategorie
                form2 = dictFormGrey(initial={'content': entry.content}) # get the content from our entry, so that it doesn't need to be manually copied
                inDictionary = True # save this helper to check later if entries in the ArtikelDictionary contained parts of the ocr output
                break #leave the loop since we already found a match
                
            

    if request.method == 'POST':
        form2 = dictForm(request.POST) # get the written content of our cleaned name formfield for the ArtikelDictionary
        # überspringen button -> to skip artikel-evaluation, warning if there is no next page
        if request.POST.get('überspringen'):
            pn = seite.seitenzahl +1
            if pn > handzettel.seitenanzahl:
                messages.warning(request, f'Es gibt keine weitere Seite.')
                return render(request, 'auswertung/ausw_artikel.html', {'form' : form, 'handzettel':handzettel, 'seite':seite, 'artikel':tmp, 'pfad': path})
            else:
                return redirect('auswertung-seite', hz = handzettel.id,pn = pn)
        os.remove(storepath)
        form = ArtikelForm(request.POST, instance=tmp)
        if form.is_valid() and form2.is_valid():
            artikel = form.save(commit  = False)

            if inDictionary != True: #check if we found entries in our ArtikelDictionary before
                if form.cleaned_data['kategorie'] == None:
                    pass
                else:
                    newDictionaryEntry = ArtikelDictionary(key = form.cleaned_data['kategorie'], content= form2.cleaned_data['content']) # since we didn't find a match, create new entry
                    newDictionaryEntry.save() # save the entry
            

            ###########################################
            #       CHECK FOR REFERENZARTIKEL 
            ###########################################
            #check if Referenzartikel already exists
            refartikel = request.POST.get('refArtikel')
            ref = None
            if refartikel != None and refartikel != '' or form2.cleaned_data['content'] == None:
                if not Referenzartikel.objects.filter(name = refartikel): 
                    #if Referenzartikel does not exist, we create a new one and save it to the database
                    ref = Referenzartikel(name = refartikel)
                    ref.save()
                else:
                    #if Referenzartikel does exist, we get objekt from database
                    ref = Referenzartikel.objects.get(name = refartikel)
            

    
            ###########################################
            #       CHECK FOR AKTIONSTYP 
            ###########################################

             #check if Aktion already exists
            aktion = request.POST.get('aktion')
            akt = None
            if aktion != None and aktion != '':
                if not Aktionstyp.objects.filter(name = aktion): 
                    akt = Aktionstyp(name = aktion)#if Kategorie does not exist, we create a new one and save it to the database
                    akt.save()
                else:#if Kategorie does exist, we get objekt from database
                    akt = Aktionstyp.objects.get(name = aktion)
        
            #we store the Referenzartikel as an Attribute in the Artikel object
            artikel.referenzartikel = ref
            #artikel.kategorie = kat
            artikel.aktionsmechanik = akt
            artikel.save()

            if artikel.fertig and articlewasnotdone:
                handzettel.fertigeArtikel += 1
                handzettel.save()
            elif not artikel.fertig and not articlewasnotdone:
                handzettel.fertigeArtikel -= 1
                handzettel.save()


            if artikelzaehler < artikelanzahl: #case: there are more products to evaluate
                request.session['artikelnummer'] += 1
                messages.success(request, f'Artikel wurde erfolgreich ausgewertet!')
                return redirect('auswertung-artikel')
            else: #case all products evaluated
                seite.status = 1
                seite.save()     
                if seitenzaehler < handzettel.seitenanzahl: #case: there are more pages
                    seitenzaehler += 1
                    messages.success(request, f'Seite wurde erfolgreich ausgewertet!')
                    return redirect('auswertung-seite',hz= handzettel.id, pn=seitenzaehler)
                handzettel.status = 1 #case handzettel evaluation complete
                handzettel.save()
                messages.success(request, f'Handzettel wurde erfolgreich ausgewertet!')
                return redirect('auswertung-ausw_handzettelliste')
    
    
    #autocompletion 
    if 'term' in request.GET:
        #we check which referenzartikel contain the term passed through from the frontend
        qs = Referenzartikel.objects.filter(name__icontains=request.GET.get('term'))
        name = list()
        for refartikel in qs:
            #we store each referenzartikel in the name list
            name.append(refartikel.name)
        #we pass the list of referenzartikel which contain the term to the frontend    
        return JsonResponse(name, safe = False)
    
   
    if 'term3' in request.GET:
        #we check which actiontypes contain the term pass through from the frontend
        qs = Aktionstyp.objects.filter(name__icontains=request.GET.get('term3'))
        aktionsliste = list()
        for aktion in qs:
            #we store each aktiontype in the aktionsliste
            aktionsliste.append(aktion.name)
        #we pass the list of actiontypes which contain the term to the frontend
        return JsonResponse(aktionsliste, safe = False)
    return render(request, 'auswertung/ausw_artikel.html', {'form' : form, 'form2': form2, 'handzettel':handzettel, 'seite':seite, 'artikel':tmp, 'pfad': path})




