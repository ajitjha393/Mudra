# Global Variables and DS used in our Project

from functools import reduce
from collections import OrderedDict
import hashlib
import json
import requests

from utility.hash_util import hash_block
from utility.verification import Verification

from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10.0


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.__chain = [genesis_block]
        self.public_key = public_key
        self.node_id = node_id

        self.__open_transactions = []
        self.__peer_nodes = set()
        self.load_data()

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):

        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                self.__chain = json.loads(file_content[0][:-1])
                updated_blockchain = []

                for block in self.__chain:
                    converted_tx = [
                        Transaction(
                            tx['sender'], tx['recipient'], tx['signature'], tx['amount']
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

                self.__chain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1])

                updated_open_transactions = [
                    Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']
                    )
                    for tx in open_transactions
                ]

                self.__open_transactions = updated_open_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)


        except (IOError, IndexError):
            print('Handling exception...')
            pass
        finally:
            print('cleanup work...')

    def save_data(self):
        try:

            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
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
                        ) for block_el in self.__chain
                    ]
                ]

                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
            return True

        except IOError:
            print('Saving Failed!')
            return False

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        Nonce = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, Nonce):
            Nonce += 1
        return Nonce

    def get_balance(self, sender=None):
        # tx_sender stores amount from transactions where sender => participant

        if sender == None:
            if self.public_key == None:
                return None
            participant = self.public_key
        else:
            participant = sender
        
        tx_sender = [
            [
                tx.amount
                for tx in block.transactions if tx.sender == participant
            ]
            for block in self.__chain
        ]

        open_tx_sender = [
            tx.amount
            for tx in self.__open_transactions if tx.sender == participant
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
            for block in self.__chain
        ]

        amount_recieved = reduce(
            lambda tx_sum, tx_amount_xs: tx_sum + sum(tx_amount_xs),
            tx_recipient,
            0)
        return amount_recieved - amount_sent

    def get_last_blockchain_value(self):
        if len(self.__chain) == 0:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender,signature, amount=1.0, is_receiving=False):
        ''' 
            Add new transaction to the open transaction list

            Arguments:

            :sender -> str | Info about sender of coins \n
            :recipient -> str | Info about recipient of coins \n
            :signature -> str | Signature of the tx \n
            :amount -> float | Transaction amount

        '''
        if self.public_key == None:
            return False

        new_transaction = Transaction(sender, recipient, signature, amount)
        

        if Verification.verify_transaction(new_transaction, self.get_balance):
            self.__open_transactions.append(new_transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url,json={
                                'sender': sender,
                                'recipient': recipient,
                                'amount': amount,
                                'signature': signature
                            })
                        
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction Declined, needs Resolving!')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue        
            return True
        return False

    def mine_block(self):

        if self.public_key == None:
            return None
            
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        reward_tx = Transaction('MINING', self.public_key, '',  MINING_REWARD)

        copied_open_transactions = self.__open_transactions[:]

        for tx in copied_open_transactions:
            if not Wallet.verify_tx_signature(tx):
                return None


        copied_open_transactions.append(reward_tx)

        block = Block(
            len(self.__chain),
            hashed_block,
            copied_open_transactions,
            proof
        )

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

        converted_block = block.__dict__.copy()
        converted_tx = [tx.__dict__ for tx in converted_block['transactions']]
        converted_block['transactions'] = converted_tx

        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            try:
                response = requests.post(url,json={
                    'block': converted_block
                })
                if response.status_code == 400 or response.status_code == 500:
                    print('Block Declined, needs Resolving!')

            except requests.exceptions.ConnectionError:
                continue
        
        return block


    def add_block(self, block):
        '''
        Adding a new block to the chain for consistency
        '''
        transactions = [
                Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                for tx in block['transactions']
            ]        

        proof_is_valid = Verification.valid_proof(transactions, block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.__chain[-1]) == block['previous_hash']

        if not proof_is_valid or not hashes_match:
            return False

        converted_block = Block(
            block['index'],
            block['previous_hash'],
            transactions,
            block['proof'],
            block['timestamp']
        )    
        
        self.__chain.append(converted_block)
        self.save_data()
        return True




    def add_peer_node(self, node):
        '''
        Add a new node to the Peer node set\n
        :node -> str | The node Url which should be added
        '''
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        '''
        Removes the node from the Peer node set\n
        :node -> str | The node Url which should be removed
        '''
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        '''Returns a copy of all peer nodes \n'''
        
        return list(self.__peer_nodes)
