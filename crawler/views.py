import os
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from django.conf import settings

from auswertung.models import Handzettel, Seite, Haendler

from django.utils.datastructures import MultiValueDictKeyError

from django.db.models import Avg
from django.http import HttpResponse

import xlwt
import datetime 
#um den Fehler bei einem leeren Form abzufangen
from django.utils.datastructures import MultiValueDictKeyError

# for the crawler
from .models import UploadedFiles2, crawlURL
import urllib3
import crawler
import shutil
from .forms import crawlHandzettelForm
# for converting the pdfs to images
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
# Create your views here.
@login_required
def crawl_done(request):
    return render(request, 'crawl/crawlerdone.html')

@login_required
def crawl_classify(request):
    #some important variables we are going to use for pathing & urls
    path = settings.CRAWLER_ROOT
    urlHelper = settings.CRAWLER_URL
    mediaHelper = settings.MEDIA_ROOT

    for f in os.listdir(path): # loop through all entries in the CRAWLER_ROOT directory
        secondDir = os.path.join(path,f) # save directorypath to f
        if os.path.isdir(secondDir): #  check if f is a directory (not a csv or a different file, as pdf-crawler creates csv files by default too)
            os.chdir(secondDir) # enter directory that is unique to the website that has been crawled
            for g in os.listdir(os.getcwd()): # loop through all files that have been crawled
                saver = UploadedFiles2(name= str(g), datei = g, uniqueDir = f) # temp save the document as an uploadedfile
                if UploadedFiles2.objects.filter(name__exact= saver.name).exists(): # check if the document has been uploaded already
                    continue # don't create this object
                else:
                    saver.save() # create this object
            os.chdir(os.path.dirname(path)) # change directory back to where we started. Else we'll get nested directories 
        else:
            continue

    uploadedfiles = UploadedFiles2.objects.all()  #refresh uploadedfiles variable

    if request.method == 'POST' and 'cancel' in request.POST:
        allHz = Handzettel.objects.all().filter(haendler__name__exact = 'Crawled')
        for hz in allHz:
            hz.delete()


        UploadedFiles2.objects.all().delete() # delete all UploadedFiles2 objects as they aren't necessary anymore
        for entry in os.listdir(path): # iterate through all entries in our crawler_ROOT directory
            pathToEntry = os.path.join(path, entry) # save the path to each entry in a variable
            if os.path.isdir(pathToEntry):                # check if entry is a direcotry
                if len(os.listdir(pathToEntry)) == 0: # check if directory is empty
                    os.rmdir(pathToEntry) # delete empty directory
                else:
                    for f in os.listdir(pathToEntry): # iterate through all files in this directory (we know there won't be any more directories because this is how pdf-crawler works)
                        os.remove(os.path.join(pathToEntry, f)) # delete file from directory
                    os.rmdir(pathToEntry) # delete directory now that all files have been removed
            else:   # since it's not a directory, it is a file. 
                os.remove(pathToEntry) # delete the entry
        return redirect('auswertung-home')

    if request.method == 'POST' and 'classify' in request.POST:
        sindHz = request.POST.getlist('handouts') # get list of the names of the uploadedfiles that are selected on the template via checkboxes
        siteCounter= 0 # counter is created everytime this button is clicked. It is used to only transfer the selected uploadedfiles to handzettel objects
        if len(sindHz) == 0: 
            messages.warning(request, f'Sie haben keine Handzettel ausgewählt.')
            return render(request, 'crawl/crawlerclassify.html', {'uploadedfiles': uploadedfiles, 'urlHelper': urlHelper})
        elif len(UploadedFiles2.objects.all()) == 0: # check if there are any uploadedfiles at all (catches errors if someone navigates back to classify from rename view)
            messages.warning(request, f'Es liegen keine weiteren gecrawlten Dokumente vor oder die gecrawlten Dokumente wurden bereits gelöscht. Bitte fahren Sie mit der Klassifizierung fort.')
            return redirect('crawlerrename')
        for doc in sindHz: # iterate through each object that was selected on template via checkboxes
            if Handzettel.objects.filter(handzetteldatei__exact = sindHz[siteCounter]):
                siteCounter= siteCounter+1 #skip this doc without creating a handzettel for it
            else:  
                hzHelper = UploadedFiles2.objects.all().filter(name__exact = sindHz[siteCounter]).get() # create helper that gets the uploadedfile object of the handout that has been selected on template
                if Haendler.objects.filter(name__exact = 'Crawled').exists(): #check if the Haendler 'Crawled' exists
                    unbekannterHaendler = Haendler.objects.all().filter(name__exact = 'Crawled').get() # save Haendler 'Crawled'

                    handzettel = Handzettel(haendler= unbekannterHaendler, jahr = 2000, kw=1, handzetteldatei = hzHelper.datei) # create handzettel object with the given parameters
                    handzettel.save()
                    os.replace(os.path.join(os.path.join(path, hzHelper.uniqueDir), str(hzHelper.datei)), os.path.join(mediaHelper, str(hzHelper.datei))) # change path of handzettel from crawlResult directory to media directory

            # convert every page from handzettel-pdf to one single jpg
                    images = convert_from_path(os.path.join(settings.MEDIA_ROOT, str(hzHelper.datei)), output_folder='media', fmt='jpeg')
            # seitenzahl counter
                    counter = 1          
            # iterate over all created pages of handzettel-pdf
                    for image in images:          #iterate through all images in the list 
                # get the right path depeding on usage of Windows or iOS devices and create new Seite with seitenzahl
                        if(image.filename.split('/')[0] == 'media'):
                            tmp = Seite(bild=image.filename.split('/')[-1],seitenzahl=counter, handzettel=handzettel)   
                        else: 
                            tmp = Seite(bild=image.filename.split('\\')[-1],seitenzahl=counter, handzettel=handzettel)
                        tmp.save() 
                        counter += 1
                # save seitenanzahl to handzettel
                    handzettel.seitenanzahl = counter - 1
                    handzettel.save() 
                    
                    siteCounter = siteCounter+1 # count up 
                    hzHelper.delete() # delete the helper from the system


                else:
                    unbekannterHaendler = Haendler(name = 'Crawled') #create Haendler 'Crawled' since it doesn't exist yet
                    unbekannterHaendler.save() #save the Haendler
                    
                    handzettel = Handzettel(haendler = unbekannterHaendler, jahr = 2000, kw = 1, handzetteldatei= hzHelper.datei) # create handzettel object with the given parameters
                    handzettel.save()
                    os.replace(os.path.join(os.path.join(path, hzHelper.uniqueDir), str(hzHelper.datei)), os.path.join(mediaHelper, str(hzHelper.datei))) # change path of handzettel from crawlResult directory to media directory

                    # convert every page from handzettel-pdf to one single jpg
                    images = convert_from_path(os.path.join(settings.MEDIA_ROOT, str(handzettel.handzetteldatei)), output_folder='media', fmt='jpeg')
                     # seitenzahl counter
                    counter = 1          
                     # iterate over all created pages of handzettel-pdf
                    for image in images:          #iterate through all images in the list 
                          # get the right path depeding on usage of Windows or iOS devices and create new Seite with seitenzahl
                        if(image.filename.split('/')[0] == 'media'):
                            tmp = Seite(bild=image.filename.split('/')[-1],seitenzahl=counter, handzettel=handzettel)   
                        else: 
                            tmp = Seite(bild=image.filename.split('\\')[-1],seitenzahl=counter, handzettel=handzettel)
                        tmp.save() 
                        counter += 1
                         # save seitenanzahl to handzettel
                    handzettel.seitenanzahl = counter - 1
                    handzettel.save() 
                    siteCounter = siteCounter+1 # count up 
                    hzHelper.delete() # delete the helper from the system
        uploadedfiles = UploadedFiles2.objects.all() # refresh uploadedfiles to be rendered on template 
        return render(request, 'crawl/crawlerclassify.html', {'uploadedfiles': uploadedfiles, 'urlHelper': urlHelper})

    if request.method == 'POST' and 'done' in request.POST:
        allHz = Handzettel.objects.all().filter(haendler__name__exact = 'Crawled') #get all Handzettel with the Haendler name 'Crawled'
        if len(allHz) == 0:
            messages.warning(request, f'Sie müssen erst Handzettel erstellen, bevor Sie weiter zum nächsten Schritt können.')
            return render(request, 'crawl/crawlerclassify.html', {'uploadedfiles': uploadedfiles, 'urlHelper': urlHelper})
        elif len(UploadedFiles2.objects.all()) == 0: # check if there are any uploadedfiles at all (catches errors if someone navigates back to classify from rename view)
            messages.warning(request, f'Es liegen keine weiteren gecrawlten Dokumente vor oder die gecrawlten Dokumente wurden bereits gelöscht. Bitte fahren Sie mit der Klassifizierung fort.')
            return redirect('crawlerrename')
    
        UploadedFiles2.objects.all().delete() # delete all UploadedFiles2 objects as they aren't necessary anymore
        for entry in os.listdir(path): # iterate through all entries in our crawler_ROOT directory
            pathToEntry = os.path.join(path, entry) # save the path to each entry in a variable
            if os.path.isdir(pathToEntry):                # check if entry is a direcotry
                if len(os.listdir(pathToEntry)) == 0: # check if directory is empty
                    os.rmdir(pathToEntry) # delete empty directory
                else:
                    for f in os.listdir(pathToEntry): # iterate through all files in this directory (we know there won't be any more directories because this is how pdf-crawler works)
                        os.remove(os.path.join(pathToEntry, f)) # delete file from directory
                    os.rmdir(pathToEntry) # delete directory now that all files have been removed
            else:   # since it's not a directory, it is a file. 
                os.remove(pathToEntry) # delete the entry
        return redirect('crawlerrename')
    return render(request, 'crawl/crawlerclassify.html', {'uploadedfiles': uploadedfiles, 'urlHelper': urlHelper})

