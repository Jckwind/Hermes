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

## Features
- **GUI Viewer**: Intuitive interface for browsing and searching messages
- **Secure Extraction**: Safely extract iMessages from macOS devices
- **Export Functionality**: Export conversations or selected messages


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
   To execute the `run.sh` script, which will install required Python packages and run the GUI application:

   - Ensure the script has execute permissions:
     ```
     chmod +x run.sh
     ```

   - Run the script:
     ```
     ./run.sh
     ```

   This will install necessary Python packages from `requirements.txt` and start the GUI application.

## Usage
1. **Launch the Application**:
   Run `./run.sh` from the terminal to start Hermes.

2. **Select Conversations**:
   In the left panel, click on conversations to add them to the processing list.

3. **Export**:
   Click the "Export" button when your list is complete. Name the subdirectory when prompted. Exports are saved to `Documents/exported_chats`.

4. **Search**:
   Use the search bar to find specific keywords or phrases within selected conversations.

5. **Google Drive Export**:
   To export to Google Drive, follow the instructions in `model/README.md`.

6. **Quit**:
   Close the application window to exit Hermes.

## License
This project is open-source and available under the MIT License.

## Contributing
- [Contributing](#contributing)

## Troubleshooting
- [Troubleshooting](#troubleshooting)

## Changelog
- [Changelog](#changelog)

## Contact
For support or inquiries, please contact gibbsngresge@gmail.com.