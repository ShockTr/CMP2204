import socket
import json
from datetime import datetime
import threading
from p2chat.util.classes import User

class PeerDiscovery:
    def __init__(self, listen_port=6000):
        self.listen_port = listen_port
        self.running = False
        self.peers = {}  # IP -> User objesi

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.listen_for_peers, daemon=True)
        self.thread.start()

    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.listen_port))

        print(f"[PeerDiscovery] Listening for broadcasts on UDP port {self.listen_port}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                ip_address = addr[0]

                try:
                    payload = json.loads(data.decode())
                    username = payload.get("username")

                    if username:
                        now = datetime.now()
                        if ip_address in self.peers:
                            self.peers[ip_address].last_seen = now
                        else:
                            user = User(username=username, ip_address=ip_address, last_seen=now)
                            self.peers[ip_address] = user
                            print(f"[PeerDiscovery] New user discovered: {username} ({ip_address})")

                except json.JSONDecodeError:
                    print("[PeerDiscovery] Received invalid JSON")

            except Exception as e:
                print(f"[PeerDiscovery] Error: {e}")

    def stop(self):
        self.running = False
        print("[PeerDiscovery] Stopped listening for peers.")

    def get_active_users(self):
        """15 dakika içinde en son görülen kullanıcıları getirir."""
        now = datetime.now()
        active_users = []
        for user in self.peers.values():
            if (now - user.last_seen).total_seconds() < 15 * 60:
                active_users.append(user)
        return active_users
