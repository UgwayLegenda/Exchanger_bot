from dotenv import load_dotenv
import os

load_dotenv()  # Загрузка переменных из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")