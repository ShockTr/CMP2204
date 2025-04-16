from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static
from textual.containers import Container, Horizontal, Vertical, VerticalScroll


class p2chatApp(App):
    CSS_PATH = "p2chat.css"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Content goes here!")
        yield Footer()