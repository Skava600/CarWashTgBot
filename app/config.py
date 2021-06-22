import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://admin:admin@carwashdb:5432/carwashdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


BOT_TOKEN = os.getenv("BOT_TOKEN", "1720752774:AAFXirHSh_Y-U53s7P7XOFaXHVDfdbAVPu8")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://3fcb47ac8e05.ngrok.io")
TELEGRAM_URL = "https://api.telegram.org"
PROVIDER_TOKEN = '410694247:TEST:b374287f-33fe-498b-b8c0-d3733c2e79a3'



