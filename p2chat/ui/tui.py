from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Placeholder
from textual.containers import Container, Horizontal, Vertical

from p2chat.ui.widgets.Sidebar import Sidebar
from p2chat.ui.widgets.MessageMenu import MessageMenu

from p2chat.util.classes import User
from datetime import datetime

class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(classes="sidebar"):
                yield Sidebar()
            with Vertical(classes="message-panel"):
                yield MessageMenu(User("SenTest", "255.255.1.1", datetime.now()))

        yield Footer()