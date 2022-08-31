from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import threading
import _init_paths




from DarknetOD import ObjectDetector
#from JetsonInferenceObjectDetector import ObjectDetector


class AcqOD(threading.Thread):
    def __init__(self, threadID, queueImageToHOI, acquisition):
	    threading.Thread.__init__(self)
	    self.threadID = threadID
	    self.stopFlag = False
	    self.lockStop = threading.Lock()
	    self.queueImageToHOI = queueImageToHOI
	    
	    if acquisition == 'Zed':
	        from ZedAcquisition import Acquisition
	    else:
	        from CameraAcquisition import Acquisition
	        
	    self.acq = Acquisition()
	    self.od = ObjectDetector()
	    self.cntFrame = 1
	    
    def run(self):
        try:
            while True:#bucla infinita din care iese atunci cand este setat flag-ul stopFlag din componenta Main.
                with self.lockStop:
                    if self.stopFlag:#atunci cand acest flag este setat se termina executia acestui 
                        #fir de executie, accesul la aceasta variabila se face folosind un mecanism de sincronizare
                        print("AcquisitonAndObjectDetect thread closed.")
                        exit()
                if not self.queueImageToHOI.full():# daca coada nu este plina se achizitioneaza imagini, se detecteaza obiectele si se adauga in coada.
                    image = self.acq.getFrame()
                    image_resized, detections = self.od.getDetections(image)
                    if not self.queueImageToHOI.full():
                        self.queueImageToHOI.put((self.cntFrame, image_resized, detections))
                        self.cntFrame += 1
        except Exception as e:
	        print("AcqAndObjectDetection "+str(e))
    def stop(self):# functia care este apelata pentru terminarea executiei
        with self.lockStop:
            self.stopFlag = True
