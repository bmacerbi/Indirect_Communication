import random
import json
import time
import paho.mqtt.client as mqtt
import Controller
import Miner

class Client():
    def __init__(self, broker_adress, min_clients):
        self.id = random.randint(0, 65335)
        self.min_clients = min_clients
        self.clients_list = []
        self.clients_list.append(self.id)

        self.vote_table = {}
        self.controller_id = -1 
        
        self.mqtt_client = mqtt.Client(str(self.id))
        self.broker_adress = broker_adress

    def on_connect(self, client, userdata, flags, rc):
        print(f"Client {self.id} conectado ao broker MQTT")
        self.mqtt_client.subscribe("sd/init")
        self.mqtt_client.subscribe("sd/voting")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        client_id = data['ClientID']

        if topic == "sd/init" and client_id != self.id:
            self.clients_list.append(int(data['ClientID']))

            if self.min_clients == len(self.clients_list):
                self.__vote()

        elif topic == "sd/voting" and client_id != self.id:
            self.vote_table[client_id] = data['VoteID']

            if self.min_clients == len(self.vote_table):
                self.__countVote()

    def __vote(self):
        vote = random.randint(0, len(self.clients_list)-1)
        self.vote_table[self.id] = self.clients_list[vote]
        vote_msg = {
            'ClientID': self.id,
            'VoteID': self.clients_list[vote]
        }
        self.mqtt_client.publish("sd/voting", json.dumps(vote_msg))

    def __countVote(self):
        vote_counter = {}

        for client_id in self.vote_table:
            if self.vote_table[client_id] not in vote_counter:
                vote_counter[self.vote_table[client_id]] = 1
            else:
                vote_counter[self.vote_table[client_id]] += 1

        winner_votes = -1
        winner_id = -1
        for client in vote_counter:
            if vote_counter[client] > winner_votes:
                winner_votes = vote_counter[client]
                winner_id = client
            elif vote_counter[client] == winner_votes:
                if client > winner_id:
                    winner_id = client

        self.controller_id = winner_id
        print(f"Tabela de votos do client {self.id}: {self.vote_table} // Vencedor: {self.controller_id}")

    def startController(self):
        controller = Controller.Controller(self.broker_adress, self.mqtt_client)
        controller.runController()

    def startMiner(self):
        miner = Miner.Miner(self.broker_adress, self.id, self.mqtt_client)
        miner.runMiner()

    def runClient(self):
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect

        self.mqtt_client.connect(self.broker_adress)
        self.mqtt_client.loop_start()

        #esperando para que todos assinem as funções
        time.sleep(1)
        self.mqtt_client.publish("sd/init", json.dumps({"ClientID": self.id}))

        #esperando resultado da eleição
        while self.controller_id == -1:
            continue

        if self.id == self.controller_id:
            self.startController()
        else:
            self.startMiner()