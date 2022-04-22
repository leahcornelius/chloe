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


def run_console_bot(**params):
    api = create_api()
    bubble_id = ''.join(random.choice(string.ascii_lowercase)
                        for i in range(30))
    api.create_bubble(bubble_id)
    print("----------------------------------------------------------")
    print("Connected to API and created bubble context ({})".format(bubble_id))
    print("You can now talk to me, to exit press Ctrl-C")
    print("To restart the conversation/clear my memory type /reset")
    print("----------------------------------------------------------")
    while True:
        message = input("User > ")
        if message == "/reset":
            print("---- RESET HISTORY ----")
            bubble_id = ''.join(random.choice(string.ascii_lowercase)
                                for i in range(30))
            api.create_bubble(bubble_id)
            continue

        response = api.get_response(message, bubble_id)
        print("Bot > {}".format(response))


