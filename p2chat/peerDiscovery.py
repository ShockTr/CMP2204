import os
import socket
import threading
import time
import json
from threading import Event
from datetime import datetime
from p2chat.util.classes import User

# Dictionary to store IP addresses
peers = {}
discovered_users: list[User] = []


# Function to handle incoming messages
def handle_message(data, addr):
    message = data.decode('utf-8')
    try:
        message_data = json.loads(message)
        ip_address = addr[0]
        name = message_data.get('username')
        current_time = datetime.now()
    except json.JSONDecodeError:
        print("Received invalid JSON data")
        return

    peers[ip_address] = {'username': name, 'last_seen': current_time.timestamp()}

    # Create a User object and add it to discovered_users if not already present

    new_user = User(name, ip_address, current_time)

    # Check if user already exists in the list
    user_exists = False
    for i, user in enumerate(discovered_users):
        if user.userId == new_user.userId:
            # Update existing user's last_seen time
            discovered_users[i].last_seen = current_time
            user_exists = True
            break

    # Add new user if not found
    if not user_exists:
        discovered_users.append(new_user)


# Function to listen for incoming UDP messages
def listen_for_peers(port=6000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"Listening for peers on port {port}...")

    while True:
        data, addr = sock.recvfrom(1024)
        handle_message(data, addr)


# Function to save peers to a file
def save_peers_to_file(filename):
    try:
        with open(filename, 'r') as file:
            existing_peers = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_peers = {}

    for ip, info in peers.items():
        existing_peers[ip] = info
        existing_peers[ip]["last_seen"] = info["last_seen"]

    with open(filename, 'w') as file:
        json.dump(existing_peers, file, indent=4)


# Function to periodically save peers to a file
def periodic_save(filename, interval=3, stop_event=None):
    while stop_event is None or not stop_event.is_set():
        save_peers_to_file(filename)

        # Check the stop_event every second to allow for quicker stopping
        if stop_event:
            for _ in range(interval):
                if stop_event.is_set():
                    break
                time.sleep(1)
        else:
            time.sleep(interval)

# Function to start peer discovery in a separate thread
def start_peer_discovery(log_callback=None):
    #thread baslat ayri en bastan kapatana kadar dewam
    stop_event = Event()

    # Start the listener thread
    listener_thread = threading.Thread(target=listen_for_peers, daemon=True)
    listener_thread.start()

    # Start the periodic save thread
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "users.json")

    save_thread = threading.Thread(target=periodic_save, args=(filename, 3, stop_event), daemon=True)
    save_thread.start()

    if log_callback:
        log_callback("Peer discovery started")

    return (listener_thread, save_thread, stop_event)

def get_discovered_users():
    return discovered_users
