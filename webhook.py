import os
from flask import Flask, request
import telebot

# Vercel автоматически подтянет эти переменные из настроек, которые мы укажем позже
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Маршрут, на который Telegram будет присылать сообщения
@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Forbidden', 403

# Стартовая страница (просто чтобы проверить, что сервер работает)
@app.route('/', methods=['GET'])
def index():
    return 'Бот предложки успешно запущен на Vercel!', 200

# Логика бота: команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь сюда свой пост, мем или идею, и я передам это админам 🚀")

# Логика бота: пересылка контента
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation', 'voice'])
def forward_message(message):
    try:
        # Пересылаем пост в чат админов
        bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        # Подтверждаем пользователю
        bot.reply_to(message, "Спасибо! Твой пост отправлен в предложку.")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")
