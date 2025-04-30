import socket
import time
from threading import Thread

from textual import on, work
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widgets import Footer, Header, Static
from textual.worker import get_current_worker

from p2chat.chatResponder import handleClient
from p2chat.ui.widgets.ChangeName import ChangeNameScreen
from textual.containers import Horizontal, Vertical

from p2chat.ui.widgets.SearhForIp import SearchWithIp
from p2chat.ui.widgets.Sidebar import Sidebar, ChatOpened
from p2chat.ui.widgets.MessageMenu import MessageMenu
from p2chat.ui.widgets.LogDisplay import LogDisplay
from p2chat.serviceAnnouncer import start_announce_presence_thread
from p2chat.peerDiscovery import start_peer_discovery
import p2chat.serviceAnnouncer
from p2chat.util.classes import User, Message
from datetime import datetime

class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "change_name", "Change Name"),
        ("s", "search_start", "Search"),
        ("t", "enable_secure", "Enable Secure"),
        ("t", "disable_secure", "Disable Secure"),
    ]
    currentChatUser : Reactive[User] = Reactive(None)

    def __init__(self):
        super().__init__()
        self.announce_thread = None
        self.announce_stop_event = None
        self.peer_listener_thread = None
        self.peer_save_thread = None
        self.peer_stop_event = None
        self.log_display = LogDisplay(id="log_display")
        self.sock = None
        self.message_menu = None
        self.secure: Reactive[bool] = Reactive(True, bindings=True)
        self.user = User(p2chat.serviceAnnouncer.announceName, "localhost", datetime.now())

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            with Vertical(id="chat_window"):
                MessageMenu(self.currentChatUser)
            with Vertical(id="right_panel"):
                yield self.log_display
        yield Footer()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "enable_secure":
            return not self.secure
        return True
    def action_enable_secure(self):
        self.secure = True
        self.query_one(Footer).refresh(recompose=True)

    def action_disable_secure(self):
        self.secure = False
        self.query_one(Footer).refresh(recompose=True)

    @on(ChatOpened)
    async def openChat(self, event: ChatOpened):
        if event.user != self.currentChatUser:
            self.currentChatUser = event.user

            # Chat window container'ını bul
            chat_window = self.query_one("#chat_window")
            
            # Mevcut MessageMenu widget'ını bul ve kaldır
            existing_menu = chat_window.query("MessageMenu")
            if existing_menu:
                await existing_menu.first().remove()

            new_menu = MessageMenu(event.user)
            self.message_menu = new_menu
            await chat_window.mount(new_menu)

    def action_change_name(self):
        self.push_screen(ChangeNameScreen())

    def log_message(self, message: str):
        self.log.info(message)
        if self.log_display:
            self.log_display.add_log(message)

    def message_received_callback(self, message: Message):
        def update_ui():
            self.log_message(f"Received message: {message}")
            if self.currentChatUser and self.currentChatUser.userId == message.author.userId:
                if self.message_menu:
                    self.message_menu.display_message(message)

        self.call_from_thread(update_ui)

    @work(thread=True)
    async def start_listening_messages(self):
        worker = get_current_worker()
        port = 6001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.setblocking(False)

        self.sock.listen()
        self.log_message("Listening for incoming messages...")
        print(f"Listening for connections on port {port}")

        while not worker.is_cancelled:
            try:
                conn, addr = self.sock.accept()
                conn.setblocking(True)
                thread = Thread(target=handleClient, args=(conn, addr, self.message_received_callback))
                thread.daemon = True
                thread.start()
            except BlockingIOError:
                time.sleep(0.1)
                continue
            except Exception as e:
                self.log_message(f"Error accepting connection: {e}")
                if self.sock is None:
                    break

    def on_mount(self) -> None:
        self.start_listening_messages()
        # Start peer discovery
        self.peer_listener_thread, self.peer_save_thread, self.peer_stop_event = start_peer_discovery(self.log_message)

    def on_unmount(self) -> None:
        if self.sock:
            try:
                self.sock.close()
                self.sock = None
            except Exception as e:
                print(f"Error closing connection: {e}")

        # Stop peer discovery
        if self.peer_stop_event:
            self.peer_stop_event.set()

        # Stop announce thread
        if self.announce_stop_event:
            self.announce_stop_event.set()

    def update_user_name(self, new_name: str):
        p2chat.serviceAnnouncer.announceName = new_name
        self.app.user = User(new_name, "localhost", datetime.now())
        try:
            self.query_one("#chat_window_header", Static).update(f"Chat as {new_name}")
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

