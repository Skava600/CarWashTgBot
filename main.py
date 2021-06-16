import json
import pickle
from time import sleep
import threading
import requests
from app import flask_app
from app.models import *
from flask import request
from app import db
from app.config import *
from app.game import get_map_cell
from app.menu import *

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)

maps = {}
cols, rows = 8, 8


def working_loop():
    while True:
        sleep(3600)
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
        processing_button()
    if "message" in request.json:
        if "game" in request.json["message"]:
            return "OK"
        if "text" in request.json["message"]:

            user_id = request.json["message"]["from"]["id"]
            username = request.json["message"]["from"]["username"]
            user = User.query.get(int(user_id))
            chat_id = request.json["message"]["chat"]["id"]
            message_id = request.json["message"]["message_id"]

            if request.json["message"]["text"] == "/play":

                if user.labyrint == None:
                    map_cell = get_map_cell(cols, rows)

                    user_data = {
                        'map': map_cell,
                        'x': 0,
                        'y': 0
                    }

                    maps[chat_id] = user_data
                    user.labyrint = pickle.dumps(user_data)
                    db.session.commit()
                else:
                    maps[chat_id] = pickle.loads(user.labyrint)
                    user_data = maps[chat_id]
                create_menu(get_map_str(user_data['map'], (user_data['x'], user_data['y'])), user_id, game_menu())

            elif user is None:

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
                    create_menu("Main Menu", user_id, main_menu())
                else:
                    send_message(
                        "Похоже вы у нас впервые. Добро пожаловать на вашу автомойку. Пропишите /start чтобы начать",
                        user_id)
            else:

                if user.menu is None:
                    create_menu("Main Menu", user_id, main_menu())

                elif user.menu == "Balance":
                    create_menu(balance_text(user), user_id, balance_menu())

                elif user.menu == "Workers":
                    create_menu(get_workers(), user_id, workers_menu())

                elif user.menu == "CarWash":
                    create_menu(workers_to_string(user.car_wash.workers), user_id, carwash_menu() )

                elif user.menu == "MainMenu":
                    create_menu("Main Menu", user_id, main_menu())

            delete_message(chat_id, message_id)

    return "GOOD"


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
    chat_id = request.json["callback_query"]["message"]["chat"]["id"]
    message_id = request.json["callback_query"]["message"]["message_id"]
    user = User.query.get(int(user_id))
    rdata = request.json["callback_query"]["data"]

    # view rubles and dollar balance
    if rdata == "Balance":

        user.menu = "Balance"
        edit_message(balance_text(user), user_id,message_id,  balance_menu())

    # view all workers on car wash
    elif rdata == "Workers":

        user.menu = "Workers"
        edit_message(get_workers(), user_id, message_id, workers_menu())

    # button of carwash in main menu
    elif rdata == "CarWash":

        user.menu = "CarWash"
        edit_message(workers_to_string(user.car_wash.workers), user_id, message_id, carwash_menu())

    # Button of returning to main menu
    elif rdata == "BackMenu":

        user.menu = "MainMenu"
        edit_message("Main menu", user_id, message_id, main_menu())

    # button exchange rubles in balance menu
    elif rdata == "ExchangeRubles":
        rates = requests.get("https://www.nbrb.by/api/exrates/rates/145")
        user.balance_dollars += user.balance_rubles / rates.json()["Cur_OfficialRate"]
        user.balance_rubles = 0
        db.session.commit()
        edit_message(balance_text(user), user_id, message_id, balance_menu())

    # Buying some worker
    elif "BuyWorker" in rdata:

        if rdata.endswith("1"):
            buy_worker("🤓 Schoolboy", user)
        edit_message(get_workers(), user_id, message_id, workers_menu())
        db.session.commit()
    elif "RechargeBalance" in rdata:

        return

    elif "left" or "right" or "up" or "down" in rdata:
        user_data = load_labyrint(user, chat_id)
        new_x, new_y = user_data['x'], user_data['y']

        if rdata == 'left':
            new_x -= 1
        if rdata == 'right':
            new_x += 1
        if rdata == 'up':
            new_y -= 1
        if rdata == 'down':
            new_y += 1

        if new_x < 0 or new_x > 2 * cols - 2 or new_y < 0 or new_y > rows * 2 - 2:
            return None
        if user_data['map'][new_x + new_y * (cols * 2 - 1)]:
            return None

        user_data['x'], user_data['y'] = new_x, new_y
        user.labyrint = pickle.dumps(user_data)
        if new_x == cols * 2 - 2 and new_y == rows * 2 - 2:
            delete_message(chat_id, message_id)
            send_message("Congratulations! You won. You recieved 5 BYN", chat_id)
            user.balance_rubles += 5
            user.labyrint = None
            db.session.commit()
            return None
        edit_message(get_map_str(user_data['map'], (new_x, new_y)), chat_id, message_id, game_menu())
        db.session.commit()
        return None
    db.session.commit()


def get_workers():
    return "Here you can buy workers for your car wash\n" f"1.{school_boy_worker.name}\n\t--💵 Price - " \
           f"{school_boy_worker.price}💸\n\t"    f"--Income per minute - {school_boy_worker.income} BYN"


def buy_worker(name, user):
    if user.balance_dollars < school_boy_worker.price:
        send_message("Please donate dollars or exchange them", user.id)
    else:
        for worker in user.car_wash.workers:
            if worker.name == name:
                user.balance_dollars -= school_boy_worker.price
                worker.count += 1
                break


def get_map_str(map_cell, player):
    map_str = ""
    for y in range(rows * 2 - 1):
        for x in range(cols * 2 - 1):
            if map_cell[x + y * (cols * 2 - 1)]:
                map_str += "⬛"
            elif (x, y) == player:
                map_str += "🤓"
            else:
                map_str += "⬜"
        map_str += "\n"

    return map_str


def load_labyrint(user, chat_id):
    if user.labyrint == None:
        map_cell = get_map_cell(cols, rows)

        user_data = {
            'map': map_cell,
            'x': 0,
            'y': 0
        }

        maps[chat_id] = user_data
        user.labyrint = pickle.dumps(user_data)
        db.session.commit()
    else:
        maps[chat_id] = pickle.loads(user.labyrint)
        return maps[chat_id]

x = threading.Thread(target=working_loop)
x.start()
flask_app.run()
