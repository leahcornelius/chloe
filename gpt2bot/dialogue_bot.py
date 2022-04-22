import random
import string
from gpt2bot.api_client import ApiClient
from random import randint


def create_api():
    host = input("Enter API host (ip:port): ")
    if host == "":
        host = "192.168.1.146:5000"
    secret = input("Enter API secret: ")
    if secret == "":
        secret = "qwertybob_key01"
    api = ApiClient(host, secret, "client-{}".format(randint(0, 200)))
    api.authenticate()
    return api


def run_dialoge_bot(**params):
    api = create_api()
    bubble_id = ''.join(random.choice(string.ascii_lowercase)
                        for i in range(30))
    print("----------------------------------------------------------")
    print("Connected to API")
    print("You can now enter the starting prompt and i will talk to myself")
    print("To exit, press CTRL-C")
    print("----------------------------------------------------------")

    start = input("Enter Starting prompt > ")
    api.create_bubble(bubble_id + "1", start=start)
    api.create_bubble(bubble_id + "2")
    turn = False
    last_message = start
    print("Bot 1 > ", last_message)

    while True:
        if turn:
            # bubble_id + 1
            last_message = api.get_response(last_message, bubble_id + "1")
        else:
            last_message = api.get_response(last_message, bubble_id + "2")

        print("Bot {} > {}".format(1 if turn else 2, last_message))
        turn = not turn

