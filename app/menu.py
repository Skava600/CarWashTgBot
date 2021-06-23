from app import Worker


def workers_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}],

                                                 [{"text": "1️⃣", "callback_data": "BuyWorker1"}]]}}
def main_menu():
    return {"text": "Main Menu",
            "reply_markup": {"inline_keyboard": [[{"text": "💵 Balance", "callback_data": "Balance"},
                                                  {"text": "👷 Workers", "callback_data": "Workers"}],

                                                 [{"text": "🕋 Car wash", "callback_data": "CarWash"}]]}}


def carwash_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}]]}}


def balance_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"},
                                                  {"text": "₽➡️💸 Exchange Rubles", "callback_data": "ExchangeRubles"}],

                                                 [{"text": "Recharge balance", "callback_data": "RechargeBalance"},
                                                  {"text": "Withdraw", "callback_data": "Withdraw"}]]}}


def game_menu():
    return {"reply_markup": {"inline_keyboard": [[{"text": "↑", "callback_data": "up"}],
                                                  [{"text": "←",
                                                   "callback_data": "left"}, {"text": "→",
                                                   "callback_data": "right"}], [{"text": "↓",
                                                   "callback_data": "down"}]]}}


school_boy_worker = Worker(price=10, income=1, name="🤓 Schoolboy")
