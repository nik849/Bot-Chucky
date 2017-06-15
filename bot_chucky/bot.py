import requests as r

from .constants import API_URL
from .errors import BotChuckyInvalidToken, BotChuckyTokenError
from .helpers import FacebookData, TwitterData, WeatherData, SoundCloudData


class BotChucky:
    def __init__(self, token, open_weather_token=None,
                 tw_consumer_key=None, tw_consumer_secret=None,
                 tw_access_token_key=None, tw_access_token_secret=None,
                 soundcloud_id=None):
        """
        :param token: Facebook Token, required
        :param open_weather_token: not required
        :param tw_consumer_key: Twitter Consumer Key, not required
        :param tw_consumer_secret: Twitter Consumer Secret, not required
        :param tw_access_token_key: Twitter Access Token Key, not required
        :param tw_access_token_secret: Twitter Access Token Secret,
        not required
        :param headers: Set default headers for the graph API, default
        :param fb: Instace of FacebookData class, default
        :param weather: Instace of WeatherData class, default
        :param twitter: Instance of TwitterData class, default
        :param soundcloud_id: SoundCloud Access Token, not required
        """
        self.token = token
        self.open_weather_token = open_weather_token
        self.params = {'access_token': self.token}
        self.headers = {'Content-Type': 'application/json'}
        self.fb = FacebookData(self.token)
        self.weather = WeatherData(open_weather_token)
        self.twitter_tokens = {
            'consumer_key': tw_consumer_key,
            'consumer_secret': tw_consumer_secret,
            'access_token_key': tw_access_token_key,
            'access_token_secret': tw_access_token_secret
        }
        self.twitter = TwitterData(self.twitter_tokens)
        self.soundcloud_id = soundcloud_id
        self.soundcloud = SoundCloudData(self.soundcloud_id)

    def send_message(self, id_: str, text):
        """
        :param  id_: User facebook id, type -> str
        :param text: some text, type -> str
        """
        data = {
            'recipient': {'id': id_},
            'message': {'text': text}
        }
        message = r.post(API_URL, params=self.params,
                         headers=self.headers, json=data)
        if message.status_code is not 200:
            return message.text

    def send_weather_message(self, id_: str, city_name: str):
        """
        :param id_: User facebook id, type -> str
        :param city_name: Find weather by city name
        :return send_message function, send message to a user,
        with current weather
        """
        if self.open_weather_token is None:
            raise BotChuckyTokenError('Open Weather')

        weather_info = self.weather.get_current_weather(city_name)
        if weather_info['cod'] == 401:
            error = weather_info['message']
            raise BotChuckyInvalidToken(error)

        if weather_info['cod'] == '404':
            msg = 'Sorry I cant find information ' \
                  'about weather in {}, '.format(city_name)

            return self.send_message(id_, msg)

        description = weather_info['weather'][0]['description']
        msg = 'Current weather in {} is: {}'.format(city_name, description)
        return self.send_message(id_, msg)

    def send_tweet(self, status: str):
        """
        :param status: Tweet text, type -> str
        """
        if not all(self.twitter_tokens.values()):
            raise BotChuckyTokenError('Twitter')

        reply = self.twitter.send_tweet(status)

        if reply['success']:
            return 'I have placed your tweet with status {}.'.format(status)

        return 'Twitter Error: {}.'.format(reply["detail"])

    def send_soundcloud_message(self, artist: str):
        """
        :param artist: artist to search for, type -> str
        """
        if not self.soundcloud_id:
            raise BotChuckyTokenError('SoundCloud')
        result = self.soundcloud.search(artist)

        if result['success']:
            tracks_from_artist = list(result['tracks'].title)
            msg = 'SoundCloud found {}, \n' \
                        'Track Listing: {}'.format(result['artists'],
                                               tracks_from_artist)

            return self.send_message(id_, msg)

        msg = 'SoundCloud Error: {}'.format(result['detail'])

        return self.send_message(id_, msg)
