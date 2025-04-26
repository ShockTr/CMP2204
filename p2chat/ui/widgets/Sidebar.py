from dataclasses import dataclass
from datetime import datetime
from time import time

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
    User("emre", "3131", datetime.now()),
    User("anil", "3131", datetime.now()),
    User("yunus", "3131", datetime.now()),
    User("eren", "3131", datetime.now()),
    User("emirhan", "3131", datetime.now()),
    User("kaan", "3131", datetime.now()),
    User("yigit", "3131", datetime.now()),
    User("emir", "3131", datetime.now()),
    User("deniz", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
]


class ChatWindow(Static):
    """Sağ tarafta açılacak sohbet penceresi."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def compose(self) -> ComposeResult:
        yield Static(f"Chat with {self.user.username}", classes="chat_window_header")
        yield Static("Chat content here...", classes="chat_window_content")
        yield Input(placeholder="Type a message...", id="chat_input" ,classes="chat_window_input")

    def on_mount(self):
        self.styles.width = "100%"
        self.styles.height = "100%"
        #renk unutma

class Sidebar(Static):
    def compose(self) -> ComposeResult:
        with Vertical(classes="sidebar_vertical"):
            yield Button("Search", id="search_button", classes="sidebar_search_button")
            yield OptionList(
                *(item for pair in zip([SidebarChatListItem(user) for user in USERS], [None] * len(USERS)) for item in pair if item),
                classes="sidebar_chat_list",
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        selected_option = event.option
        if isinstance(selected_option, SidebarChatListItem):
            chat_window = ChatWindow(selected_option.user)
            parent_container = self.parent
            if isinstance(parent_container, Container) or isinstance(parent_container, Horizontal):
                for child in parent_container.children:
                    if isinstance(child, ChatWindow):
                        child.remove()
                # Mount the new chat window
                parent_container.mount(chat_window)

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
