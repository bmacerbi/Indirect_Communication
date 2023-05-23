from concurrent import futures
import random
import threading
import paho.mqtt.client as mqtt 
import hashlib
import aux
import json
import sys

broker_adress = "127.0.0.1"

class Controller():
    def __init__(self):
        self.controller_client = mqtt.Client()
        self.transactions = {}
        self.transactions[0] = {}

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        transactionId = data["TransactionID"]
        self.transactions[transactionId]['winner'] = data["ClientID"]
        self.transactions[transactionId]['solution'] = data["Solution"]
    
    def newChallenge(self):
        topic = "sd/challenge"
        newTransactionId = max(self.transactions.keys())
        self.transactions[newTransactionId] = {
            'challenge': random.randint(1, 6), 
            'solution': None, 
            'winner': None
            }
        self.controller_client.publish(topic, json.dumps(self.transactions[newTransactionId]))
        self.__printTransations()

        while self.transactions[newTransactionId]['winner'] == None:
            continue
    
    def __printTransations(self):
        print("Transactions Table")
        for transaction in self.transactions:
            print(f"Challenge: {self.transactions[transaction]['challenge']} / Soluction; {self.transactions[transaction]['solution']} / Winner: {self.transactions[transaction]['winner']}")
        print("-------------------------------------------")

    def runController(self):
        self.controller_client.on_message = self.on_message
        self.controller_client.on_connect = self.on_connect

        self.controller_client.connect(broker_adress)

        self.controller_client.loop_start()

        try:
            self.newChallenge()
                
        except KeyboardInterrupt:
            self.controller_client.loop_stop()
            self.controller_client.disconnect()
            print("Servidor MQTT desconectado")


    # def submitChallenge(self, request, context):
    #     transactionId = request.transactionId
    #     if self._getLocalStatus(transactionId) == 0:
    #         return mine_grpc_pb2.intResult(result=(2))
    #     if self._getLocalStatus(transactionId) == -1:
    #         return mine_grpc_pb2.intResult(result=(-1))
        
    #     hash = hashlib.sha1(request.solution.encode('utf-8')).digest()
    #     binary_hash = bin(int.from_bytes(hash, byteorder='big'))[2:]

    #     if binary_hash[1:self.transactions[transactionId]['challenge']+1] == '0' * self.transactions[transactionId]['challenge']:
    #         self.transactions[transactionId]['winner'] = request.clientId
    #         self.transactions[transactionId]['solution'] = request.solution

    #         self.transactions[transactionId+1] = {'challenge': random.randint(1, 6), 'solution': None, 'winner': -1} # criando novo desafio
    #         return mine_grpc_pb2.intResult(result=(1))
    #     else:
    #         return mine_grpc_pb2.intResult(result=(0))
    
class Miner():
    print()

def startController():
    controller = Controller()
    controller.runController()

def startMiner():
    print()

if __name__ == '__main__':
    try:
        qtd_cients = sys.argv[1]
    except IndexError:
        print("Quantidade inválias de argumentos. Informe a quantidade de clients.") 
    
    controller_id = random.randint(0, qtd_cients-1)

    for client_id in range(len(qtd_cients)):
        if controller_id == client_id:
            controller_thread = threading.Thread(target = startController)
            controller_thread.start()
        else:
            miner_thread = threading.Thread(target = startMiner)
            miner_thread.start()