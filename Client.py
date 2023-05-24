import random
import json
import time
import paho.mqtt.client as mqtt 

class Client():
    def __init__(self, broker_adress, min_clients):
        self.mqtt_client = mqtt.Client()
        self.broker_adress = broker_adress

        self.id = random.randint(0, 65335)
        self.min_clients = min_clients
        self.clients_list = []
        self.clients_list.append(self.id)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Client {self.id} conectado ao broker MQTT")
        self.mqtt_client.subscribe("sd/init")
        self.mqtt_client.subscribe("sd/voting")

        self.mqtt_client.publish("sd/init", json.dumps({"ClientID": self.id}))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        print(self.clients_list)
        if topic == "sd/init":
            print(self.clients_list)
            self.clients_list.append(int(data['ClientID']))

            if self.min_clients == len(self.clients_list):
                print(self.clients_list)
                self.__vote()

        elif topic == "sd/voting":
            print(f"{data['ClientID']} / {data['VoteID']}")

    def __vote(self):
        vote = random.randint(0, len(self.clients_list)-1)
        print(f"Client {self.id}: Votou em {vote}")
        vote_msg = {
            'ClientID': self.id,
            'VoteID': vote
        }
        self.mqtt_client.publish("sd/voting", json.dumps(vote_msg))

    def runClient(self):
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect

        self.mqtt_client.connect(self.broker_adress)
        self.mqtt_client.loop_start()

        while self.controller == -1:
            continue
