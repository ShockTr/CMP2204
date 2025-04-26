from dataclasses import dataclass
from datetime import datetime
from rich.console import ConsoleOptions, RenderResult, Console
from rich.text import Text
from textual.widgets import Input, Static, OptionList, Footer, Header
from textual.screen import Screen
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widgets._option_list import Option
from p2chat.util.classes import User

OnlineUsers = [
    User("OTest1", "3131", datetime.now()),
    User("OTest2", "3131", datetime.now()),
    User("OTest3", "3131", datetime.now()),
    User("OTest4", "3131", datetime.now()),
    User("OTest5", "3131", datetime.now()),
    User("OTest6", "3131", datetime.now()),
    User("OTest7", "3131", datetime.now()),
    User("OTest8", "3131", datetime.now()),
    User("OTest3", "3131", datetime.now()),
    User("OTest4", "3131", datetime.now()),
    User("OTest5", "3131", datetime.now()),
    User("OTest6", "3131", datetime.now()),
    User("OTest7", "3131", datetime.now()),
    User("OTest8", "3131", datetime.now()),
    User("OTest3", "3131", datetime.now()),
    User("OTest4", "3131", datetime.now()),
    User("OTest5", "3131", datetime.now()),
    User("OTest6", "3131", datetime.now()),
    User("OTest7", "3131", datetime.now()),
    User("OTest8", "3131", datetime.now()),
]


class SearchWithIp(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="SearchWithIp_wrapper"):
            yield Input(placeholder= "Search for user with IP", classes="SearchWithIp_search_input")
            yield OptionList(
                *[SearchWithIpItem(user) for user in OnlineUsers],
                classes="SearchWithIp_screen",
            )


@dataclass
class SearchWithIpRenderable:
    user: User
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = Text()
        text.append(f"{self.user.username}\n", style="bold center", )
        text.append(f"{self.user.getStatus()}", style="dim")
        yield text

class SearchWithIpItem(Option):
    def __init__(self, user: User):
        super().__init__(SearchWithIpRenderable(user))
        self.user = user
