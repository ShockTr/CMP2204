import json
import socket
from datetime import datetime
import os
from threading import Thread

import p2chat.util.encryption as encryption
from p2chat.util.classes import User, MessageContent, Message, KeyExchange

def log_message(message: Message, userId: str):

    history_dir = "history"
    if not os.path.isdir(history_dir):
        os.makedirs(history_dir)

    log_file = os.path.join(history_dir, f"{userId}.json")
    message_record = message.toJSON()

    if os.path.exists(log_file):
        with open(log_file, "r+") as f:
            data = json.load(f)
            data["messages"].append(message_record)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    else:
        with open(log_file, "w") as f:
            data = {"messages": [message_record]}
            json.dump(data, f, indent=4)

def send_unsecure_message(target_ip, message_text):
    port = 6001
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))

        message_content = MessageContent(unencrypted_message=message_text)
        message = Message(
            author=User("Me", socket.gethostbyname(socket.gethostname()), datetime.now()),
            content=message_content,
            timestamp=datetime.now()
        )

        s.send(json.dumps({"unencrypted_message": message_content}).encode())
        s.close()
        print("Unsecure message sent successfully.")
        log_message(message, message.author.userId)

    except Exception as e:
        raise e

def send_secure_message(target_ip, secret_number, message_text):
    port = 6001
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))

        try:
            private_key = int(secret_number)
        except ValueError:
            print("Secret number must be an integer.")
            s.close()
            return

        s.send(json.dumps({"key": str(secret_number)}).encode())
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
            author=User("Me", socket.gethostbyname(socket.gethostname()), datetime.now()),
            content=message_content,
            timestamp=datetime.now()
        )

        s.send(json.dumps({"encrypted_message": encrypted_msg}).encode())
        s.close()
        print("Secure message sent successfully.")
        log_message(message, message.author.userId)

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
        thread = Thread(target=chat_session)
        thread.start()
        thread.join()
