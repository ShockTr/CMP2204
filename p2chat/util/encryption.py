import random
import hashlib
import base64
import pyDes

# DH sabitleri
P = 19
G = 2

def generate_private_key():
    return random.randint(1, P - 2)

def generate_public_key(private_key):
    return pow(G, private_key, P)

def generate_shared_secret(received_key, private_key):
    shared = pow(received_key, private_key, P)
    return shared

def encrypt_message(shared_secret, message):
    des_key = str(shared_secret).ljust(24)

    cipher = pyDes.triple_des(des_key)
    encrypted = cipher.encrypt(message, padmode=pyDes.PAD_PKCS5)
    # byte string → base64 → str
    return base64.b64encode(encrypted).decode()

def decrypt_message(shared_secret, encoded_ciphertext):
    des_key = str(shared_secret).ljust(24)

    cipher = pyDes.triple_des(des_key)
    decoded_bytes = base64.b64decode(encoded_ciphertext.encode())
    return cipher.decrypt(decoded_bytes, padmode=pyDes.PAD_PKCS5).decode()
