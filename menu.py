from app import Worker


def workers_menu():
    return {"text": "Here you can buy workers for your car wash\n"
                    f"1.{school_boy_worker.name}\n\t--💵 Price - {school_boy_worker.price}💸\n\t"
                    f"--Income per minute - {school_boy_worker.income} BYN",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}],

                                                 [{"text": "1️⃣", "callback_data": "BuyWorker1"}]]}}
def main_menu():
    return {"text": "Main Menu",
            "reply_markup": {"inline_keyboard": [[{"text": "💵 Balance", "callback_data": "Balance"},
                                                  {"text": "👷 Workers", "callback_data": "Workers"}],

                                                 [{"text": "🕋 Car wash", "callback_data": "CarWash"}]]}}


def carwash_menu(text: str):
    return {"text": text,
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}]]}}



def balance_menu(text: str):
    return {"text": text,
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"},
                                                  {"text": "₽➡️💸 Exchange Rubles", "callback_data": "ExchangeRubles"}]]}}


school_boy_worker = Worker(price=10, income=1, name="🤓 Schoolboy")
