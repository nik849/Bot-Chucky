import requests as r

from .constants import API_URL
from .helpers import FacebookData


class BotChucky:
    def __init__(self, token):
        self.token = token
        self.params = {'access_token': self.token}
        self.headers = {'Content-Type': 'application/json'}
        self.fb = FacebookData(self.token)

    def send_message(self, _id, text):
        data = {
            'recipient': {'id': _id},
            'message': {'text': text}
        }
        message = r.post(API_URL, params=self.params,
                         headers=self.headers, json=data)
        if message.status_code is not 200:
            return message.text
