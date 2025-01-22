# This file implements messaging between two peer secured by 
# cryptographic methods such as DS, HMAC, AES
# This file is going to run inside of k8s cluster as a server

# Assume that public key for digital signature is already distributed by secure channel

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, hmac 

message = os.urandom(32) # random 32-bytes message

bob_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
bob_public_key = bob_private_key.public_key()

bob_signature = bob_private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

