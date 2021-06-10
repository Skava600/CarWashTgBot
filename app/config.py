import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://tgbot:123@localhost:5432/tgdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


BOT_TOKEN = os.getenv("BOT_TOKEN", "1720752774:AAFXirHSh_Y-U53s7P7XOFaXHVDfdbAVPu8")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://4cc50c750794.ngrok.io")
TELEGRAM_URL = "https://api.telegram.org"


def main_menu():
    return {"text": "卐卐卐 Главное меню 卐卐卐",
            "reply_markup": {"inline_keyboard": [[{"text": "Balance 💲"  , "callback_data": "Balance"},
                                                  {"text": "Workers", "callback_data": "Workers"}],

                                                 [{"text": "Car wash", "callback_data": "CarWash"}]]}}


def balance_menu(text: str):
    return {"text": text,
            "reply_markup": {"inline_keyboard": [[{"text": "Back", "callback_data": "BackMenu"},
                                                  {"text": "Exchange Rubles", "callback_data": "ExchangeRubles"}]]}}
