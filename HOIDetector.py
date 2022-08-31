from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import _init_paths
from PIL import Image
import matplotlib.pyplot as plt
from ult.config import cfg
import json
import tensorflow as tf
import numpy as np
import argparse
import pickle
import ipdb
import threading

from ult.vsrl_eval import VCOCOeval
from models.test_im_det import hoiDetectAndShowObj

class HOIDetector(threading.Thread):
    def __init__(self, threadID, queueODToHOI, queueHOIToMain, network, sess):   
	    threading.Thread.__init__(self)
	    self.threadID = threadID
	    self.stopFlag = False 
	    self.lockStop = threading.Lock()   
	    self.queueODToHOI = queueODToHOI
	    self.queueHOIToMain = queueHOIToMain
	    self.network = network
	    self.sess = sess
        #se initializeaza datele necesare retelei pentru a putea prezice interactiunea, o masca cu care sunt inmultite predictiile
        #si actiunile ce pot fi detectate de retea
	    self.priorMask     = pickle.load( open( cfg.DATA_DIR + '/' + 'prior_mask.pkl', "rb" ), encoding = "latin1" )
	    self.ActionDic     = json.load(   open( cfg.DATA_DIR + '/' + 'action_index.json'))
	    self.ActionDicInv = {y:x for x,y in self.ActionDic.items()}
	    
    #foloseste o functie din iCAN care detecteaza interactiuniile
    def getHOIDetection(self, image, objectDetections):
	    detections = []
	    hoiDetectAndShowObj(self.sess, self.network, image, 1, objectDetections, self.priorMask, self.ActionDicInv, 0.4, 0.8, 3, detections)
	    return detections
        
    def run(self):	
        try:
            while True:#bucla infinita din care iese atunci cand este setat flag-ul stopFlag din componenta Main.
                with self.lockStop:
                    if self.stopFlag:#atunci cand acest flag este setat se termina executia acestui 
                        #fir de executie, accesul la aceasta variabila se face folosind un mecanism de sincronizare
                        print("HOIDetector thread closed.")
                        exit()
                imageData = self.queueODToHOI.get()#se extrage imagine si obiectele ei
                hoiDetections = self.getHOIDetection(imageData[1], imageData[2])#se detecteaza intracgtiunile
                if not self.queueHOIToMain.full():#daca nu este plina coada se adauga numarul imaginii, imaginea si detectiile in coada, altfel se asteapta eliberarea unui loc in coada
                    self.queueHOIToMain.put((imageData[0], imageData[1], hoiDetections))
        except Exception as e:
            print("HoiDetector "+str(e))
			
    def stop(self):# functia care este apelata pentru terminarea executiei
        with self.lockStop:
            self.stopFlag = True


    def close(self):
	    sess.close()
		
