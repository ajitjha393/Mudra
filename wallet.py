from binascii import hexlify
from Crypto.PublicKey import RSA
import Crypto.Random
import binascii


class Wallet:
    def __init__(self):
        self.private_key , self.public_key =  None , None

    def create_keys(self):
        self.private_key , self.public_key =  self.generate_keys()

    def load_keys(self):
        pass

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publicKey()

        return (
            binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
            binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        )

print(Wallet().private_key)