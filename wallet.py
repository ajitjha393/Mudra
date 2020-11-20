from binascii import hexlify
from Crypto.PublicKey import PublicKey, RSA
import Crypto.Random
import binascii


class Wallet:
    def __init__(self):
        self.private_key , self.public_key =  None , None

    def create_keys(self):
        private_key , public_key = self.generate_keys()
        self.private_key , self.public_key =  private_key , public_key
        
    def save_keys(self):
        if self.public_key and self.private_key:
            try:
                with open('wallet.txt',mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)

            except (IOError , IndexError):
                print('Saving Wallet Failed ...')


    def load_keys(self):
        try :
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key , self.private_key = public_key , private_key
        
        except(IOError, IndexError):
            print('Loading Wallet Failed...')

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()

        return (
            binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
            binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        )

print(Wallet().private_key)