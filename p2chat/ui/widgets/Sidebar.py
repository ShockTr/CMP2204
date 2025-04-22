from dataclasses import dataclass
from datetime import datetime

from textual.widgets import Input, Static, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical
from textual.app import ComposeResult
from rich.console import RenderResult, Console, ConsoleOptions
from rich.markup import escape
from rich.padding import Padding
from rich.text import Text
from p2chat.util.classes import User

USERS = [
    User("TEST", "3131", datetime.now()),
    User("TEST2", "3131", datetime.now()),
    User("TEST3", "3131", datetime.now()),
    User("TEST4", "3131", datetime.now()),
]

class Sidebar(Static):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Search...")
            yield OptionList(
                *[SidebarChatListItem(user) for user in USERS],
                classes="sidebar_chat_list",
            )


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