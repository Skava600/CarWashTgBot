import logging
import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://tgbot:123@localhost:5432/tgdb"#"postgresql://admin:admin@carwashdb:5432/carwashdb"#
    SQLALCHEMY_TRACK_MODIFICATIONS = False


BOT_TOKEN = os.getenv("BOT_TOKEN", "1720752774:AAFiYNyLsAL3ecNxyFX4ZNmR88r6N7SJg5U")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://ff8df8d3d444.ngrok.io")
TELEGRAM_URL = "https://api.telegram.org"
PROVIDER_TOKEN = '410694247:TEST:b374287f-33fe-498b-b8c0-d3733c2e79a3'

lg = logging.getLogger('sqlalchemy.engine')



