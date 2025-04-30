import binascii
import json
import os
from datetime import datetime

from p2chat.util.classes import Message, User

history_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "history")
if not os.path.isdir(history_dir):
    os.makedirs(history_dir)

def get_history(user_id, logger=print) -> list[Message]:

    path = os.path.join(history_dir, f"{user_id}.jsonl")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r") as f:
            messages = [Message.fromJSON(json.loads(line)) for line in f]
            return messages
    except Exception as e:
        logger(f"Error reading history: {e}")
        return []

def save_message(user_id: str, message: Message, logger=print) -> None:
    path = os.path.join(history_dir, f"{user_id}.jsonl")
    try:
        with open(path, "a", buffering=1) as f:
            f.write(json.dumps(message.toJSON()) + "\n")
    except Exception as e:
        logger(f"Error saving message: {e}")

def get_users_with_history(logger=print) -> list[User]:
    try:
        usersFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "users.json")
        seenUsers = []
        if os.path.isfile(usersFile):
            with open(usersFile, "r") as f:
                seenUsers = json.load(f)
        users = []
        for file in os.listdir(history_dir):
            if file.endswith(".jsonl"):
                userId = file[:-6]
                ip_address = binascii.unhexlify(userId).decode()
                username = "Unknown"
                last_seen = datetime.fromtimestamp(0)
                if ip_address in seenUsers:
                    username = seenUsers[ip_address]["username"]
                    last_seen = datetime.fromtimestamp(seenUsers[ip_address]["last_seen"])
                user = User(username, ip_address, last_seen)
                users.append(user)
        return users
    except Exception as e:
        raise e
        logger(f"Error getting users with history: {e}")
        return []