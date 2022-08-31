from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import cv2
import numpy as np

import paho.mqtt.client as mqtt
import json

#clasele obiectelor ce pot fi detectate
CLASSES = ['__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus','train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter','bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'relationphant', 'bear', 'zebra', 'giraffe', 'backpack','umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite','baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl','banana', 'apple', 'sandwich', 'orange', 'broccoli','carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table','toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven','toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier','toothbrush']


class Stream():
	def __init__(self, mqttConn, showVideo):
		self.mqttConn = mqttConn
		self.showVideo = showVideo
		#se incarca fisierul cu activitatile ce trebuie sa fie monitorizate
		self.activities = json.load(open('activities.json',))
		print(self.activities)
	
	#functia care afiseaza video activitatile si seteaza activitatea curenta din MQTTConnection
	#afisarii video este preluata din fisierul Demo.ipynb din iCAN
	#dar a fost modificata pentru a afisa folosind opencv, in loc de matplotlib
	def showFrame(self,image, hoiDetections):
		cc = plt.get_cmap('hsv', lut=6)
		HO_dic = {}
		HO_set = set()
		count = 0
		#pentru fiecare relatie
		for relation in hoiDetections:
			#iCAN are la intrare un anumit format, de aceea s-a pus id-ul 1 la toate imaginile
			if (relation['image_id'] == 1):
				action_count = -1
				H_box = relation['person_box'] 

				if tuple(H_box) not in HO_set:
					HO_dic[tuple(H_box)] = count
					HO_set.add(tuple(H_box))
					count += 1 

				show_H_flag = 0
				
				#se verifica daca exista vreo actiune monitorizata, in oridinea importantei, de asemenea se deseneaza si activitatile
				find = False
				if relation['smile'][4] > 10.0:
					cv2.putText(image, 'smile, ' + "%.2f" % relation['smile'][4], (int(H_box[0])+10, int(H_box[1])+25 + action_count * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 2)
					action_count += 1 
					show_H_flag = 1

				if relation['stand'][4] > 10.0:
					cv2.putText(image, 'stand, ' + "%.2f" % relation['stand'][4], (int(H_box[0])+10, int(H_box[1])+25 + action_count * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 2)
					action_count += 1             
					show_H_flag = 1
					self.mqttConn.setActivity({
						"cod": "007",
						"description": "stand - "+ self.activities[6]["description"],
						"confidence": "%.2f" % relation['stand'][4]
					})

				if relation['run'][4] > 10.0:
					cv2.putText(image, 'stand, ' + "%.2f" % relation['stand'][4], (int(H_box[0])+10, int(H_box[1])+25 + action_count * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9,np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 2)
					action_count += 1  
					show_H_flag = 1

				if relation['walk'][4] > 10.0:
					cv2.putText(image,  'walk, ' + "%.2f" % relation['walk'][4], (int(H_box[0])+10, int(H_box[1])+25 + action_count * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 2)
					action_count += 1  
					show_H_flag = 1
					
				for activity in self.activities[:-1]:
					find = False
					for action_key, action_value in relation.items():
						if (action_key.split('_')[-1] != 'agent') and action_key != 'image_id' and action_key != 'person_box':
							if (not np.isnan(action_value[0])) and (action_value[5] > 7.0):
								if activity["name"] == action_key.split('_')[0]:
										self.mqttConn.setActivity({
											"cod": activity["cod"],
											"description": action_key.split('_')[0] +" - "+ activity["description"],
											"confidence": "%.2f" % action_value[5]
										})
										find = True
										break
					if find == True:
						break
				#daca nu exista atunci este setata activitatea 'other'
				if find == False:
					self.mqttConn.setActivity({
						"cod": self.activities[-1]["cod"],
						"description": self.activities[-1]["description"],
						"confidence": "0.0"
					})
				#daca se doreste afisarea video a activitatilor, pentru fiecare activitate se deseneaza chenarele obiecelor si activitatile pe imagini
				if self.showVideo:
					for action_key, action_value in relation.items():
						if (action_key.split('_')[-1] != 'agent') and action_key != 'image_id' and action_key != 'person_box':
							if (not np.isnan(action_value[0])) and (action_value[5] > 7.0):
								O_box = action_value[:4]

								action_count += 1

								if tuple(O_box) not in HO_set:
									HO_dic[tuple(O_box)] = count
									HO_set.add(tuple(O_box))
									count += 1   
								
								
								image = cv2.rectangle(image, (int(H_box[0]), int(H_box[1])), (int(H_box[2]), int(H_box[3])), np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 3)
								text = action_key.split('_')[0] + ' ' + CLASSES[np.int(action_value[4])] + ', ' + "%.2f" % action_value[5]
								
									
								cv2.putText(image, text, (int(H_box[0])+10, int(H_box[1])+25 + action_count * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, np.multiply(cc(HO_dic[tuple(O_box)])[:3], [255,255,255]), 2)
								image = cv2.rectangle(image, (int(O_box[0]), int(O_box[1])), (int(O_box[2]), int(O_box[3])), np.multiply(cc(HO_dic[tuple(O_box)])[:3], [255,255,255]), 3)
					#daca nu s-a intalnit vreo activitate care este generata de interactiunea cu un obiect, atunci se deseneaza doar chenarul persoanei, activitatile sunt desenate in cele 4 if-uri de mai sus	
					if show_H_flag == 1:
						image = cv2.rectangle(image, (int(H_box[0]), int(H_box[1])), (int(H_box[2]), int(H_box[3])), np.multiply(cc(HO_dic[tuple(H_box)])[:3], [255,255,255]), 3)
		#daca se doreste afisarea video se deseneaza imaginile cu activitatile si chenarele obiectelor/persoanei intr-o fereastra
		if self.showVideo:
			image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
			cv2.imshow("Video", image)
			cv2.waitKey(1)
