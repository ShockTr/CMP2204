from datetime import datetime
from dataclasses import dataclass
import hashlib

@dataclass
class User:
    userId: str
    username: str
    ip_address: str
    last_seen: datetime
    last_message: datetime
    def __init__(self, username: str, ip_address: str, last_seen: datetime):
        self.username = username
        self.ip_address = ip_address
        self.last_seen = last_seen
        self.userId = hashlib.md5(f"{ip_address}:{username}".encode()).hexdigest()

    def getStatus(self):
        diff = datetime.now() - self.last_seen
        if diff.total_seconds() < 10:
            return "Online"
        elif diff.total_seconds() < 15 * 60:
            return "Away"
        else:
            return "Offline"

@dataclass
class MessageContent:
    unencrypted_message: str = None
    encrypted_message: str = None
    key: str = None

@dataclass
class Message:
    author: User
    content: MessageContent
    timestamp: datetime

