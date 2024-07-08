from typing import List, Dict
from model.model import Model
from view.view import View
from model.text_collection.chat import Chat


class Controller:
    """Controller class for managing interactions between Model and View."""

    def __init__(self, model: Model, view: View):
        """Initialize the Controller.

        Args:
            model: The Model instance.
            view: The View instance.
        """
        self._model = model
        self._view = view
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for the view."""
        self._view.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)
        self._view.bind("<<ExportChat>>", self._on_export_chat)
        self._view.bind("<<ToggleDumpWindow>>", self._on_toggle_dump_window)
        self._view.search_var.trace("w", self._on_search)

    def run(self) -> None:
        """Load chats and start the main event loop."""
        self._load_chats()
        self._view.mainloop()

    def _load_chats(self) -> None:
        """Load chats from the model and display them in the view."""
        chats = self._model.get_chats()
        self._view.display_chats(chats)
        self._model.load_contacts()

    def _on_chat_selected(self, event: object) -> None:
        """Handle chat selection event.

        Args:
            event: The event object containing the selected chat's ID.
        """
        chat_index = event.widget.curselection()
        if chat_index:
            chat_name = self._view.chat_listbox.get(chat_index)
            self._view.display_chat_name(chat_name)
            
            # Call the backend to retrieve messages
            chat = self._model.get_chat(chat_name)
            if chat:
                messages = self._model.get_messages(chat.chat_identifier)
                # Optionally, you can log or process the messages here
                print(f"Retrieved {len(messages)} messages for chat: {chat_name}")

    def _on_export_chat(self, event: object) -> None:
        """Handle chat export event.

        Args:
            event: The event object (unused).
        """
        selected_chat = self._view.get_selected_chat()
        if selected_chat:
            chat = self._model.text_collector.chat_cache.get(selected_chat.chat_id)
            if chat:
                messages = self._model.get_messages(chat.chat_id)
                self._view.export_chat(messages)

    def _on_toggle_dump_window(self, event: object) -> None:
        """Handle toggle dump window event.

        Args:
            event: The event object (unused).
        """
        selected_chat = self._view.get_selected_chat()
        if selected_chat:
            chat = self._model.text_collector.chat_cache.get(selected_chat.chat_id)
            if chat:
                messages = self._model.get_messages(chat.chat_id)
                self._view.toggle_dump_window(messages)

    def _on_search(self, *args) -> None:
        """Handle search bar input event."""
        search_term = self._view.search_var.get().lower()
        filtered_chats = self._model.text_collector.search_chats(search_term)
        self._view.display_chats(filtered_chats)
