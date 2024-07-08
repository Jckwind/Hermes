import tkinter as tk
from tkinter import ttk


class ToolbarButton(ttk.Button):
    """A custom button widget for toolbars.

    This class extends ttk.Button to create a styled button suitable for
    use in toolbars. It includes custom styling.

    Attributes:
        None

    """

    def __init__(self, parent, text, command, *args, **kwargs):
        """Initialize the ToolbarButton.

        Args:
            parent: The parent widget.
            text: The text to display on the button.
            command: The function to call when the button is clicked.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        self._configure_style()
        super().__init__(parent, text=text, command=command,
                         style='ToolbarButton.TButton', *args, **kwargs)
        self.pack(side=tk.LEFT, padx=5, pady=5)

    def _configure_style(self):
        """Configure the custom style for the button."""
        style = ttk.Style()
        style.configure('ToolbarButton.TButton',
                        font=('Helvetica', 10, 'bold'),
                        padding=5,
                        relief='raised',
                        background='#4CAF50',
                        foreground='white')
