# Telegram Bot Control Computer

## Introduction
This project is a Telegram bot that uses Selenium to automate tasks such as browser control, system command execution, screenshot capture, and file download. The following guide will help you set up, configure, and package the project.

---

## System Requirements
1. Python
2. [Brave](https://brave.com/) or Google Chrome browser
3. Chromedriver compatible with your browser version
4. [NirCmd](https://www.nirsoft.net/utils/nircmd.html)

---

## Installation and Configuration Guide

### 1. Obtain **Telegram Bot Token**
1. Open Telegram and search for **@BotFather**.
2. Type the command `/newbot` to create a new bot.
3. Follow the instructions and provide a name and username for your bot.
4. Once created, you will receive a **Token**. Save this token and add it to the line `TOKEN = ""` in the source file.

---

### 2. Install Required Libraries
Run the following command to install the necessary third-party libraries:
`pip install pyautogui pillow nest_asyncio selenium python-telegram-bot`

---

### 3. Download and Configure Chromedriver
1. Determine the version of Brave/Chrome you are using:
   - Open your browser and navigate to `Settings > About Brave/Chrome` to check the version.
2. Download the compatible Chromedriver from the [official website](https://chromedriver.chromium.org/downloads).
3. Extract Chromedriver and save the path to the `chromedriver.exe` file.

Enter this path in the line:
CHROME_DRIVER_PATH = "D:/path/to/chromedriver.exe"

---

### 4. Configure Brave or Chrome
1. Determine the installation path of your browser:
   - **Brave**: Typically located at `C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe`.
   - **Chrome**: Typically located at `C:/Program Files/Google/Chrome/Application/chrome.exe`.
2. Enter this path in the line:
BRAVE_PATH = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

---

### 5. Configure Browser User Data
1. User Data contains user information like cookies and browser settings.
2. The default paths are usually:
   - **Brave**: `C:/Users/<Your Username>/AppData/Local/BraveSoftware/Brave-Browser/User Data`.
   - **Chrome**: `C:/Users/<Your Username>/AppData/Local/Google/Chrome/User Data`.
3. Enter this path in the line:
USER_DATA_DIR = "C:/Users/<Your Username>/AppData/Local/BraveSoftware/Brave-Browser/User Data"

---

### 6. Download and Configure NirCmd
1. Download NirCmd from the official website.
2. Extract the contents and note the path to nircmdc.exe.
3. Enter this path in the following lines of the function handle_volume_control:
os.system("<Enter the path to nircmdc.exe> changesysvolume -3277")  # Decrease volume
os.system("<Enter the path to nircmdc.exe> changesysvolume 3277")   # Increase volume


### 7. Add **Telegram Token**
Copy the token you obtained from **@BotFather** and enter it in the line:
TOKEN = "your-telegram-bot-token"

---

### 8. Running the Project
1. Open a terminal in the directory containing the source file.
2. Run the command:
`python TelegramBotControlComputer.py`
3. If everything is set up correctly, the bot will start listening for commands on Telegram.

---

### 9. Packaging the Project with PyInstaller
1. Install PyInstaller:
`pip install pyinstaller`
2. Package the source file into a standalone `.exe` file:
`pyinstaller --onefile TelegramBotControlComputer.py`
3. The executable file will be saved in the `dist/TelegramBotControlComputer.exe` directory.

---

## Notes
1. Ensure **Chromedriver** matches your browser version. Check again if Selenium fails to launch.
2. Make sure the paths (`CHROME_DRIVER_PATH`, `BRAVE_PATH`, `USER_DATA_DIR`, `nircmdc.exe`) are entered correctly.
3. Do not share your **Telegram Token** publicly to avoid unauthorized control of your bot.
4. If you get error message "Telegram.error.Timeout: Timed out". You just need to Revoke old token and Renew new token, then everything will be fine.

---

## Author
**Lê Phi Anh**  

## Contact for Work
- Discord: LePhiAnhDev  
- Telegram: @lephianh386ht  
- GitHub: [LePhiAnhDev](https://github.com/LePhiAnhDev)
