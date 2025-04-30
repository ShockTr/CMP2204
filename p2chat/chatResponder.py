import json
import os.path
import socket
from datetime import datetime
from threading import Thread
import p2chat.util.encryption as encryption
from p2chat.util.classes import KeyExchange, MessageContent, Message, User
from p2chat.peerDiscovery import get_discovered_users
from p2chat.util.history import save_message


def handleClient(conn: socket.socket, addr, callback):
    print(f"New connection from {addr}")

    user = User("Unknown", addr[0], datetime.now())
    users = get_discovered_users()
    user = [user for user in users if user.ip_address == addr[0]][0]
    # When merging with peerDiscovery branch proper username will be fetched

    KEYEXCHANGE = False
    key: KeyExchange = None
    messageContent: MessageContent = None
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                break

            jsonData: dict
            try:
                jsonData = json.loads(data.decode())
            except json.JSONDecodeError:
                print("Invalid JSON received")
                break

            if ('key' in jsonData):
                if not KEYEXCHANGE:
                    recievedKey = int(jsonData['key'])
                    privateKey = encryption.generate_private_key()
                    key = KeyExchange(recievedKey, privateKey)

                    try :
                        conn.send(json.dumps({'key': encryption.generate_public_key(privateKey)}).encode())
                    except Exception as e:
                        print(f"Error sending key: {e}")
                        break
                    KEYEXCHANGE = True
                else:
                    print(f"Key exchange already done from {addr}")
                    break
            else:
                messageContent = MessageContent(jsonData.get('unencrypted_message', ""), jsonData.get('encrypted_message', ""), key)

        except Exception as e:
            print(f"Error: {e}")
            break
    conn.close()
    finalMessage = Message(user, messageContent, datetime.now())
    save_message(user.userId, finalMessage)
    callback(finalMessage)
    print(f"Connection closed from {addr}")


def listenChatMessages(messageCallback, port=6001) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))

    sock.listen()
    print(f"Listening for connections on port {port}")

    while True:
        conn, addr = sock.accept()

        thread = Thread(target=handleClient, args=(conn, addr, messageCallback))
        thread.start()

if __name__ == '__main__':
    listenChatMessages(print)