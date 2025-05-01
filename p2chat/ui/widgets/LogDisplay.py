from textual.app import ComposeResult
from textual.widgets import RichLog
from textual.widget import Widget


class LogDisplay(Widget):
    """A widget to display log messages."""

    def __init__(self, id=None):
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        self.log_widget = RichLog(auto_scroll=True, wrap=True, highlight=True, min_width=0, id="log_display")
        yield self.log_widget

    def add_log(self, message: str):
        """Add a log message to the display."""
        self.log_widget.write(message)
