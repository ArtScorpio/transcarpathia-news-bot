import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN

# Налаштування логування для відслідковування помилок
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context):
    """Функція для команди /start"""
    welcome_text = (
        "🏔 Вітаємо у боті Закарпатських новин!\n\n"
        "Виберіть опцію з меню нижче:"
    )
    
    # Створюємо кнопки для головного меню
    keyboard = [
        [
            InlineKeyboardButton("📰 Останні новини", callback_data='news'),
            InlineKeyboardButton("🌤 Погода", callback_data='weather')
        ],
        [InlineKeyboardButton("ℹ️ Про бота", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(welcome_text, reply_markup=reply_markup)

def help_command(update, context):
    """Функція для команди /help"""
    help_text = (
        "Доступні команди:\n"
        "/start - Запустити бота\n"
        "/news - Останні новини\n"
        "/weather - Погода в Закарпатті\n"
        "/help - Показати це повідомлення"
    )
    update.message.reply_text(help_text)

def news(update, context):
    """Функція для отримання новин"""
    news_text = (
        "📰 Останні новини Закарпаття:\n\n"
        "1. В Ужгороді відкрили нову пішохідну зону\n"
        "2. На Рахівщині відбудеться фестиваль\n"
        "3. У Мукачеві модернізували лікарню"
    )
    update.message.reply_text(news_text)

def weather(update, context):
    """Функція для отримання погоди"""
    weather_text = (
        "🌤 Погода в Закарпатті:\n\n"
        "Ужгород: +20°C, сонячно\n"
        "Мукачево: +19°C, хмарно\n"
        "Хуст: +18°C, дощ"
    )
    update.message.reply_text(weather_text)

def button(update, context):
    """Обробник натискань на кнопки"""
    query = update.callback_query
    query.answer()  # Відповідаємо на callback

    # Обробляємо різні кнопки
    if query.data == 'news':
        query.edit_message_text(text="📰 Останні новини Закарпаття...")
        # Тут можна додати функцію отримання реальних новин
    elif query.data == 'weather':
        query.edit_message_text(text="🌤 Завантажую погоду...")
        # Тут можна додати функцію отримання реальної погоди
    elif query.data == 'about':
        about_text = (
            "ℹ️ Бот для отримання новин Закарпаття\n"
            "Версія: 1.0\n"
            "Створено: 2024"
        )
        query.edit_message_text(text=about_text)

def error(update, context):
    """Функція для логування помилок"""
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    """Основна функція для запуску бота"""
    # Створюємо об'єкт updater та передаємо йому токен бота
    updater = Updater(TOKEN, use_context=True)

    # Отримуємо диспетчер для реєстрації обробників
    dp = updater.dispatcher

    # Реєструємо обробники команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("weather", weather))

    # Реєструємо обробник кнопок
    dp.add_handler(CallbackQueryHandler(button))

    # Реєструємо обробник помилок
    dp.add_error_handler(error)

    # Запускаємо бота
    updater.start_polling()
    print("Бот запущений...")

    # Тримаємо бота запущеним до переривання
    updater.idle()

if __name__ == '__main__':
    main()
