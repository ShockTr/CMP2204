from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Placeholder
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

from p2chat.ui.widgets.Sidebar import Sidebar


class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            yield Placeholder()
        yield Footer()