from flask import Flask, jsonify
import threading
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем новую версию для Render
import pc_client_render as pc_client

app = Flask(__name__)
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
    global bot_running
    bot_running = True
    try:
        pc_client.main()
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot_running = False

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)