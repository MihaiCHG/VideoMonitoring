from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from IAcquisition import IAcquisition
import cv2
#aceasta clasa implementeaza interfata IAcquisition 
#folosind mecanismele de achizitionare a unei camere normale
class Acquisition(IAcquisition):
    def __init__(self):
        self.vid = cv2.VideoCapture(0)
      
    def getFrame(self):
        ret, image = self.vid.read()
        return image
    def close(self):
        self.vid.release()    
	
	    
