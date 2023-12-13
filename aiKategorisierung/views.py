import os
from django.shortcuts import render, redirect
from django.contrib import messages
from auswertung.models import Handzettel, Seite
from django.conf import settings
from django.views.generic import ListView
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
import sys # Enables the passing of arguments
import numpy as np
import cv2 
import pytesseract
from pytesseract import Output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
import pathlib
import tensorflow as tf
import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

@login_required
def uebersicht(request, id):
    return render(request, 'uebersicht.html', {'id': id})

def load_image_into_numpy_array(path):
    """ Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
    path: the file path to the image

    Returns:
    uint8 numpy array with shape (img_height, img_width, 3)
    """
    return np.array(Image.open(path))

boxlist = []
classlist = []
@login_required
def aiKategorisierungView(request, id):
    global boxlist
    global classlist
    seite = Seite.objects.get(id = id)
    if request.method == 'GET':
        #define path to model and labelmap
        PATH_TO_MODEL_DIR = os.path.join(settings.KI_ROOT, 'inference_graph')
        IMAGE_PATHS = os.path.join(settings.MEDIA_ROOT, os.path.basename(seite.bild.url))
        PATH_TO_LABELS = os.path.join(settings.KI_ROOT,'label_map.pbtxt')
        PATH_TO_SAVED_MODEL = os.path.join(PATH_TO_MODEL_DIR, "saved_model")
        
        start_time = time.time()

        # Load saved model and build the detection function
        detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)

        end_time = time.time()
        elapsed_time = end_time - start_time

        category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

        


        image_np = load_image_into_numpy_array(IMAGE_PATHS)

        # Things to try:
        # Flip horizontally
        # image_np = np.fliplr(image_np).copy()

        # Convert image to grayscale
        # image_np = np.tile(
        #     np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)

        # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
        input_tensor = tf.convert_to_tensor(image_np)
        # The model expects a batch of images, so add an axis with `tf.newaxis`.
        input_tensor = input_tensor[tf.newaxis, ...]

        # input_tensor = np.expand_dims(image_np, 0)
        detections = detect_fn(input_tensor)
      
        # All outputs are batches tensors.
        # Convert to numpy arrays, and take index [0] to remove the batch dimension.
        # We're only interested in the first num_detections.
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                    for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        image_np_with_detections = image_np.copy()

        #visualize the detected objects
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.30,
            agnostic_mode=False)

        plt.figure()
        plt.imsave(os.path.join(settings.MEDIA_ROOT,'kioutput.jpg'), image_np_with_detections)

        # This is the way I'm getting my coordinates
        boxes = detections['detection_boxes']
        # get all boxes from an array
        max_boxes_to_draw = boxes.shape[0]
        # get scores to get a threshold
        scores = detections['detection_scores']
        # this is set as a default but feel free to adjust it to your needs
        min_score_thresh=.30
        # iterate over all objects found
        global boxlist
        boxlist = []
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            # 
            if scores is None or scores[i] >= min_score_thresh:
                # boxes[i] is the box which will be drawn
                class_name = category_index[detections['detection_classes'][i]]['name']
                boxlist.append(boxes[i])
                classlist.append(detections['detection_classes'][i])
        img_path=seite.bild.url
        img_path_clean=img_path[1:]
        img = cv2.imread(img_path_clean)
        height, width = img.shape[:2]
       
        

    # sphinx_gallery_thumbnail_number = 2
    ###
    if request.method == 'POST':
        if request.POST.get("zurAuswertung"):
            ## aiKategorisierung hier verwerfen?
            
            
            if len(boxlist) != seite.artikelanzahl:
                messages.warning(request, f'Artikelanzahl stimmt nicht mit der gefundenen Anzahl überein')
                return render(request, 'aiKategorisierung.html', {'pfad' : os.path.join(settings.MEDIA_URL, 'kioutput.jpg')})
            
            # get the image that gets annotated
            img_path=seite.bild.url
            img_path_clean=img_path[1:]
            img = cv2.imread(img_path_clean)

            index = 0
            # get the product-objects which are contained on the page
            artikelset = seite.artikel_set.all()

            # get the shape of the image
            height, width = img.shape[:2]
            # assign product coordinates to each product   
            for artikel in artikelset:
                artikel.startpunkt_x = boxlist[index][1]*width
                artikel.startpunkt_y = boxlist[index][0]*height
                artikel.endpunkt_x = boxlist[index][3]*width
                artikel.endpunkt_y = boxlist[index][2]*height
                if classlist[index] == 2:
                    artikel.heroartikel = True
                artikel.save()
                index = index+1
            seite.kategorisiert = True
            seite.save()
            return redirect('auswertung-artikel')
        if request.POST.get('zurAnnotation'):
            return redirect('annotation-annotation', id = seite.id)

    return render(request, 'aiKategorisierung.html', {'pfad' : os.path.join(settings.MEDIA_URL, 'kioutput.jpg')})