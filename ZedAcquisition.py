from __future__ import absolute_import
from __future__ import division
from __future__ import print_function



from IAcquisition import IAcquisition
import pyzed.sl as sl

#aceasta clasa implementeaza interfata IAcquisition 
#folosind mecanismele de achizitionare puse la dispozitie
#de StereoLabs prin modulul 'pyzed'.
class Acquisition(IAcquisition):
    def __init__(self):
        self.camera = sl.Camera()
        #sunt setati parametrii de achizitionare: rezolutia si numarul de cadre pe secunda
        self.initParams = sl.InitParameters()
        self.initParams.camera_resolution = sl.RESOLUTION.VGA
        self.initParams.camera_fps = 30
        err = self.camera.open(self.initParams)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)
        self.runtimeParameters = sl.RuntimeParameters()
      
    def getFrame(self):
        image = sl.Mat()
        if self.camera.grab(self.runtimeParameters) == sl.ERROR_CODE.SUCCESS:
            #se preia imaginea de pe camera stanga, in viitor se vor putea folosi amandoua
            #pentru a extrage imagini de profunzime
            self.camera.retrieve_image(image, sl.VIEW.LEFT)
            return image.get_data()
        return None
    def close(self):
        self.camera.close()
	    
