import threading
import sys
import Client


if __name__ == '__main__':
    try:
        qtd_cients = int(sys.argv[1])
        broker_adress = sys.argv[2]
    except IndexError:
        print("Argumentos inválidos. A linha de comando deve conter: <quantidade_clients> <broker_adress>") 

    for i in range(qtd_cients):
        client = Client.Client(broker_adress, qtd_cients)
        thread = threading.Thread(target = client.runClient)
        thread.start()