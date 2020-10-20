"""
Module for Dumping Blockchain Data in Json and hashing using sha256 Algo
"""


import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    '''
    Hashing of block using sha256 algorithm
    '''
    hashable_block = block.__dict__.copy()
    updated_txs = [
        tx.to_ordered_dict()
        for tx in hashable_block['transactions']
    ]

    hashable_block['transactions'] = updated_txs

    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
