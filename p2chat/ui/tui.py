import socket
import time
from threading import Thread

from textual import on, work
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widgets import Footer, Header, Static
from textual.worker import get_current_worker

from p2chat.chatResponder import listenChatMessages, handleClient
from p2chat.ui.widgets.ChangeName import ChangeNameScreen
from textual.containers import Horizontal, Vertical

from p2chat.ui.widgets.Sidebar import Sidebar, ChatOpened
from p2chat.ui.widgets.MessageMenu import MessageMenu
from p2chat.ui.widgets.LogDisplay import LogDisplay
from p2chat.util.announce import start_announce_presence_thread

from p2chat.util.classes import User, Message
from datetime import datetime

class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "change_name", "Change Name")
    ]
    currentChatUser : Reactive[User] = Reactive(None)

    def __init__(self):
        super().__init__()
        self.announce_thread = None
        self.announce_stop_event = None
        self.log_display = LogDisplay(id="log_display")
        self.sock = None
        self.message_menu = None
        global announceName
        announceName = "Anonymous"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            with Vertical(id="chat_window"):
                MessageMenu(self.currentChatUser)
            with Vertical(id="right_panel"):
                yield self.log_display
        yield Footer()

    @on(ChatOpened)
    async def openChat(self, event: ChatOpened):
        if event.user != self.currentChatUser:
            self.currentChatUser = event.user

            chat_window = self.query_one("#chat_window")
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

    def on_unmount(self) -> None:
        if self.sock:
            try:
                self.sock.close()
                self.sock = None
            except Exception as e:
                print(f"Error closing connection: {e}")
        if self.announce_thread is not None and self.announce_stop_event is not None:
            self.announce_stop_event.set()
            self.announce_thread = None
            self.announce_stop_event = None

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

