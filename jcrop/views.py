from django.shortcuts import render, redirect
import sys # Enables the passing of arguments
from auswertung.models import Seite, Artikel
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
import os
import json



path = None


def annotation(request, id):
    global path 
    # get the page which should be annotated
    seite = Seite.objects.get(id = id)
    # path to the picture of the page
    path=seite.bild.url

    if request.method == 'POST':
        # get the data from the frontend which come in a jsonString-Format
        # it contains the coordinates of the products shown on the page
        artikel = request.POST.get("daten")
        # convert the data into json-Format
        jsonOb = json.loads(artikel)  
        # check if the number of products which got annotated 
        # equals the number of products on the page   
        if len(jsonOb["artikel"]) != seite.artikelanzahl:
            # if the numbers are not equal we return a failure message
            data = {'success': False,'message': "Artikelanzahl passt nicht. Bitte kategorisieren Sie erneut"}
            return JsonResponse(data)   
        index = 0

        # get the product-objects which are contained on the page
        artikelset = seite.artikel_set.all()

        # assign product coordinates to each product   
        for artikel in artikelset:
            koordinaten = jsonOb["artikel"][index]
            artikel.startpunkt_x = koordinaten["x"]/ 0.3
            artikel.startpunkt_y = koordinaten["y"]/ 0.3
            artikel.endpunkt_x = (koordinaten["x"] + koordinaten["w"])/ 0.3
            artikel.endpunkt_y = (koordinaten["y"] + koordinaten["h"])/ 0.3
            artikel.save()
            index = index+1
        seite.kategorisiert = True
        seite.save()
        # return success information
        data = {'success': True}
        return JsonResponse(data)
        #return redirect('auswertung-artikel')
    return render(request, 'jcrop/imagecrop.html', {'pfad' : path, 'id': id})