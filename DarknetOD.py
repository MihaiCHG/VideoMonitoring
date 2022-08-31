from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import darknet.darknet as darknet
import cv2
import numpy as np
from IObjectDetector import IObjectDetector
#Clasa care implementeaza interfata IObjectDetector cu functionalitatile oferite de 
#implementarea darknet
class ObjectDetector(IObjectDetector):
    def __init__(self):
        self.network, self.class_names, self.class_colors = darknet.load_network(
            "./darknet/cfg/yolov4.cfg",
            "./darknet/cfg/coco.data",
            "darknet/yolov4.weights",
            batch_size=1
        )
		#se incarca reteaua, clasele obiectelor si ponderile retelei.
        self.CLASSES81 = ['__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus','train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter','bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack','umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite','baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl','banana', 'apple', 'sandwich', 'orange', 'broccoli','carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table','toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven','toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier','toothbrush']
    
	#functie care detecteaza obiectele din imaginea primita ca parametru
    def image_detection(self, image, network, class_names, class_colors, thresh):
	    width = darknet.network_width(network)
	    height = darknet.network_height(network)
	    darknet_image = darknet.make_image(width, height, 3)

	    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	    image_resized = cv2.resize(image_rgb, (width, height),
		                           interpolation=cv2.INTER_LINEAR)

	    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
	    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
	    darknet.free_image(darknet_image)
	    image = darknet.draw_boxes(detections, image_resized, class_colors)
		#pana aici este preluat din darknet
		#de aici in jos se salveaza detectiile in formatul potrivit pentru reteaua iCAN.
	    detectionJson = {}
	    dets=[]
	    for det in detections:
		    d = [1]
		    x, y, w, h = det[2]
		    xmin = x - (w / 2)
		    xmax = x + (w / 2)
		    ymin = y - (h / 2)
		    ymax = y + (h / 2)
		    box = [xmin, ymin, xmax, ymax]
		    index = self.CLASSES81.index(det[0])
		    if  index == 1:
			    d.append("Human")
		    else:
			    d.append("Object")
		    d.append(np.array(box))
		    d.append(np.nan)
		    d.append(index)
		    d.append(float(det[1]))
		    dets.append(d)
	    detectionJson[1] = dets
	    return image_resized, detectionJson
    
	#intoarce detectiile dar si imaginea redimensionata la dimensiunea utilizata de darknet.
    def getDetections(self, image):
        imageWithDets, detections = self.image_detection(image, self.network, self.class_names, self.class_colors, 0.25)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image_rgb, imageWithDets.shape[:2], interpolation=cv2.INTER_LINEAR)
        return image, detections;
