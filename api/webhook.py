import os
import telebot
from flask import Flask, request

# Берем настройки из переменных окружения Vercel
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- Маршрут для обработки вебхуков ---
@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Forbidden', 403

# --- Основная страница для проверки (можно открыть в браузере) ---
@app.route('/', methods=['GET'])
def index():
    return 'Бот предложки работает!', 200

# --- ЛОГИКА БОТА ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь пост, и я передам его админам.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation', 'voice'])
def forward_message(message):
    try:
        # Пересылка сообщения админу
        bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        bot.reply_to(message, "✅ Спасибо! Пост отправлен админам.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Это важно для Vercel: переменная 'app' должна существовать