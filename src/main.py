from view.view import View
from model.model import Model
from controller.controller import Controller
from pathlib import Path

def main():
    # Set up the database path
    db_path = Path.home() / "Library" / "Messages" / "chat.db"

    # Initialize the model
    model = Model(db_path)

    # Initialize the view
    view = View()

    # Initialize the controller
    controller = Controller(model, view)

    # Reset the application state before starting
    controller._on_reset()

    # Start the application
    controller.run()

if __name__ == "__main__":
    main()
