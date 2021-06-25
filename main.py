import pickle
from time import sleep
import threading
from app import flask_app
from app.models import *
import random
from flask import request
from app import db
from app.game import get_map_cell
from app.menu import *
from app.tg_api_tools import *

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)

maps = {}
cols, rows = 8, 8


@flask_app.route("/", methods=["POST"])
def receive():
    log(request.json)
    if "pre_checkout_query" in request.json:
        processing_payment()
    if "callback_query" in request.json:
        processing_button()
    if "message" in request.json:
        chat_id = request.json["message"]["chat"]["id"]
        message_id = request.json["message"]["message_id"]
        if "text" in request.json["message"]:

            user_id = request.json["message"]["from"]["id"]
            username = request.json["message"]["from"]["username"]
            user = User.query.get(int(user_id))


            if user is None:

                if request.json["message"]["text"] == "/start":
                    user = User(id=int(user_id), username=username, balance_rubles=0, balance_dollars=0)
                    car_wash = CarWash(user_id=user_id)
                    db.session.add(user)

                    db.session.commit()
                    db.session.add(car_wash)
                    db.session.commit()
                    worker = Worker(car_wash_id=car_wash.id, income=5, name="👩 mother", count=1, price=5)
                    db.session.add(Worker(price=school_boy_worker.price, income=school_boy_worker.income,
                                          car_wash_id=user.car_wash.id, name=school_boy_worker.name, count=0))

                    db.session.add(worker)
                    log(f"{username}: {user.id} registered")
                    db.session.commit()
                    create_menu("Main Menu", user_id, main_menu())
                else:

                    send_message(
                        "Looks like you are a new one in car wash. Type /start to begin",
                        user_id)
            else:

                if request.json["message"]["text"] == "/play":

                    if user.labyrint is None:
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
                    return "good"

                if request.json["message"]["text"] == "/menu":
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


def processing_payment():

    data = {"pre_checkout_query_id": request.json["pre_checkout_query"]["id"], "ok": True}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/answerPreCheckoutQuery"
    user_id = request.json["pre_checkout_query"]["from"]["id"]
    requests.post(url, data=data)
    user = User.query.get(int(user_id))
    user.balance_dollars += float(request.json["pre_checkout_query"]["total_amount"] / 100)
    db.session.commit()


def processing_button():

    user_id = request.json["callback_query"]["from"]["id"]
    chat_id = request.json["callback_query"]["message"]["chat"]["id"]
    message_id = request.json["callback_query"]["message"]["message_id"]
    user = User.query.get(int(user_id))
    rdata = request.json["callback_query"]["data"]

    # view rubles and dollar balance
    if rdata == "Balance":

        user.menu = "Balance"
        edit_message(balance_text(user), user_id, message_id,  balance_menu())

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
        log(f"{user.username}:{user.id} exchanged rubles")
        edit_message(balance_text(user), user_id, message_id, balance_menu())

    # Buying some worker
    elif "BuyWorker" in rdata:

        if rdata.endswith("1"):
            buy_worker("🤓 Schoolboy", user)
        db.session.commit()
        return
    elif "Withdraw" in rdata:
        user.balance_dollars = 0
        db.session.commit()

    elif "Lottery" in rdata:

        if "Lottery" == rdata:

            user.Menu = "Lottery"
            edit_message("Lotteries🧾:\n"
                         f"1. Great Lottery:Every minute. Contribution - {simple_lottery.contribution}. Winning all bank\n"
                         f"2. WorkeR Lottery Every hour. Contribution - {worker_lottery.contribution}. Winning worker with stats: income - "
                         f"{worker_lottery.contribution }", chat_id, message_id, lottery_menu())
            return "good"

        elif rdata.endswith("1"):

            lottery = Lottery.query.filter(Lottery.name == simple_lottery.name).first()
        elif rdata.endswith("2"):

            lottery = Lottery.query.filter(Lottery.name == worker_lottery.name).first()
        if user.balance_dollars >= lottery.contribution:

            for userLot in lottery.users:

                if userLot.user_id == user_id:

                    send_message("You already take part in this lottery", user_id)
                    return "already exist in lottery"
            send_message(f"You successfully registered at {lottery.name}", user_id)
            user.balance_dollars -= lottery.contribution
            lottery.users.append(UserLotteryAssociation(lottery_id=lottery.id, user_id=user_id))
            db.session.commit()
        else:

            send_message("Not enough money for lottery", user_id)
        return "good"


    elif "RechargeBalance" in rdata:
        invoice = {
            'chat_id': chat_id,
            'title': 'Receive dollars',
            'description': 'Donate dollars to receive in-game dollars',
            'payload': '5$',
            'provider_token': PROVIDER_TOKEN,
            'start_parameter': 'start',
            'photo_url': 'https://im0-tub-by.yandex.net/i?id=32f08b8c351ca4a23dd2e61d4ebdb589&n=13',
            'photo_width': 600,
            'photo_height': 600,
            'currency': 'USD',
            'prices': json.dumps([{'label': '5#', 'amount': 500}])
        }
        send_payment(invoice)

    elif ("left" or "right" or "up" or "down") == rdata:
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
            log(f"{user.username}:{user.id} completed labyrint")
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


