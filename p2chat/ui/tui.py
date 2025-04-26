from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Placeholder
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from p2chat.ui.widgets.ChangeName import ChangeNameScreen
from textual.containers import Container, Horizontal, Vertical

from p2chat.ui.widgets.Sidebar import Sidebar
from p2chat.ui.widgets.MessageMenu import MessageMenu
from p2chat.ui.widgets.LogDisplay import LogDisplay
from p2chat.util.announce import start_announce_presence_thread

from p2chat.util.classes import User
from datetime import datetime

class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "change_name", "Change Name")
    ]

    def __init__(self):
        super().__init__()
        self.announce_thread = None
        self.announce_stop_event = None
        self.log_display = None
        # Initialize the global variable
        global announceName
        announceName = "Anonymous"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(classes="sidebar"):
                yield Sidebar()
            with Vertical(classes="message-panel"):
                yield MessageMenu(User("SenTest", "255.255.1.1", datetime.now()))
            #degistirmeyi unutma biraz karisti aq bura aglayacam
            with Vertical(id="right_panel"):
                # ChatWindow will replace this when a chat is selected
                self.log_display = LogDisplay(id="log_display")
                yield self.log_display
        yield Footer()

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
