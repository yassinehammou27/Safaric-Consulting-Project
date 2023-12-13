from django.shortcuts import render, redirect
import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library
import pandas as pd # Import Pandas library
import sys # Enables the passing of arguments
from auswertung.models import Seite, Artikel
from django.conf import settings
from django.contrib import messages

import os

# setting global variables
ROIs = None
done = False
path = None

# Create your views here.
def annotation(request, id):

    global done
    global path
     
    storepath = os.path.join(settings.MEDIA_ROOT, 'test.jpeg')
    if request.method == 'POST':
        if request.POST.get("kategorisieren"):
            seite = Seite.objects.get(id = id)

            # image_path
            img_path=seite.bild.url
            img_path_clean=img_path[1:]

            # read image
            img_raw = cv2.imread(img_path_clean)

            # resize image to fit screen
            scale_percent = 28 # percent of original size
            width = int(img_raw.shape[1] * scale_percent / 100)
            height = int(img_raw.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            img_raw = cv2.resize(img_raw, dim, interpolation = cv2.INTER_AREA) 
           
            # select ROIs function
            global ROIs
            ROIs = cv2.selectROIs('Auswahl der Artikelbereiche', img_raw)

            for rect in ROIs:
                x1 = rect[0]
                y1 = rect[1]
                x2 = rect[2]
                y2 = rect[3]

                color = (255, 0, 0)
                thickness = 2
                img_raw = cv2.rectangle(img_raw,(x1,y1),(x1+x2,y1+y2), color, thickness = 2)     
            
            
            path = os.path.join(settings.MEDIA_URL,'test.jpeg')
            storepath = os.path.join(settings.MEDIA_ROOT, 'test.jpeg')
            
            cv2.imwrite(storepath, img_raw)
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            done = True
            # check if right amount of articles was selected
            if seite.artikelanzahl != len(ROIs):
                messages.warning(request, f'Artikelanzahl passt nicht. Bitte kategorisieren Sie erneut')
                done = False
            return render(request, 'annotation/annotation.html', {'pfad': path})
        
        if request.POST.get('bestätigen') and done:
            index = 0
            seite = Seite.objects.get(id = id)
            artikelset = seite.artikel_set.all()
            
            # save coordinates for each article
            for artikel in artikelset:
                rect = ROIs[index]
                artikel.startpunkt_x = round(rect[0]/28*100)
                artikel.startpunkt_y = round(rect[1]/28*100)
                artikel.endpunkt_x = round((rect[0]+rect[2])/28*100) # x1 plus Breite
                artikel.endpunkt_y = round((rect[1]+rect[3])/28*100)
                artikel.save()
                index = index+1
                
            os.remove(storepath)
            seite.kategorisiert = True
            seite.save()
            return redirect('auswertung-artikel')
        else:
            messages.warning(request, f'Die Artikelanzahl der ausgewählten Artikel passt nicht. Bitte kategorisieren Sie erneut.')
            return render(request, 'annotation/annotation.html', {'pfad': path})
    return render(request, 'annotation/annotation.html')

