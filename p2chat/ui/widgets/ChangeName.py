from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static, Input, Button


class ChangeNameScreen(Screen):

    def compose(self) -> ComposeResult:
        with Vertical(classes="change_name_wrapper", id="change_name_screen"):
            yield Static("Enter your new name:", classes="change_name_label")
            yield Input(placeholder="Your new name...", id="change_name_input")
            yield Button("Submit", id="change_name_submit")

    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "change_name_submit":
            new_name_input = self.query_one("#change_name_input", Input)
            new_name = new_name_input.value.strip()

            if new_name:
                self.app.update_user_name(new_name)

            self.app.pop_screen()
