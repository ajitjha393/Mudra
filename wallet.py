from binascii import hexlify
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    def __init__(self, node_id):
        self.private_key , self.public_key =  None , None
        self.node_id = node_id

    def create_keys(self):
        private_key , public_key = self.generate_keys()
        self.private_key , self.public_key =  private_key , public_key
        
    def save_keys(self):
        if self.public_key and self.private_key:
            try:
                with open('wallet-{}.txt'.format(self.node_id),mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True

            except (IOError , IndexError):
                print('Saving Wallet Failed ...')
                return False


    def load_keys(self):
        try :
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key , self.private_key = public_key , private_key
            return True
        
        except(IOError, IndexError):
            print('Loading Wallet Failed...')
            return False

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()

        return (
            binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
            binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        )

    def sign_transactions(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount) ).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_tx_signature(transaction):  
        public_key =  RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier =  PKCS1_v1_5.new(public_key)
        h = SHA256.new(
            (str(transaction.sender) + str(transaction.recipient) + str(transaction.amount))
            .encode('utf8')
        )

        return verifier.verify(h, binascii.unhexlify(transaction.signature))
          