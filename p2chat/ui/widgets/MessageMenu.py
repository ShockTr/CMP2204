import json
import os

from textual.widgets import Input, Static, Label, RichLog
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
from p2chat.util.history import get_history


class MessageMenu(Static):
    def __init__(self, user: User , *args , **kwargs ):
        super().__init__(*args, **kwargs)
        self.user = user


    def compose(self) -> ComposeResult:
        with Vertical():
            self.message_list = RichLog(auto_scroll=True, wrap=True, min_width=0, classes="message_list")
            yield self.message_list

            self.input= Input(placeholder="Send a message from here...", classes="message_input")
            yield self.input

    def on_mount(self) -> None:
        messages = get_history(self.user.userId, self.app.log_message)
        for message in messages:
            self.display_message(message)

    @on(Input.Submitted) # on ve input import edildi
    def send_message(self, event: Input.Submitted) -> None:
        content = event.value.strip()
        if content:
            self.input.disabled = True
            message: Message
            try:
                if self.app.secure:
                    send_secure_message(self.user.ip_address, generate_private_key(), content)
                    message = Message(
                        author=self.app.user,
                        content=MessageContent(encrypted_message=content),
                        timestamp=datetime.now()
                    )
                else:
                    send_unsecure_message(self.user.ip_address, content)
                    message = Message(
                        author=self.app.user,
                        content=MessageContent(unencrypted_message=content),
                        timestamp=datetime.now()
                    )
                self.display_message(message)
                self.input.value = ""
            except Exception as e:
                self.app.log_message(f"Error sending message: {e}")
            finally:
                self.input.disabled = False
                self.input.focus()



    def display_message(self, message: Message) -> None:
        emojis = "🔒" if message.content.encrypted_message else "🔓"
        emojis += "🔑" if message.content.key else ""
        formatted = Text()
        formatted.append(message.timestamp.strftime('[%d.%m.%Y %H:%M]'), style="dimmed")
        formatted.append(f" <{escape(message.author.username)} {emojis}> ", style="bold")
        if (message.content.encrypted_message):
            formatted.append(f"{escape(decrypt_message(message.content.key.key, message.content.encrypted_message) if message.content.key else message.content.encrypted_message)}")
        elif (message.content.unencrypted_message):
            formatted.append(f"{escape(message.content.unencrypted_message)}")
        else:
            formatted.append("No message content", style="bold red")
        self.message_list.write(formatted)
