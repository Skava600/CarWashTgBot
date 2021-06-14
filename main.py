import json
from time import sleep
import threading
import requests
from app import flask_app
from app.models import *
from flask import Flask
from flask import request
from app import db
from app.config import *
from menu import workers_menu, balance_menu, main_menu, carwash_menu, school_boy_worker

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)


def working_loop():
    while True:
        sleep(60)
        users = User.query.all()
        for user in users:

            income = 0
            for worker in user.car_wash.workers:
                income += worker.income * worker.count
            user.balance_rubles += income
        db.session.commit()


@flask_app.route("/", methods=["POST"])
def receive():


    if "callback_query" in request.json:
        chat_id = request.json["callback_query"]["message"]["chat"]["id"]
        message_id = request.json["callback_query"]["message"]["message_id"]
        url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        processing_button()
    if "message" in request.json:

        if "text" in request.json["message"]:

            user_id = request.json["message"]["from"]["id"]
            username = request.json["message"]["from"]["username"]
            user = User.query.get(int(user_id))
            chat_id = request.json["message"]["chat"]["id"]
            message_id = request.json["message"]["message_id"]
            url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/deleteMessage"
            data = {"chat_id": chat_id, "message_id": message_id}
            if user is None:

                if request.json["message"]["text"] == "/start":
                    user = User(id=int(user_id), username=username, balance_rubles=0, balance_dollars=0)
                    car_wash = CarWash(user_id=user_id)
                    db.session.add(user)

                    db.session.commit()
                    db.session.add(car_wash)
                    db.session.commit()
                    worker = Worker(car_wash_id=car_wash.id, income=100, name="👩 mother", count=1, price=5)
                    db.session.add(Worker(price=school_boy_worker.price, income=school_boy_worker.income,
                                          car_wash_id=user.car_wash.id, name=school_boy_worker.name, count=0))
                    db.session.add(worker)

                    db.session.commit()
                    create_menu(user_id, main_menu())
                else:
                    send_message(
                        "Похоже вы у нас впервые. Добро пожаловать на вашу автомойку. Пропишите /start чтобы начать",
                        user_id)
            else:
                if user.menu is None:
                    create_menu(user_id, main_menu())
                elif user.menu == "Balance":
                    create_menu(user_id, balance_menu(balance_text(user)))
                elif user.menu == "Workers":
                    create_menu(user_id, workers_menu())
                elif user.menu == "CarWash":
                    create_menu(user_id, carwash_menu(workers_to_string(user.car_wash.workers)))
                elif user.menu == "MainMenu":
                    create_menu(user_id, main_menu())

    requests.post(url, data=data)
    return "GOOD"


def create_menu(user_id, menu):
    headers = {"Content-type": "application/json"}
    data = {"chat_id": user_id}
    data.update(menu)
    db.session.commit()
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


def send_message(message, user_id):
    data = {"chat_id": user_id, "text": message}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data=data)


def workers_to_string(workers):
    text = "Your workers:\n"
    income = 0
    i = 1
    for worker in workers:
        income += worker.income * worker.count
        if worker.count != 0:
            text += f"{i}. {worker.name}\n💰 income: {worker.income},\n count: {worker.count}.\n"
            i += 1
    text += f"Total income: {income}"
    return text


def balance_text(user):
    return f"Balance rubles BYN: {user.balance_rubles:.2f},"f" \nBalance dollars 💸: {user.balance_dollars:.2f}"


def processing_button():
    user_id = request.json["callback_query"]["from"]["id"]
    user = User.query.get(int(user_id))
    rdata = request.json["callback_query"]["data"]

    # view rubles and dollar balance
    if rdata == "Balance":

        user.menu = "Balance"
        create_menu(user_id, balance_menu(balance_text(user)))

    # view all workers on car wash
    elif rdata == "Workers":

        user.menu = "Workers"
        create_menu(user_id, workers_menu())

    # button of carwash in main menu
    elif rdata == "CarWash":

        user.menu = "CarWash"
        create_menu(user_id, carwash_menu(workers_to_string(user.car_wash.workers)))

    # Button of returning to main menu
    elif rdata == "BackMenu":

        user.menu = "MainMenu"
        create_menu(user_id, main_menu())

    # button exchange rubles in balance menu
    elif rdata == "ExchangeRubles":
        rates = requests.get("https://www.nbrb.by/api/exrates/rates/145")
        user.balance_dollars += user.balance_rubles / rates.json()["Cur_OfficialRate"]
        user.balance_rubles = 0
        db.session.commit()
        create_menu(user_id, balance_menu(balance_text(user)))

    # Buying some worker
    elif "BuyWorker" in rdata:

        if rdata.endswith("1"):
            buy_worker("🤓 Schoolboy", user)
        db.session.commit()
    db.session.commit()


def buy_worker(name, user):
    if user.balance_dollars < school_boy_worker.price:
        send_message("Please donate dollars or exchange them", user.id)
    else:
        for worker in user.car_wash.workers:
            if worker.name == name:
                user.balance_dollars -= school_boy_worker.price
                worker.count += 1
                break


x = threading.Thread(target=working_loop)
x.start()
flask_app.run()
