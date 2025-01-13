import os
import re
import time
import pyautogui
import nest_asyncio
nest_asyncio.apply()
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from pynput.mouse import Controller, Button
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

# Đường dẫn lưu file tải về
UPLOAD_FOLDER = "D:/"

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

COMMANDS = {
    "/introduce": "Giới thiệu về tôi.",
    "/shutdown": "Lệnh tắt máy.",
    "/sleep": "Lệnh vào chế độ ngủ.",
    "/restart": "Lệnh khởi động máy.",
    "/cancel": "Huỷ toàn bộ các lệnh.",

    "/screenshot": "Chụp ảnh màn hình và gửi về máy.",
    "/uploadfile": "Người dùng gửi file để tải lên máy.",
    "/downloadfile": "Người dùng nhập đường dẫn để tải về.",
    "/tasklist": "Danh sách các tiến trình đang chạy.",
    "/systeminfo": "Thông tin hệ thống.",
    "/ipconfig": "Thông tin cấu hình mạng.",
    "/release": "Giải phóng địa chỉ IP hiện tại.",
    "/renew": "Gia hạn địa chỉ IP mới.",
    "/netuser": "Danh sách người dùng trên máy tính.",
    "/whoami": "Tên tài khoản đang đăng nhập.",
    "/hostname": "Hiển thị tên máy tính.",

    "/menu": "Hiển thị danh sách các lệnh.",
    "/playvideo": "Phát video YouTube từ link.",
    "/customvolume": "Điều chỉnh âm lượng.",
    "/controlmouse": "Điều khiển chuột ảo.",
    "/keyboardemulator": "Điều khiển bàn phím ảo.",
    "/deletefile": "Người dùng nhập đường dẫn để xoá file.",
    "/openweb": "Mở các trang web từ lệnh.",
}

# Selenium setup
CHROME_DRIVER_PATH = "ENTER YOUR PATH TO CHROMEDRIVER.EXE"
BRAVE_PATH = "ENTER YOUR PATH TO BRAVE.EXE"

options = Options()
options.binary_location = BRAVE_PATH

# Thêm đường dẫn đến hồ sơ trình duyệt của bạn
USER_DATA_DIR = "ENTER YOUR PATH TO BRAVE USER DATA"
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

options.add_argument("--start-maximized")

# Biến toàn cục cho Selenium
driver = None

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    basic_commands = "\n".join([
        f"🔻 {command}➡️ {desc}" for command, desc in COMMANDS.items()
    ])
    await update.message.reply_text(f"Danh sách các lệnh:\n{basic_commands}")

async def set_command_suggestions(context: ContextTypes.DEFAULT_TYPE):
    commands = [BotCommand(command, desc) for command, desc in COMMANDS.items()]
    await context.bot.set_my_commands(commands)

