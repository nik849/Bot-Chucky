""" Helper classes """

import base64
import os
from email.mime.text import MIMEText
from urllib import parse

import facebook
import httplib2
import requests as r
import twitter
from apiclient import discovery
from oauth2client.file import Storage

from bot_chucky.errors import BotChuckyError


class FacebookData:
    def __init__(self, token):
        """
        :param token: Facebook Page token
        :param _api: Instance of the GraphAPI object
        """
        self.token = token
        self._api = facebook.GraphAPI(self.token)

    def get_user_name(self, _id):
        """
        :param _id: find user object by _id
        :return: first name of user, type -> str
        """
        if not isinstance(_id, str):
            raise ValueError('id must be a str')
        user = self._api.get_object(_id)
        return user['first_name'] if user else None


class WeatherData:
    """
    Class which collect weather data
    """
    def __init__(self, api_token):
        """
        :param api_token: Open Weather TOKEN
        """
        self.token = api_token

    def get_current_weather(self, city_name):
        """
        :param city_name: Open weather API, find by city name
        :return dictionary object with information

        for example:

        {'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky'}]}
        """
        api_url = f'http://api.openweathermap.org' \
                  f'/data/2.5/weather?q={city_name}&APPID={self.token}'

        info = r.get(api_url).json()
        return info


class TwitterData:
    """
    Class which collect Twitter data
    """
    def __init__(self, tokens):
        """
        :param tokens: Dictionary of all tokens
                       [consumer_key, consumer_secret, access_token_key, access_token_secret]
                       required to initialize the Twitter Api
        """
        self.api = twitter.Api(
            consumer_key=tokens['consumer_key'],
            consumer_secret=tokens['consumer_secret'],
            access_token_key=tokens['access_token_key'],
            access_token_secret=tokens['access_token_secret']
        )

    def send_tweet(self, status):
        if status:
            try:
                return {
                    'success': True,
                    'tweet': self.api.PostUpdate(status)
                }
            except twitter.error.TwitterError as TWE:
                return {
                    'detail': TWE.message[0]['message'],
                    'success': False
                }


class StackExchangeData:
    """
    Class which collect StackExchange data
    """
    _default_parameters = {
        'order': 'desc',
        'sort': 'activity',
        'site': 'stackoverflow',
    }

    def get_stack_answer_by(self, **kwargs):
        """
        :param kwargs: create a query by arguments
                       for example:
                            tag='Python', will be search by tag
                            title='Update Python', will be search by title
                            and etc.

        :return: an array with links
        """
        if len(kwargs) > 1:
            raise BotChuckyError('The argument must be one')

        for key in kwargs.keys():
            query = kwargs.get(key)
            self._default_parameters.update({key: query})

            if not isinstance(query, str):
                raise TypeError(f'{query} must be a string')

        encode_query = parse.urlencode(self._default_parameters)

        stack_url = f'https://api.stackexchange.com/2.2/search/advanced?' \
                    f'{encode_query}'

        questions = r.get(stack_url).json()
        links = [obj['link'] for obj in questions['items']]
        return links


class GmailData:
    """
    Class which collect Gmail Data
    """
    def __init__(self):
        self.api = self._create_gmail_api()

    def send_mail(self, to, subject, body):
        """
        :param to: Email address of the receiver
        :param subject: Subject of the email
        :param body: Body of the email
        """
        message = self._create_message(to, subject, body)
        try:
            message = self.api.users().messages().send(
                userId='me',
                body=message
            ).execute()
            return {
                "success": True,
                "message": message
            }
        except Exception as e:
            return {
                "success": False,
                "detail": str(e)
            }

    def _create_gmail_api(self):
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        return service

    def _get_credentials(self):
        """Gets valid user credentials from storage.
        :return: Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        return credentials

    def _create_message(self, to, subject, body):
        """
        Create a message for an Email.
        :param to: Email address of the receiver
        :param subject: Subject of the email
        :param body: Body of the email
        """
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        return {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
        }


class ChuckyCustomGenerator:
    """
    Class will allow to add customs unique words/functions
    Warning: not completed yet
    """
    pass
