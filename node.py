class Node:

    def __init__(self):
        self.blockchain = []

    def get_transaction_input(self):
        tx_recipient = input('Enter the Recipient of the Transacation: ')
        tx_amount = float(input('Enter your transaction amount: '))
        return (tx_recipient, tx_amount)

    def get_menu_input(self):
        print('1. Add a new transaction ')
        print('2. Mine a new block ')
        print('3. Display the Blockchain')
        print('4. Check for validity of Transactions')
        print('5. Exit the Loop ')
        return int(input('Enter a choice : '))

    def display_blockchain(self):
        for block in self.blockchain:
            print('Outputting Block -> ')
            print(block)

    def listen_for_input(self):
        while True:
            global open_transactions
            choice = self.get_menu_input()
            if choice == 1:
                tx_recipient, tx_amount = self.get_transaction_input()
                if add_transaction(recipient=tx_recipient, amount=tx_amount):
                    print('Added Transaction')
                else:
                    print('Transaction Failed!')

            elif choice == 2:
                if mine_block():
                    open_transactions = []
                    save_data()
            elif choice == 3:
                self.display_blockchain()

            elif choice == 4:
                if Verification().verify_transactions(open_transactions, get_balance):
                    print('All transactions are valid!')
                else:
                    print('Invalid Tx present!')
            elif choice == 5:
                break
            else:
                print('Invalid Input!')
            if not Verification().verify_chain_integrity(blockchain):
                print('Block chain has been compromised .... x x x x ')
                break
            print(f'Balance of {tx_owner} = {get_balance(tx_owner):.2f}')

        print('Done :) ')
        return 0
