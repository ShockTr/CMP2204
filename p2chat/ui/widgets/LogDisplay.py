from textual.app import ComposeResult
from textual.widgets import Log
from textual.widget import Widget


class LogDisplay(Widget):
    """A widget to display log messages."""

    def __init__(self, id=None):
        super().__init__(id=id or "log_display")

    def compose(self) -> ComposeResult:
        yield Log(id="log_content", highlight=True)

    def add_log(self, message: str):
        """Add a log message to the display."""
        log_widget = self.query_one("#log_content", Log)
        log_widget.write_line(message)
