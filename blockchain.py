def display_blockchain():
    for block in blockchain:
        print(block)


def get_last_blockchain_value():
    if len(blockchain) == 0:
        return None
    return blockchain[-1]


def add_value(sender, recipient, amount=1.0):
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
    pass


def get_transaction_input():
    tx_recipient = input('Enter the Recipient of the Transacation: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return (tx_recipient, tx_amount)


def get_menu_input():
    print('1. Add block to Blockchain ')
    print('2. Display the Blockchain')
    print('3. Manipulate the block ')
    print('4. Exit the Loop ')
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
            add_value(
                last_transaction=get_last_blockchain_value(),
                transaction_amount=get_transaction_input()
            )

        elif choice == 2:
            display_blockchain()
        elif choice == 3:
            if len(blockchain) >= 1:
                blockchain[0] = ['Manipulated Data']

        elif choice == 4:
            break
        else:
            print('Invalid Input!')
        if not verify_chain_integrity():
            print('Block chain has been compromised .... x x x x ')
            break

    print('Done :) ')
    return 0


blockchain = []
open_transactions = []
tx_owner = 'Bisu Baby'
main()
