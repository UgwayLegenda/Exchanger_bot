import logging
import os

# Создаем директорию logs, если она не существует
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка логирования
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)