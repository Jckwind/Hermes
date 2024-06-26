# Hermes - Encrypted iMessage Extractor and Viewer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.x-green.svg)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [License](#license)
- [Contact](#contact)

## Overview
Hermes is a powerful tool designed to securely extract and view iMessages from macOS devices. It provides a user-friendly interface for accessing and managing your iMessage data, ensuring privacy and ease of use.

![Hermes Screenshot](path/to/screenshot.png)

## Features
- **GUI Viewer**: Intuitive interface for browsing and searching messages
- **Secure Extraction**: Safely extract iMessages from macOS devices
- **Export Functionality**: Export conversations or selected messages
- **Multi-device Support**: Compatible with iPhone and Mac synchronization

## Prerequisites
- macOS device with iMessages enabled
- Python 3.x
- Homebrew (for easy Python installation)

To set up Text Message Forwarding from your iPhone to your Mac, follow these steps:

1. **Access Settings on iPhone**:
   - Open `Settings`.
   - Navigate to `Messages`.

2. **Enable Text Message Forwarding**:
   - Tap on `Text Message Forwarding`.

3. **Verify Account Consistency**:
   - **Note**: If you do not see the Text Message Forwarding option, ensure that you are signed in with the same Apple ID on both your iPhone and your Mac.

4. **Select Your Mac**:
   - Turn on the option for your Mac listed under devices.

5. **Authentication**:
   - If you are not using two-factor authentication, a six-digit activation code will appear on your Mac.
   - Enter this code on your iPhone and tap `Allow` to authenticate.

## Installation
Conda is an open-source package management and environment management system. It functions like a library, where you can easily access and manage collections of software packages without conflicts.

### Installing Python with Homebrew

1. **Install Homebrew**:
   If you do not have Homebrew installed, run this line in your terminal:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**:
   Once Homebrew is installed, you can install Python by running:
   ```
   brew install python
   ```

3. **Verify Python Installation**:
   After installation, you can verify that Python is installed correctly by checking its version:
   ```
   python3 --version
   ```

4. **Set Up Python Environment** (Optional):
   If you need to manage multiple Python environments, you can install `pyenv` using Homebrew:
   ```
   brew install pyenv
   ```
   Then you can create a new environment, for example with Python 3.9:
   ```
   pyenv install 3.9.1
   pyenv global 3.9.1
   ```

5. **Update PATH**:
   Ensure that the Homebrew Python version is used when you run `python` commands by adding the following line to your `.zshrc` file:
   ```
   export PATH="/usr/local/opt/python/libexec/bin:$PATH"
   ```
   Save and close the file. Then, source the `.zshrc` file to update your environment:
   ```
   source ~/.zshrc
   ```

6. **Verify Python Environment**:
   Check that the correct version of Python is being used:
   ```
   python --version
   ```
   This should reflect the version installed via Homebrew or `pyenv`.

7. **Run `run.sh`**:
   To execute the `run.sh` script, which will install required Python packages and run the GUI application, follow these steps:

   - First, ensure that the script has execute permissions. Run the following command in your terminal:
     ```
     chmod +x run.sh
     ```

   - Now, you can run the script using the Python installed by Homebrew. Execute the script by typing:
     ```
     ./run.sh
     ```

   This will install all necessary Python packages specified in `requirements.txt` and then start the GUI application using the Python version installed via Homebrew.

## Usage
1. **Launch the Application**:
   Run the `gui.py` script from the `src` directory to start the Hermes application.

2. **Select a Conversation**:
   The left panel displays a list of your iMessage conversations. Click on a conversation to view its messages.

3. **View Messages**:
   The main panel shows the messages for the selected conversation. You can scroll through the messages and view their contents, including text, images, and attachments.

4. **Search Messages**:
   Use the search bar at the top to search for specific keywords or phrases within the selected conversation. The messages will be filtered based on your search query.

5. **Export Messages**:
   To export messages from a conversation, click on the "Export" button. You can choose to export the entire conversation or select specific messages to export. The exported messages will be saved to a file in a chosen location.

6. **Dump Messages**:
   The "Dump" feature allows you to save all messages from selected participants in a conversation to a separate file. Select the desired participants from the dropdown menu and click "Dump" to generate the file.

7. **Quit the Application**:
   To exit Hermes, simply close the application window or select "Quit" from the application menu.

## Project Structure
The project is structured as follows:
