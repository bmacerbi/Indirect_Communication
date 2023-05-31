import random
import hashlib
import json
import string

class Miner():
    def __init__(self, broker_adress, id, mqtt_client):
        self.mqq_miner = mqtt_client
        self.id = id
        self.broker_adress = broker_adress
        self.transactions = {}
    
    def on_connect(self, client, userdata, flags, rc):
        self.mqq_miner.subscribe("sd/challenge")
        self.mqq_miner.subscribe(f"sd/{self.id}/result")

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
                self.transactions[0] = {
                    'challenge': data['challenge'],
                    'solution': None,
                    'winner': -1
                    }
                
                transactionId = 0

            solution_msg = {
                "ClientID": self.id,
                "TransactionID": transactionId,
                "Solution": solution
            }

            self.mqq_miner.publish("sd/solution", json.dumps(solution_msg))

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
        self.mqq_miner.on_message = self.on_message
        self.mqq_miner.on_connect = self.on_connect

        self.mqq_miner.connect(self.broker_adress)
        self.mqq_miner.loop_start()