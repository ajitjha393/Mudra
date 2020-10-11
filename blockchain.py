# Global Variables and DS used in our Project

genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}

blockchain = [genesis_block]
open_transactions = []
tx_owner = 'Bisu Baby'
participants = {tx_owner}


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_balance(participant):
    # tx_sender stores amount from transactions where sender => participant

    tx_sender = [
        [
            tx['amount']
            for tx in block['transactions'] if tx['sender'] == participant
        ]
        for block in blockchain
    ]

    amount_sent = 0
    for tx in tx_sender:
        for amount in tx:
            amount_sent += amount

    tx_recipient = [
        [
            tx['amount']
            for tx in block['transactions'] if tx['recipient'] == participant
        ]
        for block in blockchain
    ]

    amount_recieved = 0
    for tx in tx_recipient:
        for amount in tx:
            amount_recieved += amount

    return amount_recieved - amount_sent


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
    new_transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }

    open_transactions.append(new_transaction)
    participants.add(sender)
    participants.add(recipient)


def mine_block():
    last_block = blockchain[-1]
    # Will change hash later
    hashed_block = hash_block(last_block)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }

    blockchain.append(block)
    return True


def get_transaction_input():
    tx_recipient = input('Enter the Recipient of the Transacation: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return (tx_recipient, tx_amount)


def get_menu_input():
    print('1. Add block to Blockchain ')
    print('2. Mine a new block ')
    print('3. Display the Blockchain')
    print('4. Manipulate the block ')
    print('5. Display the Participants')
    print('6. Exit the Loop ')
    return int(input('Enter a choice : '))


def verify_chain_integrity():
    '''
    Verify the hash value of each block and verifies it Integrity

    @return -> Boolean
    '''
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False

    return True


def main():

    while True:
        global open_transactions
        choice = get_menu_input()
        if choice == 1:
            tx_recipient, tx_amount = get_transaction_input()
            add_transaction(recipient=tx_recipient, amount=tx_amount)
            print(open_transactions)

        elif choice == 2:
            if mine_block():
                open_transactions = []
        elif choice == 3:
            display_blockchain()
        elif choice == 4:
            if len(blockchain) >= 1:
                blockchain[0] = {
                    'previous_hash': '',
                    'index': 0,
                    'transactions': [{'sender': 'PnB', 'recipient': 'Nirav Modi', 'amount': 11}]
                }

        elif choice == 5:
            display_participants()
        elif choice == 6:
            break
        else:
            print('Invalid Input!')
        if not verify_chain_integrity():
            print('Block chain has been compromised .... x x x x ')
            break
        print(get_balance(tx_owner))

    print('Done :) ')
    return 0


main()
