import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import pytz
import json

# Додайте цей код в bot.py
def test_post(self):
    """Тестова публікація для перевірки роботи бота"""
    try:
        test_message = "🔄 Тестове повідомлення. Перевірка роботи бота."
        self.updater.bot.send_message(
            chat_id=self.channel_id,
            text=test_message,
            parse_mode='HTML'
        )
        print("Тестове повідомлення відправлено успішно!")
    except Exception as e:
        print(f"Помилка при відправці: {e}")

# Імпортуємо налаштування
from config import TOKEN, CHANNEL_ID, NEWS_SOURCES, POSTING_HOURS, POST_INTERVAL

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot_log.txt'
)
logger = logging.getLogger(__name__)

class NewsBot:
    def __init__(self, token, channel_id):
        """Ініціалізація бота"""
        self.updater = Updater(token=token, use_context=True)
        self.channel_id = channel_id
        self.news_sources = NEWS_SOURCES
        self.posted_news = self.load_posted_news()
        
        # Додавання обробників команд
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("status", self.status))
        dp.add_handler(CallbackQueryHandler(self.button))
        dp.add_error_handler(self.error)

    def load_posted_news(self):
        """Завантаження історії опублікованих новин"""
        try:
            with open('posted_news.json', 'r', encoding='utf-8') as file:
                return set(json.load(file))
        except FileNotFoundError:
            return set()

    def save_posted_news(self):
        """Збереження історії опублікованих новин"""
        with open('posted_news.json', 'w', encoding='utf-8') as file:
            json.dump(list(self.posted_news), file)

    def start(self, update, context):
        """Обробка команди /start"""
        keyboard = [
            [InlineKeyboardButton("📰 Останні новини", callback_data='latest')],
            [InlineKeyboardButton("ℹ️ Статус", callback_data='status')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Вітаю! Я бот для публікації новин Закарпаття.',
            reply_markup=reply_markup
        )

    def help(self, update, context):
        """Обробка команди /help"""
        help_text = (
            "Доступні команди:\n"
            "/start - Запустити бота\n"
            "/status - Перевірити статус бота\n"
            "/help - Показати це повідомлення"
        )
        update.message.reply_text(help_text)

    def status(self, update, context):
        """Обробка команди /status"""
        status_text = (
            f"📊 Статус бота:\n"
            f"Опубліковано новин: {len(self.posted_news)}\n"
            f"Активні джерела: {len(self.news_sources)}\n"
            f"Час роботи: {self.get_uptime()}"
        )
        update.message.reply_text(status_text)

    def button(self, update, context):
        """Обробка натискань кнопок"""
        query = update.callback_query
        query.answer()
        
        if query.data == 'latest':
            self.show_latest_news(query)
        elif query.data == 'status':
            self.show_status(query)

    def error(self, update, context):
        """Обробка помилок"""
        logger.warning(f'Update {update} caused error {context.error}')

    def get_news_from_source(self, source_name, url):
        """Отримання новин з вказаного джерела"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            # Парсинг в залежності від джерела
            if 'zakarpattya.net.ua' in url:
                news_blocks = soup.find_all('div', class_='news-title')
                for block in news_blocks[:5]:
                    link = block.find('a')
                    if link and link.get('href'):
                        title = link.text.strip()
                        news_url = link['href']
                        if news_url not in self.posted_news:
                            news_items.append({
                                'title': title,
                                'url': news_url,
                                'source': source_name
                            })
            # Додайте парсинг для інших джерел...

            return news_items
        except Exception as e:
            logger.error(f"Помилка при отриманні новин з {source_name}: {e}")
            return []

    def format_news_post(self, news):
        """Форматування новини для публікації"""
        return f"""📰 {news['title']}

🔍 Джерело: {news['source']}
👉 {news['url']}

#новини #закарпаття #новиниЗакарпаття"""

    def post_news(self):
        """Публікація новин у канал"""
        all_news = []
        for source_name, url in self.news_sources.items():
            news_items = self.get_news_from_source(source_name, url)
            all_news.extend(news_items)

        for news in all_news:
            if news['url'] not in self.posted_news:
                try:
                    formatted_post = self.format_news_post(news)
                    self.updater.bot.send_message(
                        chat_id=self.channel_id,
                        text=formatted_post,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    self.posted_news.add(news['url'])
                    self.save_posted_news()
                    time.sleep(POST_INTERVAL)
                except Exception as e:
                    logger.error(f"Помилка при публікації новини: {e}")

    def schedule_news(self):
        """Планування публікації новин"""
        for hour in POSTING_HOURS:
            schedule.every().day.at(f"{hour:02d}:00").do(self.post_news)

    def get_uptime(self):
        """Отримання часу роботи бота"""
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return str(datetime.timedelta(seconds=uptime_seconds))

    def run(self):
        """Запуск бота"""
        self.schedule_news()
        logger.info("Бот запущений. Чекаю на розклад публікацій...")
        print("Бот запущений. Чекаю на розклад публікацій...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Бот зупинений користувачем")
            print("Бот зупинений користувачем")

def main():
    """Головна функція"""
    bot = NewsBot(TOKEN, CHANNEL_ID)
    bot.run()

if __name__ == '__main__':
    main()
