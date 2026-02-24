# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import threading
import os
import sys
import time

# Добавляем путь к папке, где лежит бот
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем твоего бота (предполагаем, что основной файл называется pc_client.py)
import pc_client

app = Flask(__name__)

# Флаг, что бот запущен
bot_running = False

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot": "active" if bot_running else "starting",
        "message": "Bot is running on Render!"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

def run_bot():
    """Запускает твоего бота в отдельном потоке"""
    global bot_running
    bot_running = True
    try:
        # Передаём управление боту
        pc_client.main()
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot_running = False

# Запускаем бота при старте сервера
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)