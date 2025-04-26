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
    # DES için ilk 8 byte yeterli
    return hashlib.sha256(str(shared).encode()).digest()[:8]

def encrypt_message(des_key, message):
    cipher = pyDes.des(des_key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    encrypted = cipher.encrypt(message)
    # byte string → base64 → str
    return base64.b64encode(encrypted).decode()

def decrypt_message(des_key, encoded_ciphertext):
    cipher = pyDes.des(des_key, pyDes.ECB, padmode=pyDes.PAD_PKCS5)
    decoded_bytes = base64.b64decode(encoded_ciphertext.encode())
    return cipher.decrypt(decoded_bytes).decode()
