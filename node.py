from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)


CORS(app)


# BLOCKCHAIN ROUTES 

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot =  blockchain.get_chain()
    dict_chain =  [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
   
    return jsonify(dict_chain), 200


@app.route('/mine', methods=['POST'])
def mine_block():
    if blockchain.resolve_conflicts:
        response = {
            'message': 'Resolve conflicts first , block not added'
        }
        return jsonify(response), 409
    block = blockchain.mine_block()
    
    
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']
        ]

        return jsonify({
            'message': 'Block Added successfully...',
            'block' : dict_block,
            'funds': blockchain.get_balance()
        }),  201

    else:
        response =  {
            'message' : 'Mining of block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500



# RESOLVING CONFLICTS ROUTE

@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {
            'message': 'Chain was replaced!'
        }
    else:
        response = {
            'message': 'Local Chain was kept!'
        }    

    return jsonify(response), 200




# WALLET ROUTES

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched Balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message' : 'Loading balance failed!',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500  


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        #reinitializing blockchain with keys
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)

        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201    
    else:
        response = {
            'message' : 'Saving keys failed.'
        }
        return jsonify(response), 500


    
@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        #reinitializing blockchain with keys
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)

        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201    
    else:
        response = {
            'message' : 'Loading keys failed.'
        }
        return jsonify(response), 500



# BROADCASTING ROUTES

@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found...',
        }
        return jsonify(response), 400

    required_fields = ['sender', 'recipient', 'amount', 'signature']    

    if not all(key in values for key in required_fields):
        return jsonify ({
            'message': 'Required fields are missing.'
        }) , 400

    sender = values['sender']
    recipient = values['recipient']
    signature = values['signature']
    amount = values['amount']

    success = blockchain.add_transaction(recipient, sender, signature, amount,is_receiving=True)

    if success:
        response = {
            'message': 'Successfully added tx',
            'transaction': {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            }
        }

        return jsonify(response), 201

    else:
        response = {
            'message': 'Creating a Tx Failed.'
        }

        return jsonify(response), 500    


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found...',
        }
        return jsonify(response), 400

    if 'block' not in values:
        return jsonify ({
            'message': 'Required fields are missing.'
        }) , 400
    
    block = values['block']
    if block['index'] == blockchain.get_chain()[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                'message': 'Block Added'
            }

            return jsonify(response), 201
        else:
            response = {
                'message': 'Block Seems invalid!'
            }
            return jsonify(response), 409

        
    elif block['index'] > blockchain.get_chain()[-1].index:
        response = {
            'message': 'Blockchain seems to differ from local blockchain!'
        }
        blockchain.resolve_conflicts = True
        return jsonify(response), 200

    else:
        response = {
            'message': 'Blockchain seems to be shorter/stale, Block not added!'
        }
        return jsonify(response), 409 # Means outdated-invalid data
    




# TRANSACTION ROUTES

@app.route('/transaction', methods=['POST'])
def add_transaction():

    if wallet.public_key == None:
        return jsonify({
            'message': 'No wallet setup.'
        }), 400

    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found...',
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']

    if not all(field in values for field in required_fields) :
        return jsonify ({
            'message': 'Required fields are missing.'
        }) , 400

    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transactions(wallet.public_key, recipient, amount)  
    added_tx = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)  

    if added_tx:
        response = {
            'message': 'Successfully added tx',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201

    else:
        response = {
            'message': 'Creating a Tx Failed.'
        }

        return jsonify(response), 500    




@app.route('/transactions', methods=['GET'])
def get_open_txs():
    open_txs = blockchain.get_open_transactions()
    dict_open_txs = [tx.__dict__ for tx in open_txs]
    response = {
        'message': 'Fetched Transactions successfully',
        'transactions': dict_open_txs
    }
    return jsonify(response), 200




# UI VIEWS
@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('UI','node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('UI','network.html')


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached...',
        }
        return jsonify(response), 400

    if 'node' not in values:
        response = {
            'message': 'No node data found ...'
        }
        return jsonify(response), 400   

    node = values['node']     
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully!',
        'all_nodes': blockchain.get_peer_nodes()
    }

    return jsonify(response), 200 


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message' : 'No node Found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)

    response = {
        'message': 'Node Removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p','--port',type=int ,default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0',port=port)

