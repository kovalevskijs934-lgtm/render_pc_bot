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
        KeyboardButton('🌐 Открыть браузер'),
        KeyboardButton('❌ Закрыть браузер'),
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
    bot.send_message(message.chat.id, "📸 Скриншот работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🌐 Открыть браузер')
def browser_open(message):
    if message.chat.id == ADMIN_ID:
        if platform.system() == "Windows":
            os.system("start https://google.com")
        else:
            bot.send_message(message.chat.id, "🌐 Открыть браузер можно только на Windows")

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть браузер')
def browser_close(message):
    bot.send_message(message.chat.id, "❌ Закрыть браузер можно только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔍 Поиск')
def search(message):
    if message.chat.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "🔍 Введи запрос:")
        bot.register_next_step_handler(msg, process_search)

def process_search(message):
    query = message.text.strip()
    bot.send_message(message.chat.id, f"🔍 Поиск: {query} (работает только на Windows)")

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
