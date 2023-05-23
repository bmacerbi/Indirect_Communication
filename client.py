import sys
import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
import pybreaker
import threading
import aux
import random


class Miner():
    def __init__(self):
        self.transactions = {}
        self.transactions[0] = {'challenge': None, 'solution': None, 'winner': None}
    
if __name__ == "__main__":
    print()
