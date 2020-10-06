def display_blockchain():
    for block in blockchain:
        print(block)


def get_last_blockchain_value():
    if len(blockchain) == 0:
        return None
    return blockchain[-1]


def add_value(transaction_amount, last_transaction):
    if get_last_blockchain_value() == None:
        last_transaction = [0.0]
    blockchain.append([last_transaction, transaction_amount])


def get_transaction_amount():
    return float(input('Enter your transaction amount: '))


def get_menu_input():
    print('1. Add block to Blockchain ')
    print('2. Display the Blockchain')
    print('3. Manipulate the block ')
    print('4. Exit the Loop ')
    return int(input('Enter a choice : '))


def main():

    while True:
        choice = get_menu_input()
        if choice == 1:
            add_value(
                last_transaction=get_last_blockchain_value(),
                transaction_amount=get_transaction_amount()
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

    print('Done :) ')
    return 0


blockchain = []
main()
