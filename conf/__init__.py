import os


REDIS_URL = None # "rediss://:6380/0"
TELEGRAM_URL = None # "https://api.telegram.org//"
TELEGRAM_CHANNEL = None # "@"

if not any(REDIS_URL, TELEGRAM_URL, TELEGRAM_CHANNEL):
    REDIS_URL = os.environ["REDIS_URL"]
    TELEGRAM_URL = os.environ["TELEGRAM_URL"]
    TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]