# Tính năng phát video
async def play_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver

    # Kiểm tra trạng thái của Brave
    brave_running = "brave.exe" in os.popen('tasklist').read()

    if brave_running:
        # Tạo nút chọn hành động (nằm ngang)
        keyboard = [
            [
                InlineKeyboardButton("✅ Có", callback_data="close_brave_and_play"),
                InlineKeyboardButton("❌ Không", callback_data="cancel_playvideo")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Trình duyệt Brave hiện đang mở. Bạn có muốn đóng trình duyệt để phát video không?",
            reply_markup=reply_markup
        )
        return

    # Lấy link từ tham số hoặc tin nhắn
    youtube_url = context.args[0] if context.args else update.message.text.strip()

    # Kiểm tra link YouTube hợp lệ
    youtube_pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+" 
    if not re.match(youtube_pattern, youtube_url):
        await update.message.reply_text("Hãy gửi một link YouTube kèm lệnh /playvideo [link].\nLưu ý trình duyệt phải đang đóng.")
        return

    # Khởi chạy Selenium nếu chưa khởi động
    if driver is None:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

    # Mở link YouTube
    driver.get(youtube_url)
    await update.message.reply_text("Đang phát video trên Brave.")

    # Tạo các nút điều khiển
    keyboard = [
        [InlineKeyboardButton("⏯ Phát / Tạm dừng", callback_data="play_pause"),
         InlineKeyboardButton("⏪ Tua lại 10s", callback_data="rewind")],
        [InlineKeyboardButton("⏩ Tua tới 10s", callback_data="forward"),
        InlineKeyboardButton("❌ Đóng toàn bộ", callback_data="close_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Chọn hành động:", reply_markup=reply_markup)


# Xử lý hành động từ nút
async def handle_brave_controls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver
    query = update.callback_query
    await query.answer()

    if query.data == "close_brave_and_play":
        os.system("taskkill /F /IM brave.exe")
        await query.edit_message_text("Đã đóng Brave. Bạn có thể chạy lại lệnh /playvideo.")
    elif query.data == "cancel_playvideo":
        await query.edit_message_text("Lệnh /playvideo đã bị hủy.")

# Xử lý button điều khiển video
async def video_controls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver
    query = update.callback_query
    await query.answer()

    action = query.data
    if action == "play_pause":
        video_element = driver.find_element(By.TAG_NAME, "video")
        driver.execute_script("arguments[0].paused ? arguments[0].play() : arguments[0].pause();", video_element)
        await query.edit_message_text("Đã chuyển trạng thái phát / tạm dừng.")

    elif action == "rewind":
        driver.execute_script("document.querySelector('video').currentTime -= 10;")
        await query.edit_message_text("Đã tua lại 10 giây.")

    elif action == "forward":
        driver.execute_script("document.querySelector('video').currentTime += 10;")
        await query.edit_message_text("Đã tua tới 10 giây.")

    elif action == "close_all":
        try:
            if driver:
                driver.quit()  # Đóng hoàn toàn driver Selenium
                driver = None  # Đặt lại biến `driver` về None

            # Tắt toàn bộ trình duyệt Brave
            os.system("taskkill /F /IM brave.exe")
            await query.edit_message_text("Đã đóng toàn bộ trình duyệt Brave.")
        except Exception as e:
            await query.edit_message_text(f"Có lỗi xảy ra khi tắt Brave: {e}")

    # Lưu lại và giữ các nút điều khiển video luôn hoạt động (trừ khi đã đóng toàn bộ)
    if action != "close_all":
        keyboard = [
            [InlineKeyboardButton("⏯ Phát / Tạm dừng", callback_data="play_pause"),
             InlineKeyboardButton("⏪ Tua lại 10s", callback_data="rewind")],
            [InlineKeyboardButton("⏩ Tua tới 10s", callback_data="forward"),
            InlineKeyboardButton("❌ Đóng trình duyệt", callback_data="close_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        
# Lệnh điều chỉnh âm lượng
async def custom_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔉 Giảm âm lượng", callback_data="decrease_volume"),
            InlineKeyboardButton("🔊 Tăng âm lượng", callback_data="increase_volume")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Chọn hành động để điều chỉnh âm lượng:", reply_markup=reply_markup)

# Xử lý các nút giảm/tăng âm lượng
async def handle_volume_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    try:
        if action == "decrease_volume":
            os.system("ENTER YOUR PATH TO NIRCMDC.EXE changesysvolume -3277")  # Giảm âm lượng
            await query.edit_message_text("Đã giảm âm lượng.")
        elif action == "increase_volume":
            os.system("ENTER YOUR PATH TO NIRCMDC.EXE changesysvolume 3277")  # Tăng âm lượng
            await query.edit_message_text("Đã tăng âm lượng.")
    except Exception as e:
        await query.edit_message_text(f"Có lỗi xảy ra: {e}")

    # Giữ lại các nút điều khiển sau khi nhấn
    keyboard = [
        [
            InlineKeyboardButton("🔉 Giảm âm lượng", callback_data="decrease_volume"),
            InlineKeyboardButton("🔊 Tăng âm lượng", callback_data="increase_volume")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)

# Tạo menu lệnh
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lệnh giới thiệu
    introduce_command = "🔻 /introduce ➡️ Giới thiệu về tôi."

    # Các nhóm lệnh khác
    system_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/shutdown", "/sleep", "/restart", "/cancel"
        ]
    ])
    image_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/screenshot"
        ]
    ])
    file_io_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/uploadfile", "/downloadfile", "/deletefile"
        ]
    ])
    system_info_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/tasklist", "/systeminfo", "/netuser", "/whoami", "/hostname"
        ]
    ])
    network_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/ipconfig", "/release", "/renew"
        ]
    ])
    entertainment_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/menu", "/playvideo", "/openweb"
        ]
    ])
    utility_commands = "\n".join([
        f"🔻 {command} ➡️ {desc}" for command, desc in COMMANDS.items() if command in [
            "/customvolume", "/controlmouse", "/keyboardemulator"
        ]
    ])

    # Nội dung menu đầy đủ
    menu_text = (
        f"DANH SÁCH CÁC LỆNH\n"
        f"📌 Author: LePhiAnhDev\n\n"
        f"⚡️ GIỚI THIỆU\n{introduce_command}\n\n"
        f"⚡️ HỆ THỐNG LỆNH:\n{system_commands}\n\n"
        f"⚡️ LỆNH HÌNH ẢNH:\n{image_commands}\n\n"
        f"⚡️ I/O FILE:\n{file_io_commands}\n\n"
        f"⚡️ LỆNH THÔNG TIN MÁY:\n{system_info_commands}\n\n"
        f"⚡️ LỆNH HỆ THỐNG:\n{network_commands}\n\n"
        f"⚡️ LỆNH GIẢI TRÍ:\n{entertainment_commands}\n\n"
        f"⚡️ LỆNH TIỆN ÍCH:\n{utility_commands}"
    )

    await update.message.reply_text(menu_text)

