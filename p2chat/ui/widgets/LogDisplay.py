from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static
from rich.text import Text

#degistirilecek unutma bilgi icin YO YO YO YO


class LogDisplay(Static):
    """A widget to display log messages."""

    def __init__(self, id=None):
        super().__init__(id=id or "log_display")
        self.logs = []

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="log_scroll"):
            yield Static("", id="log_content")

    def add_log(self, message: str):
        """Add a log message to the display."""
        self.logs.append(message)
        self.update_logs()

    def update_logs(self):
        """Update the log content with all logs."""
        log_content = self.query_one("#log_content", Static)
        text = Text()
        for log in self.logs:
            text.append(f"{log}\n")
        log_content.update(text)