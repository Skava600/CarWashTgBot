import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://tgbot:123@localhost:5432/tgdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


BOT_TOKEN = os.getenv("BOT_TOKEN", "1720752774:AAFXirHSh_Y-U53s7P7XOFaXHVDfdbAVPu8")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://f4ec3266d124.ngrok.io")
TELEGRAM_URL = "https://api.telegram.org"