import json
import os

from textual.widgets import Input, Static , Label
from textual.containers import Vertical, VerticalScroll
from textual.app import ComposeResult
from textual import on

from rich.markup import escape
from rich.text import Text

from p2chat.util.classes import User, MessageContent, Message, KeyExchange
from p2chat.chatInitiator import send_secure_message, send_unsecure_message

from dataclasses import dataclass
from datetime import datetime

from p2chat.util.encryption import generate_private_key, decrypt_message


class MessageMenu(Static):
    def __init__(self, user: User , *args , **kwargs ):
        super().__init__(*args, **kwargs)
        self.user = user


    def compose(self) -> ComposeResult:
        with Vertical():
            self.message_list = VerticalScroll(Static(f"Beginning of a great conversation... User {self.user.username}, ID: {self.user.userId}"),classes="message_list")
            yield self.message_list

            self.input= Input(placeholder="Send a message from here...", classes="message_input")
            yield self.input

    def on_mount(self) -> None:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "history", f"{self.user.userId}.json")
        if os.path.isfile(path):
            with open(path, "r") as f:
                data = json.load(f)
                for message in data["messages"]:
                    if message["content"].get("key") is not None:
                        messageContent = MessageContent(message["content"]["unencrypted_message"],
                                                        message["content"]["encrypted_message"],
                                                        KeyExchange(0, 0, int(message["content"].get("key", 0))))
                    else:
                        messageContent = MessageContent(message["content"]["unencrypted_message"],
                                                        message["content"]["encrypted_message"])
                    author = User(message["author"]["username"], message["author"]["ip_address"], datetime.fromtimestamp(message["author"]["last_seen"]))
                    message = Message(author, messageContent, datetime.fromtimestamp(message["timestamp"]))
                    self.display_message(message)

    @on(Input.Submitted) # on ve input import edildi
    def send_message(self, event: Input.Submitted) -> None:
        content = event.value.strip()
        if content:
            message = Message(
                author=self.app.user,
                content=MessageContent(unencrypted_message=content),
                timestamp=datetime.now()
            )
            try:
                if self.app.secure:
                    send_secure_message(self.user.ip_address, generate_private_key(), content)
                else:
                    send_unsecure_message(self.user.ip_address, content)
                self.display_message(message)
                self.input.value = ""
            except Exception as e:
                self.app.log.error(f"Error sending message: {e}")



    def display_message(self, message: Message) -> None:
        formatted = Text()
        formatted.append(f"[{message.author.username}]: ", style="bold")
        if(message.content.encrypted_message):
            formatted.append(f"{escape(decrypt_message(message.content.key.key, message.content.encrypted_message))}" )
        formatted.append(f"{escape(message.content.unencrypted_message)}" )
        self.message_list.mount(Label(formatted, classes="chat_message"))