# Các lệnh mới
# Tạo đối tượng điều khiển chuột

mouse = Controller()
# Hàm xử lý di chuyển và click chuột
async def handle_mouse_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    # Điều khiển chuột
    if action == "up":
        mouse.move(0, -30)  # Lên
    elif action == "down":
        mouse.move(0, 30)  # Xuống
    elif action == "left":
        mouse.move(-30, 0)  # Trái
    elif action == "right":
        mouse.move(30, 0)  # Phải
    elif action == "left_click":
        mouse.click(Button.left, 1)  # Click chuột trái
    elif action == "right_click":
        mouse.click(Button.right, 1)  # Click chuột phải

    # Tạo bàn phím với các nút điều khiển
    keyboard = [
        [
            InlineKeyboardButton("⬆️ Lên", callback_data="up")
        ],
        [
            InlineKeyboardButton("⬅️ Trái", callback_data="left"),
            InlineKeyboardButton("➡️ Phải", callback_data="right")
        ],
        [
            InlineKeyboardButton("⬇️ Xuống", callback_data="down")
        ],
        [
            InlineKeyboardButton("🖱️ Click trái", callback_data="left_click"),
            InlineKeyboardButton("🖱️ Click phải", callback_data="right_click")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Cập nhật tin nhắn với các nút mới
    await query.edit_message_text(
        text=f"Đã thực hiện thao tác: {action}\nChọn thao tác điều khiển chuột:",
        reply_markup=reply_markup
    )

# Lệnh /controlmouse
async def control_mouse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tạo bàn phím với các nút điều khiển
    keyboard = [
        [
            InlineKeyboardButton("⬆️ Lên", callback_data="up")
        ],
        [
            InlineKeyboardButton("⬅️ Trái", callback_data="left"),
            InlineKeyboardButton("➡️ Phải", callback_data="right")
        ],
        [
            InlineKeyboardButton("⬇️ Xuống", callback_data="down")
        ],
        [
            InlineKeyboardButton("🖱️ Click trái", callback_data="left_click"),
            InlineKeyboardButton("🖱️ Click phải", callback_data="right_click")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Gửi bàn phím đến người dùng
    await update.message.reply_text("Chọn thao tác điều khiển chuột:", reply_markup=reply_markup)

# Hàm hiển thị bàn phím mô phỏng
async def keyboard_emulator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Tạo bàn phím với các phím từ a đến z, dấu cách, backspace, và enter
    keyboard = [
        [KeyboardButton('a'), KeyboardButton('b'), KeyboardButton('c'), KeyboardButton('d'), KeyboardButton('e'),
         KeyboardButton('f'), KeyboardButton('g'), KeyboardButton('h'), KeyboardButton('i'), KeyboardButton('j')],
        [KeyboardButton('k'), KeyboardButton('l'), KeyboardButton('m'), KeyboardButton('n'), KeyboardButton('o'),
         KeyboardButton('p'), KeyboardButton('q'), KeyboardButton('r'), KeyboardButton('s'), KeyboardButton('t')],
        [KeyboardButton('u'), KeyboardButton('v'), KeyboardButton('w'), KeyboardButton('x'), KeyboardButton('y'),
         KeyboardButton('z')],
        [KeyboardButton('space'), KeyboardButton('Backspace'), KeyboardButton('Enter')]  # Dấu cách, backspace, enter
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Đây là bàn phím mô phỏng của bạn.",
        reply_markup=reply_markup
    )

# Xử lý khi người dùng nhấn phím
async def handle_key_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text  # Lấy nội dung từ phím bấm

    # Mô phỏng nhấn phím với pyautogui
    if user_input == 'Backspace':
        pyautogui.press('backspace')  # Mô phỏng nhấn phím Backspace
    elif user_input == 'Enter':
        pyautogui.press('enter')  # Mô phỏng nhấn phím Enter
    elif user_input == 'space':
        pyautogui.press('space')  # Mô phỏng nhấn phím Space
    else:
        pyautogui.typewrite(user_input)  # Mô phỏng nhấn các phím chữ thường

# Ghi kết quả vào file và gửi file
async def run_command_to_file(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str, file_name: str):
    try:
        result = os.popen(command).read()
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        # Ghi kết quả vào file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(result if result.strip() else "Không có dữ liệu để hiển thị hoặc lệnh không hợp lệ.")

        # Gửi file qua Telegram
        with open(file_path, 'rb') as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)

        # Xóa file sau khi gửi
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"Có lỗi xảy ra: {e}")

# Cập nhật các lệnh mới
async def tasklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "tasklist", "tasklist_output.txt")

async def systeminfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "systeminfo", "systeminfo_output.txt")

