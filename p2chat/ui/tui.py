from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static
from p2chat.ui.widgets.ChangeName import ChangeNameScreen
from textual.containers import Horizontal, Vertical

from p2chat.ui.widgets.SearhForIp import SearchWithIp
from p2chat.ui.widgets.Sidebar import Sidebar, ChatOpened
from p2chat.ui.widgets.MessageMenu import MessageMenu
from p2chat.ui.widgets.LogDisplay import LogDisplay
from p2chat.util.announce import start_announce_presence_thread
from p2chat.util.peer_discovery import start_peer_discovery

from p2chat.util.classes import User
from datetime import datetime

class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "change_name", "Change Name"),
        ("s", "search_start", "Search")
    ]
    currentChatUser = None

    def __init__(self):
        super().__init__()
        self.announce_thread = None
        self.announce_stop_event = None
        self.peer_listener_thread = None
        self.peer_save_thread = None
        self.peer_stop_event = None
        self.log_display = LogDisplay(id="log_display")
        # Initialize the global variable
        global announceName
        announceName = "Anonymous"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            with Vertical(id="chat_window"):
                yield MessageMenu(User("SenTest", "255.255.1.1", datetime.now()))
            with Vertical(id="right_panel"):
                yield self.log_display
        yield Footer()

    def on_mount(self):
        # Start peer discovery
        self.peer_listener_thread, self.peer_save_thread, self.peer_stop_event = start_peer_discovery(self.log_message)

    def on_unmount(self):
        # Stop peer discovery
        if self.peer_stop_event:
            self.peer_stop_event.set()

        # Stop announce thread
        if self.announce_stop_event:
            self.announce_stop_event.set()

    @on(ChatOpened)
    async def openChat(self, event: ChatOpened):
        if event.user != self.currentChatUser:
            self.currentChatUser = event.user
            # Chat window container'ını bul

            chat_window = self.query_one("#chat_window")
            # Mevcut MessageMenu widget'ını bul ve kaldır

            existing_menu = chat_window.query("MessageMenu")
            if existing_menu:
                existing_menu.first().remove()

            # Seçilen kullanıcı ile yeni bir MessageMenu oluştur ve ekle
            new_menu = MessageMenu(event.user)
            await chat_window.mount(new_menu)

    def action_change_name(self):
        self.push_screen(ChangeNameScreen())

    def log_message(self, message: str):
        self.log.info(message)
        if self.log_display:
            self.log_display.add_log(message)

    def update_user_name(self, new_name: str):
        global announceName
        announceName = new_name
        try:
            self.query_one("#chat_window_header", Static).update(f"Chat as {announceName}")
        except Exception:
            pass

        # oncekini durdur yeni baslata yariyor
        if self.announce_thread is not None and self.announce_stop_event is not None:
            # Signal the thread to stop
            self.announce_stop_event.set()

            self.announce_thread = None
            self.announce_stop_event = None

        # yeni baslat
        self.announce_thread, self.announce_stop_event = start_announce_presence_thread(new_name, self.log_message)

    def action_search_start(self):
        self.push_screen(SearchWithIp())
