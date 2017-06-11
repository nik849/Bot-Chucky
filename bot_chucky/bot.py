from .utils import get_user_fb_name
import json
import requests as r
from .constants import API_URL


class BotChucky:
    def __init__(self, token):
        self.token = token
        self.params = {'access_token': self.token}
        self.headers = {'Content-Type': 'application/json'}

    def send_message(self, _id, text):
        data = {
            'recipient': {'id': _id},
            'message': {'text': text}
        }
        print(r.post(API_URL, params=self.params, headers=self.headers, json=data).content)
