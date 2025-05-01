from dataclasses import dataclass
from rich.console import ConsoleOptions, RenderResult, Console
from rich.text import Text
from textual import on
from textual.widgets import Input, OptionList, Button
from textual.screen import Screen
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widgets._option_list import Option
from p2chat.util.classes import User
from p2chat.peerDiscovery import get_discovered_users
from p2chat.util.history import get_users_with_history

selected_users = get_users_with_history()

class SearchWithIp(Screen):
    current_search = ""

    def compose(self) -> ComposeResult:
        with Vertical(classes="SearchWithIp_wrapper"):
            self.input= Input(placeholder="Search for users by name or IP...", classes="SearchWithIp_search_input")
            yield self.input
            yield OptionList(
                classes="SearchWithIp_screen",
            )
            yield Button("Back", id="back_button", classes="back_button")


    # YAZDIGIN INPUTU FILTRELE ALTTA
    @on(Input.Changed)
    def filter_users(self, event: Input.Changed) -> None:
        self.current_search = event.value.lower()
        self.filter_user_list(self.current_search)

    # OLDU GALIBA
    def filter_user_list(self, search_text: str) -> None:
        discovered_users = get_discovered_users()
        option_list = self.query_one(".SearchWithIp_screen", OptionList)

        option_list.clear_options()

        filtered_users = [
            user for user in discovered_users
            if (search_text in user.username.lower() or 
                search_text in user.ip_address.lower())
        ]
        for user in filtered_users:
            option_list.add_option(SearchWithIpItem(user))



    @on(Input.Submitted)
    def choose_user(self, event: Input.Submitted) -> None:
        search_text = event.value.lower()
        option_list = self.query_one(".SearchWithIp_screen", OptionList)

        for option in option_list.options:
            if (search_text in option.user.username.lower() or
                    search_text in option.user.ip_address.lower()):
                selected_user = User(option.user.username, option.user.ip_address, option.user.last_seen)
                if selected_user in selected_users:
                    pass
                else:
                    selected_users.append(selected_user)
                self.app.pop_screen()
                return

        # No matching user found
        self.input.value = ""

    # userlisti guncellemek icin
    def on_mount(self):
        #1 saniyede bir guncelle
        self.refresh_user_list()
        self.set_interval(1 , self.refresh_user_list)


    #refreshliyor
    # OFFLINE OLDUGUNDA ARAMA LISTESINDEN SIL
    def refresh_user_list(self):
        # offline olunca arama  listesinden kaldirmak icin
        discovered_users = [user for user in get_discovered_users() if user.getStatus() != "Offline"]
        option_list = self.query_one(".SearchWithIp_screen", OptionList)

        # option listi temizle
        option_list.clear_options()

        # yenilerken filtreyi uygula
        if self.current_search:
            filtered_users = [
                user for user in discovered_users
                if (self.current_search in user.username.lower() or
                    self.current_search in user.ip_address.lower())
            ]
            for user in filtered_users:
                option_list.add_option(SearchWithIpItem(user))
        else:
            # Add all discovered users if no filter
            for user in discovered_users:
                option_list.add_option(SearchWithIpItem(user))

    def on_button_pressed(self, event):
        """Handle button press events"""
        if event.button.id == "back_button":
            self.app.pop_screen()



    def on_option_list_option_selected(self, event):
        selected_user = User(event.option.user.username, event.option.user.ip_address, event.option.user.last_seen)
        if selected_user in selected_users:
            pass
        else:
            selected_users.append(selected_user)

        self.app.pop_screen()

@dataclass
class SearchWithIpRenderable:
    user: User
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = Text()
        text.append(f"{self.user.username}", style="bold")
        # saga docklamak icin boslugu olc :D
        status = self.user.getStatus()
        available_width = options.max_width - len(self.user.username)
        padding = available_width - (len(status)+ 8)
        if padding > 0:
            text.append(" " * padding)
        text.append(f"Status: {status}\n", style="dim")
        text.append(f"{self.user.ip_address}", style="dim")

        yield text

class SearchWithIpItem(Option):
    def __init__(self, user: User):
        super().__init__(SearchWithIpRenderable(user))
        self.user = user

def get_selected_users():
    return selected_users
