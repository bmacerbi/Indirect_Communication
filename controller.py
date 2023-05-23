from concurrent import futures
import random
import paho.mqtt.client as mqtt 
import hashlib
import grpc
import threading
import aux

class Controller():
    def __init__(self):
        self.transactions = {}
        self.transactions[0] = {'challenge': random.randint(1, 6), 'solution': None, 'winner': -1}
    
    def runMenu(self):
        while True:
            print('Menu Options:')
            print('1 - newChallenge')
            print('2 - exitController')
            print()
            
            try:
                operation = int(input('Enter your choice: '))
            except ValueError:
                print("Invalid Operation!\n")
                continue

            if operation == 1:
                self.newChallenge()
            elif operation == 2:
                self.exitController()
            else:
                print("Invalid Operation!\n")

            input("Press Enter to continue...")


    def newChallenge(self):
        print()

    def exitController(self):
        print()

    def submitChallenge(self, request, context):
        transactionId = request.transactionId
        if self._getLocalStatus(transactionId) == 0:
            return mine_grpc_pb2.intResult(result=(2))
        if self._getLocalStatus(transactionId) == -1:
            return mine_grpc_pb2.intResult(result=(-1))
        
        hash = hashlib.sha1(request.solution.encode('utf-8')).digest()
        binary_hash = bin(int.from_bytes(hash, byteorder='big'))[2:]

        if binary_hash[1:self.transactions[transactionId]['challenge']+1] == '0' * self.transactions[transactionId]['challenge']:
            self.transactions[transactionId]['winner'] = request.clientId
            self.transactions[transactionId]['solution'] = request.solution

            self.transactions[transactionId+1] = {'challenge': random.randint(1, 6), 'solution': None, 'winner': -1} # criando novo desafio
            return mine_grpc_pb2.intResult(result=(1))
        else:
            return mine_grpc_pb2.intResult(result=(0))
    


if __name__ == '__main__':
    broker_adress = "127.0.0.1"
    controller_client = mqtt.Client("Controller")
    controller_client.connect(broker_adress) 

    controller = Controller()

    controller.runMenu()