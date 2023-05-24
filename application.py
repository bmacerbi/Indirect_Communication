import random
import threading
import paho.mqtt.client as mqtt 
import hashlib
import aux
import json
import sys
import os

broker_adress = "127.0.0.1"


class Controller():
    def __init__(self):
        self.controller_client = mqtt.Client()
        self.transactions = {}

    def on_connect(self, client, userdata, flags, rc):
        print("Controller conectado ao broker MQTT")
        # controllerFile.write("Conectado ao broker MQTT\n")
        self.controller_client.subscribe("sd/solution")  

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        if topic == "sd/solution":
            transactionId = data["TransactionID"]
            solution = data["Solution"]

            if self.transactions[transactionId]['solution'] == None and self.__validSolution(transactionId, solution):
                print("\nSolução Encontrada!")

                result_payload = json.dumps({
                    "ClientID": data["ClientID"],
                    "TransactionID": transactionId, 
                    "Solution": data["Solution"],
                    "Result": 1})
                self.controller_client.publish(f"sd/{data['ClientID']}/result", result_payload)

                self.transactions[transactionId]['winner'] = data["ClientID"]
                self.transactions[transactionId]['solution'] = data["Solution"]
                self.__printTransations()

                print("Enviando resposta aos Mineradores...")
            else:
                result_payload = json.dumps({
                    "ClientID": self.transactions[transactionId]['winner'],
                    "TransactionID": transactionId, 
                    "Solution": self.transactions[transactionId]['solution'],
                    "Result": 0})
                self.controller_client.publish(f"sd/{data['ClientID']}/result", result_payload)
    
    def __validSolution(self, transactionId, solution):
        if(transactionId > max(self.transactions.keys())):
            return False

        hash = hashlib.sha1(solution.encode('utf-8')).digest()
        binary_hash = bin(int.from_bytes(hash, byteorder='big'))[2:]

        if binary_hash[1:self.transactions[transactionId]['challenge']+1] == '0' * self.transactions[transactionId]['challenge']:
            return True

        return False

    def __newChallenge(self):
        while input() != 'e':
            os.system("clear")
            if self.transactions.keys():
                newTransactionId = max(self.transactions.keys()) + 1
                self.transactions[newTransactionId] = {
                    'challenge': 20, 
                    'solution': None, 
                    'winner': -1
                    }
            else:
                self.transactions[0] = {'challenge': 20, 'solution': None, 'winner': -1}
                newTransactionId = 0

            self.controller_client.publish("sd/challenge", json.dumps(self.transactions[newTransactionId]))
            print("Gerando Novo Desafio!")
            self.__printTransations()

            while self.transactions[newTransactionId]['solution'] == None:
                continue
            
    def __printTransations(self):
        print("----------------------------------------------------")
        print("Transactions Table")
        # controllerFile.write("Transactions Table\n")
        for transaction in self.transactions:
            print(f"Challenge: {self.transactions[transaction]['challenge']} / Soluction; {self.transactions[transaction]['solution']} / Winner: {self.transactions[transaction]['winner']}")
            # controllerFile.write(f"Challenge: {self.transactions[transaction]['challenge']} / Soluction; {self.transactions[transaction]['solution']} / Winner: {self.transactions[transaction]['winner']}\n")
        # controllerFile.write("-------------------------------------------\n\n")
        print("----------------------------------------------------\n")

    def runController(self):
        self.controller_client.on_message = self.on_message
        self.controller_client.on_connect = self.on_connect

        self.controller_client.connect(broker_adress)
        self.controller_client.loop_start()

        try:
            print("Controller iniciado. Para sair digite 'e', para gerar novo desafio aperte enter...")
            self.__newChallenge()
                
        except KeyboardInterrupt:
            self.controller_client.loop_stop()
            self.controller_client.disconnect()
            print("Servidor MQTT desconectado")
            # controllerFile.write("Servidor MQTT desconectado\n")
            # controllerFile.close()
    
class Miner():
    def __init__(self):
        self.miner_client = mqtt.Client()
        self.id = random.randint(0, 65335)
        self.transactions = {}
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Client {self.id}: Conectado ao broker MQTT")
        # minerFile.write(f"Client {self.id}: Conectado ao broker MQTT\n")
        self.miner_client.subscribe("sd/challenge")
        self.miner_client.subscribe(f"sd/{self.id}/result")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        if topic == "sd/challenge":
            print(f"Miner {self.id}: Desafio de dificuldade {data['challenge']} recebido, procurando uma resposta...")
            # minerFile.write(f"Miner {self.id}: Desafio de dificuldade {data['challenge']} recebido, procurando uma resposta...\n")
            solution = aux.lookForAnswer(data['challenge'])
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
                    # minerFile.write(f"Miner {self.id}: Solução ({solution}) Negada pelo Servidor!\n\n")
                else:
                    print(f"Miner {self.id}: O servidor já possui solução para o id {data['TransactionID']}! Solução: {solution} / Vencedor: {data['ClientID']}. Atualizando tabela local.")
                    self.transactions[data["TransactionID"]]['solution'] = solution
                    self.transactions[data["TransactionID"]]['winner'] = data['ClientID']
            else:
                print(f"Miner {self.id}: Solução ({solution}) Aceita pelo Servidor! Atualizando tabela local.")
                # minerFile.write(f"Miner {self.id}: Solução ({solution}) Aceita pelo Servidor! Atualizando tabela.\n\n")
                self.transactions[data["TransactionID"]]['solution'] = solution
                self.transactions[data["TransactionID"]]['winner'] = self.id

    def runMiner(self):
        self.miner_client.on_message = self.on_message
        self.miner_client.on_connect = self.on_connect

        self.miner_client.connect(broker_adress)
        self.miner_client.loop_start()

        # try:
        #     while True:
        #         continue
        # except KeyboardInterrupt:
        #     self.miner_client.loop_stop()
        #     self.miner_client.disconnect()
        #     print("Minerador MQTT desconectado")
        #     # minerFile.write("Minerador MQTT desconectado\n")
        #     minerFile.close()

def startController():
    controller = Controller()
    controller.runController()

def startMiner():
    miner = Miner()
    miner.runMiner()

if __name__ == '__main__':
    # global controllerFile
    # global minerFile
    # controllerFile = open('ControllerOutPut', 'w')
    # minerFile = open('MinerOutPut', 'w')
    try:
        qtd_cients = int(sys.argv[1])
    except IndexError:
        print("Argumentos inválios, informe a quantidade de clients.") 
    
    controller_id = random.randint(0, qtd_cients-1)

    thread_list = []
    for client_id in range(qtd_cients):
        if controller_id == client_id:
            controller_thread = threading.Thread(target = startController)
            thread_list.append(controller_thread)
            controller_thread.start()
        else:
            miner_thread = threading.Thread(target = startMiner)
            thread_list.append(miner_thread)
            miner_thread.start()

    for thread in thread_list:
        thread.join()