async def ipconfig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "ipconfig", "ipconfig_output.txt")

async def release(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "ipconfig /renew", "renew_output.txt")

async def renew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "ipconfig /renew", "renew_output.txt")

async def netuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "net user", "netuser_output.txt")

async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "whoami", "whoami_output.txt")

async def hostname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_command_to_file(update, context, "hostname", "hostname_output.txt")

# Lệnh sleep
async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_confirmation(update, context, "sleep")

# Tạo inline button để xác nhận
async def confirm_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = context.user_data.get("action")
    if action == "shutdown":
        os.system("shutdown /s /t 3")
        await query.edit_message_text("Máy sẽ tắt sau 3 giây.")
    elif action == "restart":
        os.system("shutdown /r /t 3")
        await query.edit_message_text("Máy sẽ khởi động lại sau 3 giây.")
    elif action == "cancel":
        os.system("shutdown -a")
        await query.edit_message_text("Đã hủy toàn bộ lệnh.")
    elif action == "sleep":
        try:
            await query.edit_message_text("Máy tính sẽ vào chế độ ngủ ngay bây giờ.")
            time.sleep(2)  # Đợi 2 giây để đảm bảo tin nhắn được gửi
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        except Exception as e:
            await query.edit_message_text(f"Có lỗi xảy ra khi thực hiện lệnh sleep: {e}")
    else:
        await query.edit_message_text("Không có hành động được thực hiện.")

async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Hành động đã bị hủy.")

