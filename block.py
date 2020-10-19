from time import time


class Block:
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time

    def __repr__(self):
        return 'Index : {}, Previous Hash : {}, Proof : {}, Transactions : {} '.format(
            self.index,
            self.previous_hash,
            self.proof,
            self.transactions
        )