@login_required
def crawl_handout(request):
    urllib3.disable_warnings() # used to stop the crawler from spamming the terminal
    allURLs = list(crawlURL.objects.all()) # get list of all crawlURLS that have been created by administrators
    if len(allURLs) == 0:
        messages.warning(request, f'Sie müssen erst crawlURLs im Admin-Panel anlegen.')
        return render(request, 'crawl/crawlerstart.html',{'allURLs':allURLs})

    if request.method == 'POST':
        for u in allURLs: # iterate through all urls in the list
            try:
                crawler.crawl(url=u.url,output_dir="crawlerResults", method="rendered-all", depth=u.crawlTiefe, gecko_path='C:\Program Files (x86)\Geckodriver\geckodriver-v0.29.0\geckodriver.exe') #use pdf-crawler on the urls, with the crawl depth which have been set on creation of the crawlURL
            except:
                #print('this link was stale, lets ignore it')  
                pass      
        return redirect('crawlerclassify')
    return render(request, 'crawl/crawlerstart.html',{'allURLs':allURLs})
@login_required
def crawl_rename(request):
    crawledHandzettel = list(Handzettel.objects.all().filter(haendler__name__exact = 'Crawled')) # get a list of all Handzettel with the Haendler name "Crawled"
    # getting handzettel from database
    hz = crawledHandzettel[0] # temp save the first Handzettel from the list
    form = crawlHandzettelForm() # create an empty form
    seite = Seite.objects.get(handzettel = hz, seitenzahl = 1)  # get first page of handzettel, which should be displayed 

    if request.method == 'POST' and 'next' in request.POST:
        form = crawlHandzettelForm(request.POST, instance=hz) # get the posted data from form and the hz instance
        
        if form.is_valid(): # check if input to form is valid. form.cleaned_data needs to be within this block, else it cannot read the form input
            if form.cleaned_data['haendler'] == None: # no Haendler has been chosen
                messages.warning(request, f'Bitte wählen Sie einen validen Händler.')
                return redirect('crawlerrename')
            if form.cleaned_data['jahr'] == None: # no Haendler has been chosen
                messages.warning(request, f'Bitte wählen Sie ein valides Jahr.')
                return redirect('crawlerrename')    
            newPdfName = str(form.cleaned_data['haendler'].name) + '_' + str(form.cleaned_data['kw']) + '_' + str(form.cleaned_data['jahr']) + '.pdf'
            
            if form.cleaned_data['haendler'].name == 'Crawled': # Haendler has been changed to 'Crawled'
                messages.warning(request, f'Der Haendler "Crawled" ist nur für neu gecrawlte Handzettel vorgesehen. Bitte wählen Sie einen validen Haendler.')
            elif Handzettel.objects.filter(handzetteldatei__exact = newPdfName).exists():    # The pdf of this name already exists in the system       
                messages.warning(request, f'Dieser Handzettel existiert bereits. Bitte ändern Sie die Angaben oder verwerfen Sie diesen Handzettel.')
            else: 
                form.save() #save all inputs from this form
                os.rename(os.path.join(settings.MEDIA_ROOT, str(hz.handzetteldatei)), os.path.join(settings.MEDIA_ROOT, newPdfName )) #change the name of the pdf to newPdfName on server
                hz.handzetteldatei = newPdfName # change the name of the pdf in the django system
                hz.save() # save the handzettel object
                crawledHandzettel.remove(hz) # remove the handzettel object from our list. if the last one is removed the if statement below
                if len(crawledHandzettel) == 0: # will check if list is empty and redirect to the "crawlerdone" page
                    return redirect('crawlerdone')
                form = crawlHandzettelForm() # empty the form again, so that the old input isn't rendered
            return redirect('crawlerrename') 

    if request.method == 'POST' and 'delete' in request.POST:
        form = crawlHandzettelForm(request.POST, instance=hz) # get post data and the correct handzettel instance
        crawledHandzettel.remove(hz) #remove the handzettel from our list
        hz.delete() # delete the handzettel object
        # os.remove(os.path.join(settings.MEDIA_ROOT, str(hz.handzetteldatei))) # delete the handzettel from directory
        if len(crawledHandzettel) == 0: # check again is list is empty 
            return redirect('crawlerdone')
        return redirect('crawlerrename')
    return render(request, 'crawl/crawlerrename.html', {'hz':hz, 'form': form, 'seite': seite})
