# Telegram Bot Control Computer V2

## Introduction
This project is a Telegram bot that uses Selenium, Chromedriver, Nircmd and system commands to automate tasks such as browser control, system command execution, screenshot capture, file download, mouse and keyboard emulator. The following guide will help you set up, configure, and package the project.

---

## System Requirements
1. Latest [Python](https://www.python.org/downloads/) version
2. [Brave](https://brave.com/) or Google Chrome browser
3. Download [Chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) using the Stable channel and make sure it is compatible with your browser version.
4. [Nircmd](https://www.nirsoft.net/utils/nircmd-x64.zip) 64 bit version

---

## Installation and Configuration Guide

### 1. Obtain **Telegram Bot Token**
1. Open Telegram and search for **@BotFather**.
2. Type the command `/newbot` to create a new bot.
3. Follow the instructions, provide a name and username for your bot.
4. Once created, you will receive a **Token**. Save this token and add it to the line `TOKEN = 'ENTER YOUR BOT TOKEN'` in the source file.

---

### 2. Install Required Libraries
Run the following command to install the necessary third-party libraries:
`pip install pyautogui pillow nest_asyncio selenium pyinstaller pynput python-telegram-bot`

---

### 3. Download and Configure Chromedriver
1. Determine the version of Brave/Chrome you are using:
   - Open your browser and navigate to `Settings > About Brave/Chrome` to check the version.
2. Download the compatible Chromedriver from the [official website](https://googlechromelabs.github.io/chrome-for-testing/).
3. Extract Chromedriver and save the path to the `chromedriver.exe` file.

Enter this path in the line:
CHROME_DRIVER_PATH = "CHROME_DRIVER_PATH = "ENTER YOUR PATH TO CHROMEDRIVER.EXE"

---

### 4. Configure Brave or Chrome
1. Determine the installation path of your browser:
   - **Brave**: Typically located at `C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe`.
   - **Chrome**: Typically located at `C:/Program Files/Google/Chrome/Application/chrome.exe`.
2. Enter this path in the line:
BRAVE_PATH = "ENTER YOUR PATH TO BRAVE.EXE"

---

### 5. Configure Browser User Data
1. User data contains information like cookies and browser settings, which helps the bot open your correct account.
2. The default paths are usually:
   - **Brave**: `C:/Users/<Your Username>/AppData/Local/BraveSoftware/Brave-Browser/User Data`.
   - **Chrome**: `C:/Users/<Your Username>/AppData/Local/Google/Chrome/User Data`.
3. Enter this path in the line:
USER_DATA_DIR = "ENTER YOUR PATH TO BRAVE USER DATA"

---

### 6. Download and Configure NirCmd
1. Download NirCmd from the official website.
2. Extract the contents and note the path to nircmdc.exe.
3. Enter this path in the following lines of the function handle_volume_control:
os.system("ENTER YOUR PATH TO NIRCMDC.EXE changesysvolume -3277")  # Decrease volume
os.system("ENTER YOUR PATH TO NIRCMDC.EXE changesysvolume 3277")   # Increase volume


### 7. Add **Telegram Token**
Copy the token you obtained from **@BotFather** and enter it in the line:
TOKEN = 'ENTER YOUR BOT TOKEN'

---

### 8. Running the Project
1. Open a terminal in the directory containing the source file.
2. First, check in the IDE. If everything is set up correctly, the bot will start listening for commands on Telegram. Then, it's time to package the bot.
3. You can also run the command to start the bot in the terminal (note that the terminal running the command must be in the same folder as the TelegramBotControlComputer.py file):
`python TelegramBotControlComputer.py`

---

### 9. Packaging the Project with PyInstaller
1. Package the source file into a standalone `.exe` file:
`pyinstaller --onefile TelegramBotControlComputer.py`
2. The executable file will be saved in the `dist/TelegramBotControlComputer.exe` directory.

---

## Notes
1. Ensure **Chromedriver** matches your browser version. Check again if Selenium fails to launch.
2. Make sure the paths (`CHROME_DRIVER_PATH`, `BRAVE_PATH`, `USER_DATA_DIR`, `LINE 203`, `LINE 206`, `TOKEN`) are entered correctly.
3. Do not share your **Telegram Token** publicly to avoid unauthorized control of your bot.
4. If you get error message "Telegram.error.Timeout: Timed out". You just need to Revoke old token and Renew new token, then everything will be fine.

---

## Author
**Lê Phi Anh**  

## Contact for Work
- Discord: LePhiAnhDev  
- Telegram: @lephianh386ht  
- GitHub: [LePhiAnhDev](https://github.com/LePhiAnhDev)
