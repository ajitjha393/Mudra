"""
Provides Blockhain & Transactions Verification Helper Methods
"""

from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet


class Verification:

    @staticmethod
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

    @classmethod
    def verify_chain_integrity(cls, blockchain):
        '''
        Verify the hash value of each block and verifies it Integrity

        @return -> Boolean
        '''
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Invalid Proof of work')
                return False

        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        sender_balance = get_balance(transaction.sender)
        if check_funds:
            return sender_balance >= transaction.amount and Wallet.verify_tx_signature(transaction)
        else:
            return Wallet.verify_tx_signature(transaction)    

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        # one liner using any / all
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])
