from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import jetson
import jetson.utils
import jetson.inference

from IObjectDetector import IObjectDetector
import cv2
import numpy as np
import sys


class ObjectDetector(IObjectDetector):
	def __init__(self):
		#se instantiaza reteaua ssd-mobilenet v2
		self.net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.25)
		#se declara lista de clase de obiecte detectate de retelele din darknet
		self.CLASSES81 = ['__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus','train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter','bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack','umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite','baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl','banana', 'apple', 'sandwich', 'orange', 'broccoli','carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table','toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven','toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier','toothbrush']
		#se declara lista de clase de obiecte detectate de retelele din jetson inference
		self.CLASSES91 = ['__backgroud__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'street sign', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'hat', 'backpack', 'umbrella', 'shoe', 'eye glasses', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'plate', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'mirror', 'dining table', 'window', 'desk', 'toilet', 'door', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'blender', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']


	#se detecteaza obiectele din imaginea primita ca parametru
	def getDetections(self, image):
		image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
		width = image_rgba.shape[1]
		height = image_rgba.shape[0]
		#imaginea trebui dusa in memoria placii video
		cuda_frame = jetson.utils.cudaFromNumpy(image_rgba)
		detections = self.net.Detect(cuda_frame, width, height)
		detectionJson = {}
		dets = []
		#se salveaza obiectele in formatul necesar pentru reteaua iCAN
		for detection in detections:
			try:
				det = [1]
				box = []
				box.append(detection.Left)
				box.append(detection.Top)
				box.append(detection.Left+detection.Width)
				box.append(detection.Top+detection.Height)
				if  detection.ClassID == 1:
					det.append("Human")
				else:
					det.append("Object")
				det.append(np.array(box))
				det.append(np.nan)
				
				index = self.CLASSES81.index(self.CLASSES91[detection.ClassID])
				det.append(index)
				det.append(detection.Confidence)
				dets.append(det)
			except:
				print(sys.exc_info()[0])
		detectionJson[1] = dets
		frame_rgba = jetson.utils.cudaToNumpy(cuda_frame, width, height)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		return image, detectionJson#se intoarce imaginea originala si obiectele
		#imaginea este necesara pentru ca darknet trebuie sa intoarca imaginea redimensionata
        
    
    
