import json
import os

from textual.widgets import Input, Static , Label
from textual.containers import Vertical, VerticalScroll
from textual.app import ComposeResult
from textual import on

from rich.markup import escape
from rich.text import Text

from p2chat.util.classes import User, MessageContent, Message

from dataclasses import dataclass
from datetime import datetime


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
                    messageContent = MessageContent(message["content"]["unencrypted_message"], message["content"]["encrypted_message"], message["content"].get("key"))
                    author = User(message["author"]["username"], message["author"]["ip_address"], datetime.fromtimestamp(message["author"]["last_seen"]))
                    message = Message(author, messageContent, datetime.fromtimestamp(message["timestamp"]))
                    self.display_message(message)

    @on(Input.Submitted) # on ve input import edildi
    def send_message(self, event: Input.Submitted) -> None:
        content = event.value.strip()
        if  content :
            message = Message(
                author=self.user,
                content=MessageContent(unencrypted_message=content),
                timestamp=datetime.now()
            )

            self.display_message(message)
            self.input.value = ""

    def display_message(self, message: Message) -> None:
        formatted = Text()
        formatted.append(f"[{message.author.username}]: ", style="bold")
        formatted.append(f"{escape(message.content.unencrypted_message)}" )
        self.message_list.mount(Label(formatted, classes="chat_message"))
