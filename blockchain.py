# Global Variables and DS used in our Project

from functools import reduce
from collections import OrderedDict
import hashlib
import json

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10.0


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.hosting_node = hosting_node_id

        self.open_transactions = []
        self.load_data()

    def load_data(self):

        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                self.chain = json.loads(file_content[0][:-1])
                updated_blockchain = []

                for block in self.chain:
                    converted_tx = [
                        Transaction(
                            tx['sender'], tx['recipient'], tx['amount']
                        )
                        for tx in block['transactions']
                    ]

                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx, block['proof'],
                        block['timestamp']
                    )

                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1])

                updated_open_transactions = [
                    Transaction(
                        tx['sender'], tx['recipient'], tx['amount']
                    )
                    for tx in self.open_transactions
                ]

                self.open_transactions = updated_open_transactions

        except (IOError, IndexError):
            print('Handling exception...')
            pass
        finally:
            print('cleanup work...')

    def save_data(self):
        try:

            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [
                    block.__dict__
                    for block in [
                        Block(
                            block_el.index,
                            block_el.previous_hash,
                            [
                                tx.__dict__
                                for tx in block_el.transactions
                            ],
                            block_el.proof,
                            block_el.timestamp
                        ) for block_el in self.chain
                    ]
                ]

                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_tx))
            return True

        except IOError:
            print('Saving Failed!')
            return False

    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        Nonce = 0
        while not Verification().valid_proof(self.open_transactions, last_hash, Nonce):
            Nonce += 1
        return Nonce

    def get_balance(self):
        # tx_sender stores amount from transactions where sender => participant

        participant = self.hosting_node
        tx_sender = [
            [
                tx.amount
                for tx in block.transactions if tx.sender == participant
            ]
            for block in self.chain
        ]

        open_tx_sender = [
            tx.amount
            for tx in self.open_transactions if tx.sender == participant
        ]

        tx_sender.append(open_tx_sender)

        amount_sent = reduce(
            lambda tx_sum, tx_amount_xs: tx_sum + sum(tx_amount_xs),
            tx_sender,
            0)

        tx_recipient = [
            [
                tx.amount
                for tx in block.transactions if tx.recipient == participant
            ]
            for block in self.chain
        ]

        amount_recieved = reduce(
            lambda tx_sum, tx_amount_xs: tx_sum + sum(tx_amount_xs),
            tx_recipient,
            0)
        return amount_recieved - amount_sent

    def get_last_blockchain_value(self):
        if len(self.chain) == 0:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        ''' 
            Add new transaction to the open transaction list

            Arguments:

            :sender -> str | Info about sender of coins \n
            :recipient -> str | Info about recipient of coins \n
            :amount -> float | Transaction amount

        '''

        new_transaction = Transaction(sender, recipient, amount)

        if Verification().verify_transaction(new_transaction, self.get_balance):
            self.open_transactions.append(new_transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        reward_tx = Transaction('MINING', self.hosting_node, MINING_REWARD)

        copied_open_transactions = self.open_transactions[:]

        copied_open_transactions.append(reward_tx)

        block = Block(
            len(self.chain),
            hashed_block,
            copied_open_transactions,
            proof
        )

        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True
