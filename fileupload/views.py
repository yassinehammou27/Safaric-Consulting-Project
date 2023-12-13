import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from auswertung.models import Handzettel, Seite, Referenzartikel, Kategorie, Aktionstyp, Artikel, Auslobungnormalpreis
from auswertung.models import Haendler, Branche, CustomUser, Unternehmensgruppe, Loyalty, Artikelart, Seitentyp, KategorieArtikel, Oberkategorie
from django.utils.datastructures import MultiValueDictKeyError
from .models import UploadedFiles
from auswertung.forms import HandzettelForm, SeitenForm, SeitenForm2, ArtikelForm, HandzettelForm_Upload
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)


@login_required
def upload_handout(request):

    # valid file types can be defined here
    FILE_TYPES = ['png', 'jpg', 'jpeg', 'pdf']
    form = HandzettelForm_Upload()

    if request.method == 'POST':

        # clear "hochgeladene dateien" table shown at uploadsuccesspage
        UploadedFiles.objects.all().delete()

        form = HandzettelForm_Upload(request.POST, request.FILES)
        files = request.FILES.getlist('handzetteldatei')
        
        if form.is_valid():
            uploadform = form.save(commit=False)

            # check if no file has been selected 
            if not files:
                messages.warning(request, f' Der Upload ist fehlgeschlagen. Es wurde keine Datei ausgewählt.')
                return redirect('uploadstart')
       
            # iterate over all selected files
            for f in files:

                try:
                    uploadform.handzetteldatei = f
                    file_type = uploadform.handzetteldatei.url.split('.')[-1]
                    file_type = file_type.lower()
                    dateiname = uploadform.handzetteldatei.url.split(".")[0]
                    dateiname = dateiname.split("/")[-1]
                    
                    # check if file is image or pdf
                    if file_type not in FILE_TYPES:
                        messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Es wurde nicht der richtige Dateityp ausgewählt.')
                        continue

                    # check if haendler is valid
                    n = dateiname.split("_")[0]
                    if not Haendler.objects.filter(name = n):
                        messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Der Händler wurde falsch geschrieben oder ist noch nicht angelegt. Bitte wenden Sie sich im zweiten Fall an einen Admin.')
                        continue
                    else:
                        uploadform.haendler = Haendler.objects.get(name= n)
                    
                    # check if kalenderwoche is valid
                    k = dateiname.split("_")[1]
                    if not 0 < int(k) < 54:
                        messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Die Kalenderwoche entspricht nicht dem angegebenen Format.')
                        continue
                    else:
                        uploadform.kw = k

                    # check if year is valid
                    j = dateiname.split("_")[2]
                    if not 1999 <= int(j) <= 2099:
                        messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Das Jahr entspricht nicht dem angegebenen Format.')
                        continue
                    else:
                        uploadform.jahr = j

                    # pdf processing
                    if file_type =='pdf':

                        # check if handzettel already exists
                        if (Handzettel.objects.filter(haendler__name=n, kw=k, jahr=j)).count() > 0:
                            messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Der Handzettel '+dateiname+' ist schon vorhanden.')
                            continue
                        
                        # create new handzettel
                        else:
                            uploadform.pk = None
                            uploadform.save()
                            UploadedFiles.objects.create(name=uploadform.handzetteldatei.url)

                            # convert every page from handzettel-pdf to one single jpg
                            images = convert_from_path(uploadform.handzetteldatei.path, output_folder='media', fmt='jpeg')

                            # seitenzahl counter
                            counter = 1
                            
                            # iterate over all created pages of handzettel-pdf
                            for image in images:
                                
                                # get the right path depeding on usage of Windows or iOS devices and create new Seite with seitenzahl
                                if(image.filename.split('/')[0] == 'media'):
                                    tmp = Seite(bild=image.filename.split('/')[-1],seitenzahl=counter, handzettel=uploadform)   
                                else: 
                                    tmp = Seite(bild=image.filename.split('\\')[-1],seitenzahl=counter, handzettel=uploadform)

                                tmp.save() 
                                counter += 1

                            # save seitenanzahl to handzettel
                            uploadform.seitenanzahl = counter - 1

                            uploadform.save() 
                    
                    # image processing
                    else:

                        # check if page number is valid
                        p = dateiname.split("_")[3]
                        if not 1 <= int(p) <= 1000:
                            messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Die Seite entspricht nicht dem angegebenen Format.')
                            continue

                        # check if seite already exists
                        elif (Seite.objects.filter(handzettel__haendler__name=n, seitenzahl=p, handzettel__kw=k, handzettel__jahr=j  )).count() > 0:
                            messages.warning(request, ' Der Upload von '+dateiname+' ist fehlgeschlagen. Die Seite '+dateiname+' ist schon vorhanden.')
                            continue
                        else:
                            UploadedFiles.objects.create(name=uploadform.handzetteldatei.url)

                        # check if the handzettel associated with the page exists to add a new Seite to an existing handzettel or to first create a new handzettel and add new Seite afterwards
                        if (Handzettel.objects.filter(haendler__name=n, kw=k, jahr=j)).count() > 0:

                            # add Seite to existing Handzettel and increase seitenanzahl by one
                            uploadform_stored = Handzettel.objects.get(haendler__name=n, kw=k, jahr=j)
                            if(uploadform.handzetteldatei.url.split('/')[0] == 'media'):
                                tmp = Seite(bild=os.path.basename(uploadform.handzetteldatei.url),seitenzahl=p, handzettel=uploadform_stored)   
                            else: 
                                tmp = Seite(bild=os.path.basename(uploadform.handzetteldatei.url),seitenzahl=p, handzettel=uploadform_stored)
                            tmp.save()
                            uploadform_stored.seitenanzahl += 1
                            uploadform_stored.save()

                        else:  

                            # create new Handzettel and add Seite. Set seitenanzahl to one 
                            uploadform.pk = None
                            uploadform.seitenanzahl = 1
                            uploadform.save()
                            if(uploadform.handzetteldatei.url.split('/')[0] == 'media'):
                                tmp = Seite(bild=os.path.basename(uploadform.handzetteldatei.url),seitenzahl=p, handzettel=uploadform)   
                            else: 
                                tmp = Seite(bild=os.path.basename(uploadform.handzetteldatei.url),seitenzahl=p, handzettel=uploadform)
                            tmp.save()    
                   
                except (ValueError, IndexError) as e:
                    messages.warning(request, f' Der Upload von '+dateiname+' ist fehlgeschlagen. Der Dateiname entspricht nicht dem angegebenen Format.')
 
            uploadedfiles = UploadedFiles.objects.all()    
            return render(request, 'fileupload/uploadsuccess.html', {'uploadform': uploadform, 'uploadedfiles': uploadedfiles})
    context = {"form": form,}
    return render(request, 'fileupload/uploadstart.html', context)


