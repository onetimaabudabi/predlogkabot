import os
import logging
import telebot
from flask import Flask, request

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение переменных из Vercel
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        except Exception as e:
            logger.error(f"Ошибка обработки обновления: {e}")
            return 'Error', 500
    return 'Forbidden', 403

@app.route('/', methods=['GET'])
def index():
    return 'Бот активен!', 200

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Команда /start от пользователя {message.chat.id}")
    bot.reply_to(message, "Бот готов к работе!")

# Обработчик всех остальных сообщений (текст, фото и т.д.)
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation', 'voice'])
def forward_message(message):
    logger.info(f"Получено сообщение от {message.chat.id}. Тип: {message.content_type}")
    try:
        if not ADMIN_CHAT_ID:
            logger.error("ADMIN_CHAT_ID не задан в переменных окружения!")
            return

        bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        logger.info("Сообщение успешно переслано админу")
    except Exception as e:
        logger.error(f"Критическая ошибка при пересылке: {e}")
        bot.reply_to(message, "Произошла ошибка при отправке поста.")

# Это нужно для работы Vercel
if __name__ == "__main__":
    app.run()