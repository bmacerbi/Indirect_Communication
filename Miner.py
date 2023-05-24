import random
import paho.mqtt.client as mqtt 
import hashlib
import json
import os
import string

class Miner():
    def __init__(self, broker_adress, id):
        self.miner_client = mqtt.Client()
        self.id = id
        self.broker_adress = broker_adress
        self.transactions = {}
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Client {self.id}: Conectado ao broker MQTT")
        self.miner_client.subscribe("sd/challenge")
        self.miner_client.subscribe(f"sd/{self.id}/result")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        if topic == "sd/challenge":
            print(f"Miner {self.id}: Desafio de dificuldade {data['challenge']} recebido, procurando uma resposta...")

            solution = self.__lookForAnswer(data['challenge'])
            if self.transactions.keys():
                transactionId = max(self.transactions.keys()) + 1
                self.transactions[transactionId] = {
                    'challenge': data['challenge'], 
                    'solution': None, 
                    'winner': -1
                    }
            else:
                self.transactions[0] = {'challenge': data['challenge'], 'solution': None, 'winner': -1}
                transactionId = 0

            solution_msg = {
                "ClientID": self.id,
                "TransactionID": transactionId,
                "Solution": solution
            }
            self.miner_client.publish("sd/solution", json.dumps(solution_msg))

        elif topic == f"sd/{self.id}/result":
            solution = data['Solution']
            if data['Result'] == 0:
                if solution == None:
                    print(f"Miner {self.id}: Solução ({solution}) Negada pelo Servidor!")
                else:
                    print(f"Miner {self.id}: O servidor já possui solução para o id {data['TransactionID']}! Solução: {solution} / Vencedor: {data['ClientID']}. Atualizando tabela local.")
                    self.transactions[data["TransactionID"]]['solution'] = solution
                    self.transactions[data["TransactionID"]]['winner'] = data['ClientID']
            else:
                print(f"Miner {self.id}: Solução ({solution}) Aceita pelo Servidor! Atualizando tabela local.")
                self.transactions[data["TransactionID"]]['solution'] = solution
                self.transactions[data["TransactionID"]]['winner'] = self.id

    def __lookForAnswer(self, challenger):
        count = 0
        while True:
            count += 1

            solution = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            hash = hashlib.sha1(solution.encode('utf-8')).digest()
            binary_hash = bin(int.from_bytes(hash, byteorder='big'))[2:]

            if binary_hash[1:challenger+1] == '0' * challenger:
                return solution

    def runMiner(self):
        self.miner_client.on_message = self.on_message
        self.miner_client.on_connect = self.on_connect

        self.miner_client.connect(self.broker_adress)
        self.miner_client.loop_start()