def log(message:str):
    print(message)


def buy_worker(name, user):
    if user.balance_dollars < school_boy_worker.price:

        send_message("Please donate dollars or exchange them", user.id)
    else:
        join_request = db.session.query(CarWash, Worker).outerjoin(CarWash, Worker.car_wash_id == CarWash.id).\
            filter(CarWash.user_id == user.id, Worker.name == name).first()
        if join_request is None:
            worker = None
            carwash = None
        else:
            carwash, worker = join_request

        if carwash is None and worker is None:
            db.session.add(Worker(price=school_boy_worker.price, income=school_boy_worker.income,
                                  car_wash_id=user.car_wash.id, name=school_boy_worker.name, count=1))
            return
        user.balance_dollars -= worker.price
        worker.count += 1
        log(f"{user.username}:{user.id} bought a {name}")


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


def async_tools_start():
    threading_lottery_1 = threading.Thread(target=a_simple_lottery,
                                           kwargs={'lottery_prot': simple_lottery, 'interval': 60})
    threading_lottery_1.start()
    threading_lottery_2 = threading.Thread(target=a_simple_lottery,
                                           kwargs={'lottery_prot': worker_lottery, 'interval': 360})
    threading_lottery_2.start()
    threading_income = threading.Thread(target=working_loop)
    threading_income.start()


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


def a_simple_lottery(lottery_prot, interval):
    while True:

        if len(Lottery.query.filter(Lottery.name == lottery_prot.name).all()) == 0:
            db.session.add(lottery_prot)
            db.session.commit()
        lottery = Lottery.query.filter(Lottery.name == lottery_prot.name).first()
        if len(lottery.users) > 1:
            winner = random.randint(0, len(lottery.users) - 1)
            user = User.query.get(int(lottery.users[winner].user_id))
            if lottery_prot.name == simple_lottery.name:
                jackpot = len(lottery.users) * lottery.contribution

                user.balance_dollars += jackpot
                send_message(f"Congratulations 👏. You won {jackpot} dollars", user.id)
            elif lottery_prot.name == worker_lottery.name:
                send_message(f"Congratulations 👏. You won 👷 Super Worker. Check your carwash", user.id)
                join_request = db.session.query(CarWash, Worker).outerjoin(CarWash, Worker.car_wash_id == CarWash.id). \
                    filter(CarWash.user_id == user.id, Worker.name == "👷 Super Worker").first()
                if join_request is None:
                    worker = None
                    carwash = None
                else:
                    carwash, worker = join_request

                if carwash is None and worker is None:
                    db.session.add(Worker(car_wash_id=user.car_wash.id, income=lottery.contribution, name="👷 Super Worker", count=1, price=0))
                    return
                worker.count += 1

            log(f"{user.username}:{user.id} won a {lottery.name}")
            UserLotteryAssociation.query.filter(UserLotteryAssociation.lottery_id == lottery.id).delete()
            Lottery.query.filter(Lottery.name == lottery_prot.name).delete()
            db.session.add(lottery_prot)
            db.session.commit()
        else:
            for user_as in lottery.users:
                send_message(f"{lottery_prot.name} postponed on {interval / 60} minutes", user_as.user_id)
        sleep(interval)


async_tools_start()
flask_app.run(host='0.0.0.0')
