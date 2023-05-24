import random
import threading
import sys
import Controller
import Miner
import Client

broker_adress = "127.0.0.1"

def startController():
    controller = Controller.Controller(broker_adress)
    controller.runController()

def startMiner():
    miner = Miner.Miner(broker_adress, random.randint(0, 65335))
    miner.runMiner()

if __name__ == '__main__':
    try:
        qtd_cients = int(sys.argv[1])
    except IndexError:
        print("Argumentos inválios, informe a quantidade de clients.") 

    for client_id in range(qtd_cients):
        client = Client.Client(broker_adress, qtd_cients)
        thread = threading.Thread(target = client.runClient())
        thread.start()
    
    # controller_id = random.randint(0, qtd_cients-1)

    # thread_list = []
    # for client_id in range(qtd_cients):
    #     if controller_id == client_id:
    #         controller_thread = threading.Thread(target = startController)
    #         thread_list.append(controller_thread)
    #         controller_thread.start()
    #     else:
    #         miner_thread = threading.Thread(target = startMiner)
    #         thread_list.append(miner_thread)
    #         miner_thread.start()

    # for thread in thread_list:
    #     thread.join()