"""Context menu for nodes."""

from textual.geometry import Offset
from textual.message import Message
from textual.widget import Widget
from textual.widgets import OptionList


class NodeContextMenu(Widget):
    """Context menu for node operations."""

    DEFAULT_CSS = """
    NodeContextMenu {
        background: $panel;
        border: round $primary;
        padding: 0;
        min-width: 20;
    }
    """

    class Selected(Message):
        """Menu item selected message."""

        def __init__(self, action: str, node_id: str) -> None:
            self.action = action
            self.node_id = node_id
            super().__init__()

    def __init__(self, node_id: str, position: Offset):
        super().__init__()
        self.node_id = node_id
        self.position = position
        self.options = OptionList()

    def compose(self):
        """Create the menu items."""
        self.options.add_options(
            [
                "Add to Pipeline",
                "View Documentation",
                "Configure Parameters",
                "Copy Node ID",
            ]
        )
        yield self.options

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        """Handle menu item selection."""
        self.post_message(self.Selected(event.option.prompt, self.node_id))
        self.remove()
