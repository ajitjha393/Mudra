from flask import Flask, jsonify
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)

CORS(app)

@app.route('/', methods=['GET'])
def get_ui():
    return 'Hey, This server works!'


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot =  blockchain.get_chain()
    dict_chain =  [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
   
    return jsonify(dict_chain), 200


@app.route('/mine', methods=['POST'])
def mine_block():
    block = blockchain.mine_block()
    dict_block = block.__dict__.copy()
    dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    
    if block != None:
        return jsonify({
            'message': 'Block Added successfully...',
            'block' : dict_block
        }),  201

    else:
        response =  {
            'message' : 'Mining of block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

