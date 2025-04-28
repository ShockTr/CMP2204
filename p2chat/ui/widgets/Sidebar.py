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
from p2chat.util.peer_discovery import get_discovered_users
from p2chat.ui.widgets.SearhForIp import get_selected_users

@dataclass
class ChatOpened(Message):
    user: User

class Sidebar(Static):
    def compose(self) -> ComposeResult:
        discovered_users = get_discovered_users()
        with Vertical(classes="sidebar_vertical"):
            yield Button("Search", id="search_button", classes="sidebar_search_button")
            yield OptionList(
                *(item for pair in zip([SidebarChatListItem(user) for user in discovered_users], [None] * len(discovered_users)) for item in pair if item),
                classes="sidebar_chat_list",
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if event.option:
            user = event.option.user
            self.post_message(ChatOpened(user))

    #user listi guncelemek icin. Awayi guncellememe sorunuda cozdu rendera gerek yokmus xd
    def on_mount(self):
        self.styles.dock = "left"
        self.styles.width = "25"
        self.styles.height = "100%"
        self.auto_refresh = 1 / 30
        # Set a timer to refresh the user list every 5 seconds
        self.set_interval(1, self.refresh_user_list)

    #şuan ipye gore sıralamadıgımız ıcın isim degisince farklı bır kullanıcı gıbı sayıyor ve zaten suan sadece kendını goruyor
    def refresh_user_list(self):
        #Refresh the list of users in the sidebar

        selected_user_to_add = get_selected_users()
        discovered_users = get_discovered_users()
        option_list = self.query_one(".sidebar_chat_list", OptionList)

        # Clear the current list
        option_list.clear_options()

        # Add the discovered users to the list, updating their last_seen time from discovered_users
        for user in selected_user_to_add:
            # guncelle zamanı durmadan
            for discovered_user in discovered_users:
                if user.userId == discovered_user.userId:
                    # away olmasını engelemek ıcın onlıne olanın
                    user.last_seen = discovered_user.last_seen
                    break
            option_list.add_option(SidebarChatListItem(user))


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