# Hỏi xác nhận trước khi thực hiện lệnh
async def ask_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, action):
    context.user_data["action"] = action
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận", callback_data="confirm"), InlineKeyboardButton("❎ Hủy", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Bạn có chắc chắn muốn {action} máy không?", reply_markup=reply_markup)

# Lệnh introduce
async def introduce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 DEVELOPER | LÊ PHI ANH\n\n"
        "📩 Contact for Work:\n"
        "- Discord: LePhiAnhDev\n"
        "- Telegram: @lephianh386ht\n"
        "- GitHub: https://github.com/LePhiAnhDev\n\n"
        "🌟 DONATE:\n"
        "💳 1039506134 | LE PHI ANH\n"
        "Vietcombank - Ngân hàng Ngoại Thương Việt Nam\n\n"
    )

# Lệnh shutdown
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_confirmation(update, context, "shutdown")

# Lệnh restart
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_confirmation(update, context, "restart")

# Lệnh cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_confirmation(update, context, "cancel")

# Chụp ảnh màn hình
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    file_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot_path = os.path.join(UPLOAD_FOLDER, file_name)

    try:
        # Lưu ảnh chụp màn hình vào thư mục
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        # Gửi ảnh chụp màn hình đến Telegram
        with open(screenshot_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)

        os.remove(screenshot_path)  # Xóa file ảnh sau khi gửi
        await update.message.reply_text("Đã chụp ảnh màn hình và gửi thành công!")
    except Exception as e:
        await update.message.reply_text(f"Có lỗi xảy ra khi chụp ảnh màn hình: {e}")

# Xử lý lệnh /downloadfile
async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            """
            Hãy nhập đường dẫn file bạn muốn tải về. Ví dụ:
            "/downloadfile D:/example.format"
            """
        )
        return

    # Lấy và lưu đường dẫn file vào context.user_data
    file_path = " ".join(context.args).strip()
    context.user_data["file_path"] = file_path

    # Kiểm tra file có tồn tại hay không
    if os.path.isfile(file_path):
        await update.message.reply_text(f"Đường dẫn hợp lệ. Đang chuẩn bị gửi file: {file_path}")
        try:
            # Gửi file qua Telegram
            with open(file_path, 'rb') as file:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
            await update.message.reply_text(f"File đã được gửi thành công: {file_path}")
        except Exception as e:
            await update.message.reply_text(f"Có lỗi xảy ra khi gửi file: {e}")
    else:
        await update.message.reply_text(f"Không tìm thấy file tại đường dẫn: {file_path}")

# Yêu cầu gửi file
async def upload_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hãy gửi file bạn muốn tải lên. File sẽ được lưu vào ổ D:/")

# Xử lý khi người dùng gửi file
async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Ưu tiên lấy file tài liệu, nếu không thì kiểm tra ảnh hoặc video
    file = message.document or (message.photo[-1] if message.photo else None) or message.video

    if file:
        # Lấy tên file, nếu không có, tạo tên file với đuôi mặc định
        file_name = file.file_name if hasattr(file, "file_name") else f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        # Tải file về máy
        new_file = await file.get_file()
        await new_file.download_to_drive(file_path)

        await update.message.reply_text(f"File {file_name} đã được tải và lưu trong thư mục {UPLOAD_FOLDER}.")
    else:
        await update.message.reply_text("Không nhận được file hợp lệ. Vui lòng thử lại!")

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra người dùng có nhập đường dẫn file không
    if not context.args:
        await update.message.reply_text(
            """
            Hãy nhập đường dẫn file bạn muốn xoá. Ví dụ:
            "/deletefile D:/example.format"
            """
        )
        return

    # Lấy đường dẫn file từ tin nhắn
    file_path = " ".join(context.args).strip()

    # Kiểm tra file có tồn tại không
    if os.path.isfile(file_path):
        try:
            # Xóa file
            os.remove(file_path)
            await update.message.reply_text(f"File tại đường dẫn {file_path} đã được xóa thành công.")
        except Exception as e:
            await update.message.reply_text(f"Có lỗi xảy ra khi xóa file: {e}")
    else:
        await update.message.reply_text(f"Không tìm thấy file tại đường dẫn: {file_path}")

