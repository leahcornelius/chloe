from random import randint
import requests
from urllib.parse import quote

class ApiClient():
    def __init__(self, api_host, api_secret, identifier):
        self.api_host = api_host
        self.api_secret = api_secret
        self.identifier = identifier
        #
        self.token = None
    
    def authenticate(self):
        response = requests.get('http://{}/auth/{}/{}'.format(self.api_host, self.identifier, self.api_secret))
        json = response.json()
        if 'error' not in json:
            self.token = json['token']
        else:
            print("Failed to authenticate with api, got error {}".format(json['error']))
    
    def create_bubble(self, bubble_id, history_length=5, start=""):
        if self.token is None:
            print("Cannot create bubble, not authenticated")
        else:
            response = None
            if start == "":
                response = requests.get('http://{}/create_bubble/{}/{}/{}'.format(self.api_host, quote(bubble_id), history_length, self.token))
            else:
                response = requests.get('http://{}/create_bubble/{}/{}/{}/{}'.format(self.api_host, quote(bubble_id), history_length, self.token, quote(start)))
            json = response.json()
            if 'error' not in json:
                print("Created bubble {}".format(json['bubble_id']))
            else:
                if int(json['error']) == 0:
                    self.authenticate()

                print("Failed to create bubble, got error {}".format(json['error']))

    def bubble_exists(self, bubble_id):
        if self.token is None:
            print("Cannot create bubble, not authenticated")
            return False
        else:
            response = requests.get('http://{}/bubble_info/{}/{}'.format(self.api_host, quote(bubble_id), self.token))
            json = response.json()
            if 'error' not in json:
                return True
            else:
                if int(json['error']) == 0:
                    self.authenticate()
                return False

    def get_response(self, prompt, bubble_id):
        if self.token is None:
            print("Cannot create bubble, not authenticated")
        else:
            response = requests.get('http://{}/get_response/{}/{}/{}'.format(self.api_host, quote(prompt), quote(bubble_id), self.token))
            json = response.json()
            if 'error' not in json:
                return json['response']
            else:
                if int(json['error']) == 0:
                    self.authenticate()
                print("Failed to get response from api, got error {}".format(json['error']))

