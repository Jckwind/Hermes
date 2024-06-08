<!-- # Hermes - Encrypted iMessage Extractor and Viewer -->

## Prerequisites
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


## Overview
Hermes is a tool designed to securely extract and view iMessages from macOS devices.

## Installation
Conda is an open-source package management and environment management system. It functions like a library, where you can easily access and manage collections of books (or in this case, software packages) without conflicts.

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

## Features
- **GUI Viewer**: View messages through a user-friendly interface.

### Prerequisites
- Python 3.x
- Access to macOS with iMessages

### Setup
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Hermes.git
   ```

2. Navigate to the Hermes directory:
   ```
   cd Hermes
   ```



3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```


4. Before Running the Application 
    To ensure the Cursor IDE functions correctly, it requires Full Disk Access. This access allows the program to retrieve data from your iMessages. Please follow these steps to grant the necessary permissions:

        - Open the Settings app from your applications folder.
        - Navigate to Privacy and Security.
        - Scroll to Full Disk Access and click to open it.
        - Locate the Cursor IDE in the list and check the box to grant it permission.


## Usage
Run the `gui.py` from the src directory:

```
python src/gui.py
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


