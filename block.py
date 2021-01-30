import time
from utility.printable import Printable


class Block(Printable):
    def __init__(self, index, previous_hash, transactions, proof, time=time.strftime('%Y-%m-%d %H:%M:%S')):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof

