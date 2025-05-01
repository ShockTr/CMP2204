import socket
import json
import time
import threading
from threading import Event

announceName = "Me"

def announce_presence(username, log_callback=None, stop_event=None):
    # Define the message to be sent
    message = {
        "username": username,
    }
    # Convert the message to JSON format
    json_message = json.dumps(message)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the broadcast address and port
    broadcast_address = ('192.168.1.255', 6000)

    # Enable the socket to send broadcast messages
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        while stop_event is None or not stop_event.is_set():
            # Send the JSON message
            sock.sendto(json_message.encode('utf-8'), broadcast_address)
            if log_callback:
                log_callback(f"Announced presence: {json_message}")

            # Wait for 8 seconds before sending the next announcement
            # Check the stop_event every second to allow for quicker stopping
            if stop_event:
                for _ in range(8):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
            else:
                time.sleep(8)
    except KeyboardInterrupt:
        if log_callback:
            log_callback("Stopping presence announcement.")
    finally:
        sock.close()

def start_announce_presence_thread(username, log_callback=None):
    """
    Start the announce_presence function in a separate thread
    Returns a tuple of (thread, stop_event) where stop_event can be set to stop the thread
    """
    stop_event = Event()
    thread = threading.Thread(target=announce_presence, args=(username, log_callback, stop_event), daemon=True)
    thread.start()
    return (thread, stop_event)
