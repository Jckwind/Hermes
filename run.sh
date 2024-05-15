#!/bin/bash

# Install required Python packages
echo "Installing required Python packages..."
pip install -r requirements.txt

# Run the GUI application
echo "Running the GUI application..."
python src/gui.py