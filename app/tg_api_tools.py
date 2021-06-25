import json

import requests

from app.config import *

def create_menu(message, user_id, menu):
    headers = {"Content-type": "application/json"}
    data = {"chat_id": user_id, "text": message}
    data.update(menu)
    data = json.dumps(data)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, headers=headers, data=data)


def create_button(message, user_id, callback_data):
    headers = {"Content-type": "application/json"}
    data = {"chat_id": user_id,
            "text": message,
            "reply_markup": {"inline_keyboard":
                                 [[{"text": "nig", "callback_data": callback_data}]]}}

    data = json.dumps(data)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, headers=headers, data=data)
    print(res)
    pass


def delete_message(chat_id, message_id):

    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/deleteMessage"
    data = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, data=data)


def edit_message(message, chat_id, message_id, menu):

    reply_murkup = json.dumps(menu["reply_markup"])
    data = {"chat_id": chat_id, "message_id": message_id, "text": message, "reply_markup": reply_murkup}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/editMessageText"
    requests.post(url, data=data)


def send_message(message, user_id):

    data = {"chat_id": user_id, "text": message}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data=data)


def send_payment(invoice):
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendInvoice"
    requests.post(url, data=invoice)
