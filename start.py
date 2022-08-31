from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths

from ult.config import cfg
from AcquisitionAndObjectDetect import AcqOD
from HOIDetector import HOIDetector
from Stream import Stream
from MQTTConnection import MQTTConnection
from networks.iCAN_ResNet50_VCOCO import ResNet50
import tensorflow as tf
import argparse

import queue
import signal, os
import paho.mqtt.client as mqtt


#functie care paseaza argumentele date la pornire, ce clasa sa se foloseasca pentru achizitie
#lungimea cozii in care sunt puse imaginile si detectiile
#numarul de fire de executie care vor detecta interactiunile
#daca sa se afiseze sau nu video activitatile

def parse_args():
    parser = argparse.ArgumentParser(description='Video Monitoring')
    parser.add_argument('--acquisition', dest='acquisition',
            help='Zed or Normal',
            default='Zed', type=str)
    parser.add_argument('--queueLength', dest='queueLength',
            help='length of queues',
            default=1, type=int)
    parser.add_argument('--numberHOIDetectors', dest='hoiDetectors',
            help='Number of threads for hoiDetector [1 or 2]',
            default=1, type=int)
    parser.add_argument('--showVideo', dest='showVideo',
            help='\'y\',for yes and \'n\' for no',
            default='y', type=str)
    args = parser.parse_args()
    return args

#vectorul in care vor fi salvate firele de executie
threads = []

#s-a definit o functie care va trata intreruperea
#aceasta va opri firele de executie care ruleaza
def handlerInt(sig, frame):
	for thread in threads:
		thread.stop();
	print("Principal component closed.")
	exit()
		
signal.signal(signal.SIGINT, handlerInt)


#se numara cadrele de la 1
cntFrame = 1
if __name__=="__main__":
    args = parse_args()
        

    queueImageToHOI = queue.PriorityQueue(args.queueLength)
    queueHOIToMain = queue.PriorityQueue(args.queueLength)

    weight = cfg.ROOT_DIR + '/Weights/iCAN_ResNet50_VCOCO/HOI_iter_' + str(300000) + '.ckpt'

    # se initializeaza sesiunea tensorflow
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth=True
    sess = tf.Session(config=tfconfig)

	#se incarca reteaua ResNet50, folosita pentru detectia interactiunilor
    network = ResNet50()
    network.create_architecture(False)

    #se utilizeaza ponderi deja antrenate
    saver = tf.train.Saver()
    saver.restore(sess, weight)

    print('Pre-trained weights loaded.')

    i = 0
    #daca se doresc doua fire de executie pentru detectia interactiunilor se imparte
    #memoria placii video fizice in doua pentru a obtine doua placi grafice logice
    if args.hoiDetectors > 1:
        #acest cod este preluat din documentatia TensorFlow
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
	        try:
		        tf.config.experimental.set_virtual_device_configuration(
			        gpus[0],
			        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=3072),
			         tf.config.experimental.VirtualDeviceConfiguration(memory_limit=3072)])
		        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
		        
		        for gpu in logical_gpus:
                    #se ruleaza firul de executie folosind memoria placii video logice
			        with tf.device(gpu.name):
				        threads.append(HOIDetector(i, queueImageToHOI, queueHOIToMain, network, sess))
				        threads[i].start()
				        i += 1
	        except RuntimeError as e:
		        print("Main "+str(e))
    else:
        #alfel se creaza doar un fir de executie
        threads.append(HOIDetector(i, queueImageToHOI, queueHOIToMain, network, sess))
        threads[i].start()
        i+=1
    #se initializeaza firele de executie pentru achizita si detectia obiectelor, respectiv pentru comunicarea
    #prin MQTT cu gateway-ul SMARTCARE
    threads.append(AcqOD(i, queueImageToHOI, args.acquisition))
    threads[i].start()
    i+=1
    threads.append(MQTTConnection(i))
    threads[i].start()
    #se instantiaza clasa care seteaza activitatea curenta si care afiseaza video activitatile, daca se doreste acest lucru
    stream = Stream(threads[i], args.showVideo)
    try:
        while True:
            #atunci cand in coada sunt imagini cu activitatile detectate, se scoate din coada si se afiseaza
	        imageHOIDetection = queueHOIToMain.get()
	        stream.showFrame(imageHOIDetection[1], imageHOIDetection[2])
    except Exception as e:
        print("Main " +str(e))
