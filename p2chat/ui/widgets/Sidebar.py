from dataclasses import dataclass
from datetime import datetime
from time import time

from textual.message import Message
from textual.renderables.gradient import LinearGradient
from textual.widgets import Input, Static, OptionList, Button
from textual.widgets.option_list import Option
from textual.containers import Vertical, Container, Horizontal
from textual.app import ComposeResult
from rich.console import RenderResult, Console, ConsoleOptions
from rich.markup import escape
from rich.padding import Padding
from rich.text import Text
from p2chat.ui.widgets.SearhForIp import SearchWithIp
from p2chat.util.classes import User

USERS = [
    User("test31", "192.168.1.31", datetime.now()),
    User("test21", "192.168.1.21", datetime.now()),
    User("test11", "192.168.1.11", datetime.now()),

]

@dataclass
class ChatOpened(Message):
    user: User

class Sidebar(Static):
    def compose(self) -> ComposeResult:
        with Vertical(classes="sidebar_vertical"):
            yield Button("Search", id="search_button", classes="sidebar_search_button")
            yield OptionList(
                *(item for pair in zip([SidebarChatListItem(user) for user in USERS], [None] * len(USERS)) for item in pair if item),
                classes="sidebar_chat_list",
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if event.option:
            user = event.option.user
            self.post_message(ChatOpened(user))


    def on_mount(self):
        self.styles.dock = "left"
        self.styles.width = "25"
        self.styles.height = "100%"
        self.auto_refresh = 1 / 30

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "search_button":
            self.app.push_screen(SearchWithIp())



@dataclass
class ChatListItemRenderable:
    user: User
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = Text()
        text.append(f"{self.user.username}\n", style="bold  ")
        text.append(f"{self.user.getStatus()}", style="dim")
        yield text


class SidebarChatListItem(Option):
    def __init__(self, user: User):
        super().__init__(ChatListItemRenderable(user))
        self.user = user
