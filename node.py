from blockchain import Blockchain
from uuid import uuid4
from utility.verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        # Will add public wallet key later
        self.id = 'Bisu_baby'
        self.blockchain = Blockchain(self.id)

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
        for block in self.blockchain.get_chain():
            print('Outputting Block -> ')
            print(block)

    def listen_for_input(self):
        while True:
            choice = self.get_menu_input()
            if choice == 1:
                tx_recipient, tx_amount = self.get_transaction_input()
                if self.blockchain.add_transaction(recipient=tx_recipient, sender=self.id, amount=tx_amount):
                    print('Added Transaction')
                else:
                    print('Transaction Failed!')
                print(self.blockchain.get_open_transactions())

            elif choice == 2:
                self.blockchain.mine_block()
            elif choice == 3:
                self.display_blockchain()

            elif choice == 4:
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid!')
                else:
                    print('Invalid Tx present!')
            elif choice == 5:
                break
            else:
                print('Invalid Input!')
            if not Verification.verify_chain_integrity(self.blockchain.get_chain()):
                print('Block chain has been compromised .... x x x x ')
                break
            print(
                f'Balance of {self.id} = {self.blockchain.get_balance():.2f}')

        print('Done :) ')
        return 0


if __name__ == '__main__':
    Node().listen_for_input()