async def open_web(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra người dùng có nhập lệnh mở web không
    if not context.args:
        await update.message.reply_text(
            """
            Hãy nhập lệnh mở web. Ví dụ:
            /openweb chrome.exe "web.format/component"
            """
        )
        return

    # Lấy lệnh từ tin nhắn và xử lý đường dẫn
    command = " ".join(context.args).strip()

    # Xử lý ký tự đặc biệt trong URL nếu có
    command = command.replace('“', '"').replace('”', '"').replace('‘', '"').replace('’', '"')

    try:
        # Thực thi lệnh mở web
        os.system(command)
        await update.message.reply_text(f"Đã thực thi lệnh: {command}")
    except Exception as e:
        await update.message.reply_text(f"Có lỗi xảy ra khi thực thi lệnh: {e}")

# Khởi chạy bot Telegram
async def main():
    # Thay bằng token bot của bạn từ BotFather
    TOKEN = 'ENTER YOUR BOT TOKEN'

    app = ApplicationBuilder().token(TOKEN).build()

    # Gắn các lệnh vào bot
    app.add_handler(CommandHandler("introduce", introduce))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("uploadfile", upload_request))
    app.add_handler(CommandHandler("downloadfile", download_file))
    app.add_handler(CommandHandler("tasklist", tasklist))
    app.add_handler(CommandHandler("systeminfo", systeminfo))
    app.add_handler(CommandHandler("ipconfig", ipconfig))
    app.add_handler(CommandHandler("release", release))
    app.add_handler(CommandHandler("renew", renew))
    app.add_handler(CommandHandler("netuser", netuser))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("hostname", hostname))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("playvideo", play_video))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(video_controls, pattern="^(play_pause|rewind|forward|close_all)$"))
    app.add_handler(CommandHandler("customvolume", custom_volume))
    app.add_handler(CallbackQueryHandler(handle_volume_control, pattern="^(decrease_volume|increase_volume)$"))
    app.add_handler(CallbackQueryHandler(handle_brave_controls, pattern="^(close_brave_and_play|cancel_playvideo)$"))
    app.add_handler(CommandHandler("sleep", sleep))
    app.add_handler(CallbackQueryHandler(confirm_action, pattern="^confirm$"))
    app.add_handler(CallbackQueryHandler(cancel_action, pattern="^cancel$"))
    app.add_handler(CommandHandler("controlmouse", control_mouse))
    app.add_handler(CallbackQueryHandler(handle_mouse_action, pattern="^(up|down|left|right|left_click|right_click)$"))
    app.add_handler(CommandHandler("keyboardemulator", keyboard_emulator))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_key_press))
    app.add_handler(CommandHandler("deletefile", delete_file))
    app.add_handler(CommandHandler("openweb", open_web))

    # Tạo bàn phím gợi ý cho người dùng
    user_keyboard = [
        ["/introduce"],
        ["/shutdown", "/sleep", "/restart", "/cancel"],
        ["/screenshot"],
        ["/uploadfile", "/downloadfile", "/deletefile"],
        ["/tasklist", "/systeminfo", "/netuser", "/whoami", "/hostname"],
        ["/ipconfig", "/release", "/renew"],
        ["/menu", "/playvideo", "/openweb"],
        ["/customvolume", "/controlmouse", "/keyboardemulator"]
    ]

    reply_markup = ReplyKeyboardMarkup(user_keyboard, one_time_keyboard=False, resize_keyboard=True)

    # Set bot command suggestions
    async def set_command_suggestions(context):
        commands = [BotCommand(command, desc) for command, desc in COMMANDS.items()]
        await context.bot.set_my_commands(commands)

    app.post_init = set_command_suggestions

    # Lắng nghe file gửi từ người dùng
    app.add_handler(MessageHandler(filters.ATTACHMENT, upload_file))

    # Chạy bot
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
