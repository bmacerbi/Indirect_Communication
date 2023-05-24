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
        self.transactions[0] = {'challenge': random.randint(1, 6), 'solution': None, 'winner': -1}

    def on_connect(self, client, userdata, flags, rc):
        controllerFile.write("Conectado ao broker MQTT\n")
        self.controller_client.subscribe("sd/solution")  

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        transactionId = data["TransactionID"]
        solution = data["Solution"]

        if topic == "sd/solution":
            if self.__validSolution(transactionId, solution):
                self.transactions[transactionId]['winner'] = data["ClientID"]
                self.transactions[transactionId]['solution'] = data["Solution"]

                result_payload = json.dumps({
                    "ClientID": data["ClientID"],
                    "TransactionID": transactionId, 
                    "Solution": data["Solution"],
                    "Result": 1})
                self.controller_client.publish("sd/result", result_payload)

            else:
                result_payload = json.dumps({
                    "ClientID": data["ClientID"],
                    "TransactionID": transactionId, 
                    "Solution": data["Solution"],
                    "Result": 0})
                self.controller_client.publish("sd/result", result_payload)
    
    def __validSolution(self, transactionId, solution):
        if(transactionId > max(self.transactions.keys())):
            return False

        hash = hashlib.sha1(solution.encode('utf-8')).digest()
        binary_hash = bin(int.from_bytes(hash, byteorder='big'))[2:]

        if binary_hash[1:self.transactions[transactionId]['challenge']+1] == '0' * self.transactions[transactionId]['challenge']:
            return True

        return False

    def __newChallenge(self):
        newTransactionId = max(self.transactions.keys())
        self.transactions[newTransactionId] = {
            'challenge': random.randint(1, 6), 
            'solution': None, 
            'winner': -1
            }
        self.controller_client.publish("sd/challenge", json.dumps(self.transactions[newTransactionId]))
        self.__printTransations()

        while self.transactions[newTransactionId]['winner'] == -1:
            continue
    
    def __printTransations(self):
        controllerFile.write("Transactions Table\n")
        for transaction in self.transactions:
            controllerFile.write(f"Challenge: {self.transactions[transaction]['challenge']} / Soluction; {self.transactions[transaction]['solution']} / Winner: {self.transactions[transaction]['winner']}\n")
        controllerFile.write("-------------------------------------------\n\n")

    def runController(self):
        self.controller_client.on_message = self.on_message
        self.controller_client.on_connect = self.on_connect

        self.controller_client.connect(broker_adress)

        self.controller_client.loop_start()

        try:
            self.__newChallenge()
                
        except KeyboardInterrupt:
            self.controller_client.loop_stop()
            self.controller_client.disconnect()
            controllerFile.write("Servidor MQTT desconectado\n")
    
class Miner():
    print()

def startController():
    controller = Controller()
    controller.runController()

def startMiner():
    miner = Miner()
    print()

if __name__ == '__main__':
    global controllerFile
    global minerFile
    controllerFile = open('ControllerOutPut', 'w')
    minerFile = open('MinerOutPut', 'w')

    controller = Controller()
    controller.runController()

    # try:
    #     qtd_cients = sys.argv[1]
    # except IndexError:
    #     print("Argumentos inválios, informe a quantidade de clients.") 
    
    # controller_id = random.randint(0, qtd_cients-1)

    # for client_id in range(len(qtd_cients)):
    #     if controller_id == client_id:
    #         controller_thread = threading.Thread(target = startController)
    #         controller_thread.start()
    #     else:
    #         miner_thread = threading.Thread(target = startMiner)
    #         miner_thread.start()