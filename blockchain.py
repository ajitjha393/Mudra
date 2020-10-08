genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}

blockchain = [genesis_block]
open_transactions = []
tx_owner = 'Bisu Baby'


def display_blockchain():
    for block in blockchain:
        print(block)


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


def mine_block():
    last_block = blockchain[-1]
    # Will change hash later
    hashed_block = ''
    for key in last_block:
        value = last_block[key]
        hashed_block += str(value)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }

    blockchain.append(block)
    print(blockchain)


def get_transaction_input():
    tx_recipient = input('Enter the Recipient of the Transacation: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return (tx_recipient, tx_amount)


def get_menu_input():
    print('1. Add block to Blockchain ')
    print('2. Mine a new block ')
    print('3. Display the Blockchain')
    print('4. Manipulate the block ')
    print('5. Exit the Loop ')
    return int(input('Enter a choice : '))


def verify_chain_integrity():

    for block_index in range(1, len(blockchain)):
        if blockchain[block_index][0] != blockchain[block_index - 1]:
            return False

    return True


def main():

    while True:
        choice = get_menu_input()
        if choice == 1:
            tx_recipient, tx_amount = get_transaction_input()
            add_transaction(recipient=tx_recipient, amount=tx_amount)
            print(open_transactions)

        elif choice == 2:
            mine_block()
        elif choice == 3:
            display_blockchain()
        elif choice == 4:
            if len(blockchain) >= 1:
                blockchain[0] = ['Manipulated Data']

        elif choice == 5:
            break
        else:
            print('Invalid Input!')
        # if not verify_chain_integrity():
        #     print('Block chain has been compromised .... x x x x ')
        #     break

    print('Done :) ')
    return 0


main()
