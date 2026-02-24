# -*- coding: utf-8 -*-
import telebot
import os
import sys
import time
import getpass
import platform
import socket
import uuid
import subprocess
from threading import Thread
import datetime
import threading
import json
import hashlib
import psutil

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = '8689333512:AAE1XY-yWka5xvyN-IIgnH5cy47eB_ug5xU'
ADMIN_ID = 8527578981
# ================================

# ========== ПУТИ И НАСТРОЙКИ ==========
PC_LOCKED = False  # На Render блокировка не работает (нет GUI)
ANTI_TASK_MANAGER = False

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
        KeyboardButton('📸 Скриншот'),
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
        f"✅ Управление компьютером (Render)\n💻 {pc.pc_name}\n\n"
        f"🆔 ID: {pc.pc_id}",
        reply_markup=markup
    )

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
        if platform.system() == "Windows":
            os.system("shutdown /s /t 10")
        else:
            bot.send_message(message.chat.id, "❌ Команда работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔄 Перезагрузить')
def restart(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔄 Перезагрузка через 10 секунд...")
        time.sleep(2)
        if platform.system() == "Windows":
            os.system("shutdown /r /t 10")
        else:
            bot.send_message(message.chat.id, "❌ Команда работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '📸 Скриншот')
def screenshot(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📸 Скриншот работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть окно (ALT+F4)')
def alt_f4(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "❌ ALT+F4 работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '↩️ Отмена (Ctrl+Z)')
def ctrl_z(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "↩️ Ctrl+Z работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '📋 Копировать (Ctrl+C)')
def ctrl_c(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📋 Ctrl+C работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '📌 Вставить (Ctrl+V)')
def ctrl_v(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📌 Ctrl+V работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '⏎ Enter')
def press_enter(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⏎ Enter работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '␣ Пробел')
def press_space(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "␣ Пробел работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '⎋ Esc')
def press_esc(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⎋ Esc работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '⬆️ Вверх')
def up(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⬆️ Стрелки работают только на Windows")

@bot.message_handler(func=lambda m: m.text == '⬇️ Вниз')
def down(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⬇️ Стрелки работают только на Windows")

@bot.message_handler(func=lambda m: m.text == '⬅️ Влево')
def left(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⬅️ Стрелки работают только на Windows")

@bot.message_handler(func=lambda m: m.text == '➡️ Вправо')
def right(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "➡️ Стрелки работают только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔊 Громче')
def volume_up(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔊 Управление звуком работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔉 Тише')
def volume_down(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔉 Управление звуком работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔇 Выключить звук')
def mute(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔇 Управление звуком работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🏠 Рабочий стол (Win+D)')
def show_desktop(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🏠 Win+D работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔒 Заблокировать (Win+L)')
def win_lock(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔒 Win+L работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔄 Переключить окно')
def alt_tab(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔄 Alt+Tab работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🌐 Открыть браузер')
def browser_open(message):
    if message.chat.id == ADMIN_ID:
        if platform.system() == "Windows":
            os.system("start https://google.com")
        else:
            bot.send_message(message.chat.id, "🌐 Открыть браузер можно только на Windows")

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть браузер')
def browser_close(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Закрыть браузер можно только на Windows")

@bot.message_handler(func=lambda m: m.text == '📂 30 вкладок')
def thirty_tabs(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📂 30 вкладок можно открыть только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔍 Поиск')
def search(message):
    if message.chat.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "🔍 Введи запрос (только для Windows):")
        bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text.strip()
    if platform.system() == "Windows":
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        os.system(f"start {url}")
        bot.send_message(message.chat.id, f"🔍 Ищем: {query}")
    else:
        bot.send_message(message.chat.id, "❌ Поиск работает только на Windows")

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
        if platform.system() == "Windows":
            os.system("taskmgr")
            bot.send_message(message.chat.id, "📊 Диспетчер задач открыт")
        else:
            bot.send_message(message.chat.id, "📊 Диспетчер задач работает только на Windows")

# ========== ЗАПУСК ==========
def main():
    print("🤖 Render бот запущен...")
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()