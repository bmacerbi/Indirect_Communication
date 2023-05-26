import random
import threading
import sys
import Controller
import Miner
import Client

broker_adress = "127.0.0.1"

if __name__ == '__main__':
    try:
        qtd_cients = int(sys.argv[1])
    except IndexError:
        print("Argumentos inválios, informe a quantidade de clients.") 

    for i in range(qtd_cients):
        client = Client.Client(broker_adress, qtd_cients)
        thread = threading.Thread(target = client.runClient)
        thread.start()