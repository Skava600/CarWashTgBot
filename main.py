import json

import requests

from app import flask_app
from app.models import *
from flask import Flask
from flask import request
from app import db
from app.config import *

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)

main_menu = [[{"text": "Balance", "callback_data": "Balance"},
              {"text": "Workers", "callback_data": "Workers"},
              {"text": "Car wash", "callback_data": "CarWash"}]]


@flask_app.route("/", methods=["POST"])
def receive():
    if "callback_query" in request.json:
        processing_button()
        return "GOOD button"
    user_id = request.json["message"]["from"]["id"]
    username = request.json["message"]["from"]["username"]
    user = User.query.get(int(user_id))

    create_menu("типо главное меню", user_id, main_menu)
    if user is None:
        send_message("Братан ты кто?", user_id)
        user = User(id=int(user_id), username=username, balance_rubles=0, balance_dollars=0)
        car_wash = CarWash(user_id=user_id)
        db.session.commit()
        worker = Worker(car_wash_id=car_wash.id, income=100, name="mother")
        db.session.add(car_wash)
        db.session.add(worker)
        db.session.add(user)

    else:
        send_message(f"ЗДАРОВА, {user.username}, твой баланс {user.balance_rubles}", user_id)
    reques = request.json["message"]
    db.session.commit()
    return "GOOD"


def create_menu(message, user_id, menu):
    headers = {"Content-type": "application/json"}
    buttons = [[]]

    data = {"chat_id": user_id,
            "text": message,
            "reply_markup": {"inline_keyboard": menu}}

    data = json.dumps(data)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, headers=headers, data=data)

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


def send_message(message, user_id):
    data = {"chat_id": user_id, "text": message}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data=data)

def processing_button():
    user_id = request.json["callback_query"]["from"]["id"]
    username = request.json["callback_query"]["from"]["username"]
    user = User.query.get(int(user_id))
    rdata = request.json["callback_query"]["data"]
    if rdata == "Balance":
        send_message("Balance", user_id)
    elif rdata == "Workers":
        send_message("Workers", user_id)
    elif rdata == "CarWash":
        send_message("CarWash", user_id)

flask_app.run()
