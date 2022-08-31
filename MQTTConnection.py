import paho.mqtt.client as mqtt
import json
import threading
import time

class MQTTConnection(threading.Thread):
    def __init__(self, threadID):
	    threading.Thread.__init__(self)
	    self.threadID = threadID
	    self.stopFlag = False
	    self.clientMqtt = mqtt.Client()
	    self.lockActivity = threading.Lock()
	    self.lockStop = threading.Lock()
	    self.asyncActivitySend = False
	    self.currentActivity = {}

	    self.registerData = {
		    "bridge-type":"mod-bus",
		    "internal-id":"0x00000001",
		    "bridge-id":"video-monit",
		    "device-no":"1",
		    "devices":{
			    "1":{
				    "device-type":"Video monitoring",
				    "device-name":"Monitoring system for assisted living",
				    "manufacturer-id":"135-1101-000",
				    "manufacturer":"NVIDIA",
				    "resources":{
					    "activity":{
						    "type":"read-write",
						    "capabilities":["get", "async-get"],
						    "comment":"Activity performed by the supervised person."
					    }
				    }
			    }
		    }
		    
	    }
	    
	#se apeleaza la conectare, se aboneaza la topicurile necesare descrise in documentatie
    def on_connect(self, client, userdata, flags, rc): 
	    print("S-a conectat la gateway, cod raspuns {0}".format(str(rc))) 
	    client.subscribe("gateway/discover", 0)
	    client.subscribe("video-monit/1/activity/get", 0)
	    client.subscribe("video-monit/1/activity/async-get", 0)

	#se apeleaza la primirea unui mesaj pe unul din topicurile la care suntem abonati
    def on_message(self, client, userdata, message):
		#in functie de topicul pe care s-a primit mesaj si de mesajul primit
	    try:
		    data = json.loads(message.payload)
			#daca se doreste descoperirea dispozitivului este trimis pe register obiectul cu date despre el
		    if message.topic == "gateway/discover":
			    self.clientMqtt.publish("gateway/register", json.dumps(self.registerData))
			#daca s-a primit mesajul {"operation":"inquire"} pe get, se trimite activitatea pe response-get
		    if message.topic == "video-monit/1/activity/get":
			    if data["operation"] == "inquire":
				    with self.lockActivity:
				        self.clientMqtt.publish("video-monit/1/activity/response-get", json.dumps(self.currentActivity))
			#daca pe toopicul async-get s-a primit mesajul {"operation":"on"} este setat un flag pe true ca in buncla din 
			#run() sa se trimita activitatea curenta odata la o secunda.
			#daca se primeste {"operation":"off"} flagul este setat pe false pentru a nu mai trimite activitatea
		    if message.topic == "video-monit/1/activity/async-get":
			    if data["operation"] == "on":
				    self.asyncActivitySend = True
			    else:
				    self.asyncActivitySend = False
	    except Exception as e:
		    print(e)


    def on_subscribe(self, client, userdata, mid, granted_qos):
	    print(mid)
	    
    def setActivity(self, activity):
        with self.lockActivity:
	        self.currentActivity = activity			
	    

    def run(self):
        try:
            self.clientMqtt.on_connect = self.on_connect 
            self.clientMqtt.on_message = self.on_message
            self.clientMqtt.on_subscribe = self.on_subscribe
			#se conecteaza la agentul mqtt si se inregistreaza cu obiectul json definit in constructor
            self.clientMqtt.connect("8.tcp.ngrok.io", 18122, 60)
            self.clientMqtt.publish("gateway/register", json.dumps(self.registerData))
            self.clientMqtt.loop_start()	
        except Exception as e:
            print("MQTT " + str(e))

        try:
            while True:#bucla infinita din care iese atunci cand este setat flag-ul stopFlag din componenta Main.
                with self.lockStop:
                    if self.stopFlag:#atunci cand acest flag este setat se termina executia acestui 
                        #fir de executie, accesul la aceasta variabila se face folosind un mecanism de sincronizare
                        print("MQTT connection closed.")
                        exit()
                time.sleep(1)
				#daca este setat flag-ul, atunci se trimite asincron activitatea curenta catre gateway
                if self.asyncActivitySend:
                    self.clientMqtt.publish("video-monit/1/activity/response-async-get", json.dumps(self.currentActivity))
          
        except KeyboardInterrupt:
	        print("MQTT connection closed.")
	        client.disconnect()
	        client.loopstopFlag()
		    
    def stop(self):# functia care este apelata pentru terminarea executiei
        with self.lockStop:
            self.stopFlag = True
		    
							
