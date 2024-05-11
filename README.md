<!-- # Hermes - Encrypted iMessage Extractor and Viewer -->

## Overview
Hermes is a tool designed to securely extract and view iMessages from macOS devices.

## Installation
Conda is an open-source package management and environment management system. It functions like a library, where you can easily access and manage collections of books (or in this case, software packages) without conflicts.

### Installing Conda and Setting Up the Environment

1. **Install Conda**: 
   If you do not have Conda installed, run this line in your terminal:
   ```
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. **Give Proper Permissions and Execute the Script**: 
   Run these commands to give the correct permissions and execute the script:
   ```
   chmod +x Miniconda3-latest-Linux-x86_64.sh
   ./Miniconda3-latest-Linux-x86_64.sh
   ```

3. **Follow The Installation Prompts**: 
   The installer will prompt you to review the license agreement. Keep pressing Enter to scroll through the agreement. Type 'yes' to agree to the terms and continue with the installation. After the installation, close and reopen your terminal.

4. **Initialize Conda for zsh**: 
   Open the `.zshrc` file by typing the following command into your terminal:
   ```
   nano ~/.zshrc
   ```
   Add the following line to the end of the file:
   ```
   export PATH="/Users/gibbsgresge/miniconda3/bin:$PATH"
   ```
   Save and close the file. Then, source the `.zshrc` file to update your environment:
   ```
   source ~/.zshrc
   ```
   Initialize Conda:
   ```
   conda init zsh
   ```

5. **Create a Conda Environment**:
   Open your terminal and type the following command to create a new environment named `hermes_env` with Python 3.9:
   ```
   conda create --name hermes_env python=3.9
   ```

6. **Activate the Environment**:
   Activate the newly created environment by running:
   ```
   conda activate hermes_env
   ```
   After activation, you should see `(hermes_env)` in your terminal prompt, indicating that you are currently working within the `hermes_env` environment.

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

## Usage
Run the `gui.py` from the src directory:
```
python src/gui.py
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


