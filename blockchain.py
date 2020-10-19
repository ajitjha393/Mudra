# Global Variables and DS used in our Project

from functools import reduce
from collections import OrderedDict
import hashlib
import json

from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction


MINING_REWARD = 10.0

blockchain = []
open_transactions = []
tx_owner = 'Bisu Baby'
participants = {tx_owner}


def load_data():
    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt', mode='r') as f:
            file_content = f.readlines()
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []

            for block in blockchain:
                # converted_tx = [
                #     OrderedDict(
                #         [
                #             ('sender', tx['sender']),
                #             ('recipient', tx['recipient']),
                #             ('amount', tx['amount'])
                #         ]
                #     ) for tx in block['transactions']
                # ]

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

            blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])
            # updated_open_transactions = [
            #     OrderedDict(
            #         [
            #             ('sender', tx['sender']),
            #             ('recipient', tx['recipient']),
            #             ('amount', tx['amount'])
            #         ]
            #     ) for tx in open_transactions
            # ]

            updated_open_transactions = [
                Transaction(
                    tx['sender'], tx['recipient'], tx['amount']
                )
                for tx in open_transactions
            ]

            open_transactions = updated_open_transactions

    except (IOError, IndexError):
        print('File does not exist...')

        genesis_block = Block(0, '', [], 100, 0)

        blockchain = [genesis_block]
        open_transactions = []

    finally:
        print('cleanup work...')


load_data()


def save_data():
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
                    ) for block_el in blockchain
                ]
            ]

            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))
        return True

    except IOError:
        print('Saving Failed!')
        return False


def valid_proof(transactions, last_hash, proof):
    guess = (
        str(
            [tx.to_ordered_dict() for tx in transactions]
        )
        + str(last_hash)
        + str(proof)
    ).encode()

    guess_hash = hash_string_256(guess)
    # print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    Nonce = 0
    while not valid_proof(open_transactions, last_hash, Nonce):
        Nonce += 1
    return Nonce


def get_balance(participant):
    # tx_sender stores amount from transactions where sender => participant

    tx_sender = [
        [
            tx.amount
            for tx in block.transactions if tx.sender == participant
        ]
        for block in blockchain
    ]

    open_tx_sender = [
        tx.amount
        for tx in open_transactions if tx.sender == participant
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
        for block in blockchain
    ]

    amount_recieved = reduce(
        lambda tx_sum, tx_amount_xs: tx_sum + sum(tx_amount_xs),
        tx_recipient,
        0)
    return amount_recieved - amount_sent


def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def display_blockchain():
    for block in blockchain:
        print(block)


def display_participants():
    print(participants)


def get_last_blockchain_value():
    if len(blockchain) == 0:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=tx_owner, amount=1.0):
    ''' 
        Add new transaction to the open transaction list

        Arguments:

        :sender -> str | Info about sender of coins \n
        :recipient -> str | Info about recipient of coins \n
        :amount -> float | Transaction amount

    '''

    new_transaction = Transaction(sender, recipient, amount)

    # new_transaction = OrderedDict([
    #     ('sender', sender),
    #     ('recipient', recipient),
    #     ('amount', amount)]
    # )

    if verify_transaction(new_transaction):
        open_transactions.append(new_transaction)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    # Will change hash later
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_tx = {
    #     'sender': 'MINING',
    #     'recipient': tx_owner,
    #     'amount': MINING_REWARD
    # }

    # reward_tx = OrderedDict([
    #     ('sender', 'MINING'),
    #     ('recipient', tx_owner),
    #     ('amount', MINING_REWARD)
    # ])

    reward_tx = Transaction('MINING', tx_owner, MINING_REWARD)

    copied_open_transactions = open_transactions[:]

    copied_open_transactions.append(reward_tx)

    block = Block(
        len(blockchain),
        hashed_block,
        copied_open_transactions,
        proof
    )

    blockchain.append(block)
    return True


def get_transaction_input():
    tx_recipient = input('Enter the Recipient of the Transacation: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return (tx_recipient, tx_amount)


def get_menu_input():
    print('1. Add a new transaction ')
    print('2. Mine a new block ')
    print('3. Display the Blockchain')
    print('5. Display the Participants')
    print('6. Check for validity of Transactions')
    print('7. Exit the Loop ')
    return int(input('Enter a choice : '))


def verify_chain_integrity():
    '''
    Verify the hash value of each block and verifies it Integrity

    @return -> Boolean
    '''
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Invalid Proof of work')
            return False

    return True


# A standalone utility fn for verifying open_transactions
def verify_transactions():

    # one liner using any / all
    return all([verify_transaction(tx) for tx in open_transactions])

    # for tx in open_transactions:
    #     if not verify_transaction(tx):
    #         return False
    # return True


def main():

    while True:
        global open_transactions
        choice = get_menu_input()
        if choice == 1:
            tx_recipient, tx_amount = get_transaction_input()
            if add_transaction(recipient=tx_recipient, amount=tx_amount):
                print('Added Transaction')
            else:
                print('Transaction Failed!')

        elif choice == 2:
            if mine_block():
                open_transactions = []
                save_data()
        elif choice == 3:
            display_blockchain()

        elif choice == 5:
            display_participants()

        elif choice == 6:
            if verify_transactions():
                print('All transactions are valid!')
            else:
                print('Invalid Tx present!')
        elif choice == 7:
            break
        else:
            print('Invalid Input!')
        if not verify_chain_integrity():
            print('Block chain has been compromised .... x x x x ')
            break
        print(f'Balance of {tx_owner} = {get_balance(tx_owner):.2f}')

    print('Done :) ')
    return 0


main()
