import binascii
import json
import socket
from datetime import datetime
import p2chat.serviceAnnouncer
import p2chat.util.encryption as encryption
from p2chat.util.classes import User, MessageContent, Message, KeyExchange
from p2chat.util.history import save_message

def log_message(message: Message, userId: str):
    save_message(userId, message)

def send_unsecure_message(target_ip, message_text):
    port = 6001
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))

        message_content = MessageContent(unencrypted_message=message_text)
        message = Message(
            author=User(p2chat.serviceAnnouncer.announceName, "localhost", datetime.now()),
            content=message_content,
            timestamp=datetime.now()
        )

        s.send(json.dumps({"unencrypted_message": message_text}).encode())
        s.close()
        print("Unsecure message sent successfully.")
        log_message(message, binascii.hexlify(target_ip.encode()).decode())

    except Exception as e:
        raise e

def send_secure_message(target_ip, secret_number, message_text):
    port = 6001
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))

        try:
            private_key = int(secret_number)
            public_key = encryption.generate_public_key(private_key)
        except ValueError:
            print("Secret number must be an integer.")
            s.close()
            return

        s.send(json.dumps({"key": str(public_key)}).encode())
        response = s.recv(2048)
        if not response:
            print("No response for key exchange.")
            s.close()
            return

        response_json = json.loads(response.decode())
        if "key" not in response_json:
            print("Invalid key exchange response received.")
            s.close()
            return

        peer_pub_key = int(response_json["key"])
        shared_key = encryption.generate_shared_secret(peer_pub_key, private_key)

        key_exchange = KeyExchange(peer_pub_key, private_key)
        encrypted_msg = encryption.encrypt_message(shared_key, message_text)

        message_content = MessageContent(
            unencrypted_message="",
            encrypted_message=encrypted_msg,
            key=key_exchange
        )

        message = Message(
            author=User(p2chat.serviceAnnouncer.announceName, "localhost", datetime.now()),
            content=message_content,
            timestamp=datetime.now()
        )

        s.send(json.dumps({"encrypted_message": encrypted_msg}).encode())
        s.close()
        print("Secure message sent successfully.")
        log_message(message, binascii.hexlify(target_ip.encode()).decode())

    except Exception as e:
        raise e

def chat_session():
    print("Chat Initiator")
    target_ip = input("Enter the target IP address: ").strip()
    chat_type = input("Enter chat type (secure/unsecure): ").strip().lower()

    if chat_type == "secure":
        secret_number = input("Enter your secret number for key exchange (an integer): ").strip()
        message_text = input("Enter the message to send (this will be encrypted): ").strip()
        send_secure_message(target_ip, secret_number, message_text)
    elif chat_type == "unsecure":
        message_text = input("Enter the message to send: ").strip()
        send_unsecure_message(target_ip, message_text)
    else:
        print("Invalid chat type specified. Choose 'secure' or 'unsecure'.")

if __name__ == "__main__":
    while True:
        chat_session()
