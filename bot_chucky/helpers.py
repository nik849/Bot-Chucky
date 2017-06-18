""" Helper classes """

import base64
import os
from collections import Callable
from email.mime.text import MIMEText
from urllib import parse

import facebook
import httplib2
import requests as r
import twitter
from googleapiclient import discovery, errors
from oauth2client.file import Storage

from bot_chucky.errors import BotChuckyError
from bot_chucky.utils import split_text


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
    Visit https://developers.google.com/gmail/api/quickstart/python
    to generate your credentials for Gmail API to compose mails.
    """
    def __init__(self, credentials_path='gmail-credentials.json'):
        """
        :param credentials_path: Gmail API Credentials Path. default ->
                                 './gmail-credentials.json', type -> str
        """
        self.credentials_path = credentials_path
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
        except errors.HttpError as error:
            return {
                "success": False,
                "detail": str(error)
            }

    def _create_gmail_api(self):
        try:
            credentials = self._get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('gmail', 'v1', http=http)
            return service
        except AttributeError:
            return ''

    def _get_credentials(self):
        """Gets valid user credentials from storage.
        :return: Credentials, the obtained credential.
        """
        if not os.path.exists(self.credentials_path):
            raise BotChuckyError('Invalid Path to API Credentials File.')

        return Storage(self.credentials_path).get()

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


class ChuckyCustomGenerator(Callable):
    """
    warnings:: Class not completed yet
    description:: Class will allow to add customs unique words/functions,
                  If user want to create own realization of the bot,
                  he should use the CustomGenerator class.
    future:: It will be imported into BotChucky class.

    :Example:
          # first create custom functions
          def hello_python():
            return 'Hello Python!'

          def news_python():
            return 'Python news!'

          my_config = {
            '#Python': hello_python
          }

          # Create instance of ChuckyGenerator
          bot = ChuckyCustomGenerator()
          bot.config = my_config

          # If we get some text from messenger
          # And we pass an argument to the bot

          my_message = 'Hello I want to learn #Python'
          bot(my_message)

          The bot will return the result of a custom function: 'Hello Python!'

          Update our config, and add topics:

          # Add topics
          # For example
          # If we got text with #Python and 'bye' word
          my_config = {
            '#Python': {'news': news_python}
           }
          bot.config = my_config

          my_message = 'Hey #Python, and send me your news'
          bot(my_message)

          bot will return the result of a custom function: 'Python news!'
    """
    config = {}

    def get_text(self, text):
        return split_text(text)

    @property
    def config_keys(self):
        return self.config.keys()

    def check_and_run(self, text):
        func = None
        for key in self.config_keys:
            if key not in text:
                msg = 'Sorry, could you repeat please?'
                return msg
            if key in text:
                func = self.config.get(key)
            if isinstance(func, Callable):
                return func()
            else:
                for topic in self.config.get(key):
                    if topic in text:
                        func = self.config[key][topic]
                        return func()

    def __call__(self, text, **kwargs):
        text = self.get_text(text)
        return self.check_and_run(text)

    def __str__(self):
        return f'{self.__class__.__name__}' \
               f'(Your config: {self.config})'
