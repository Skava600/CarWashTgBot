import requests

from app import flask_app
from flask import Flask
from flask import request
from app.config import *

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)


@flask_app.route("/", methods=["POST"])
def receive():
    print(request.json)
    user_id = request.json["message"]["from"]["id"]
    send_message("Добро пожаловать в автомойку", user_id)
    return "GOOD"


def send_message(message, user_id):
    data = {"chat_id" : user_id, "text" : message}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data=data)
flask_app.run()