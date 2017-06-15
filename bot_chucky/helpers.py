""" Helper classes """

from urllib import parse

import facebook
import requests as r
import twitter
import soundcloud


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
        api_url = 'http://api.openweathermap.org' \
            '/data/2.5/weather?q={0}&APPID={1}'.format(city_name, self.token)

        info = r.get(api_url).json()
        return info


class TwitterData:
    """
    Class which collect Twitter data
    """
    def __init__(self, tokens):
        """
        :param tokens: Dictionary of all tokens
                       [consumer_key, consumer_secret, access_token_key,
                       access_token_secret]
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
    def get_stack_answer_by(self, **kwargs):
        params = None
        if len(kwargs) > 1:
            pass
        for key in kwargs.keys():
            params = parse.quote_plus(kwargs.get(key))
        return params


class SoundCloudData:
    """
    Class to gather soundcloud data, tracks etc
    """
    def __init__(self, client_id):
        """
        client_id = Client ID, must be registered
        """
        self.client_id = client_id
        self._api = soundcloud.Client(client_id=self.client_id)

    def resolve_track(self, url):
        """
        Resolve a track name
        :param url: permalink to a track (str)
        """
        try:
            track = self._api.get('/resolve', str(url))

            return {
                'success': True,
                'track': track.id
            }
        except Exception as e:
            return {
                'success': False,
                'detail': 'Error: {0}, Code: {1}'.format(e.message,
                                                         e.response.
                                                         status_code)
            }

    def search(self, artist=None):
        """
        Search for tracks by artist, or artist by track
        :param artist: search by artist, returns tracks and info, type -> str
        """
        self.artist = artist

        if self.artist is not None:
            try:
                artists = self._api.get('/users', q=self.artist)
                tracks = self._api.get('/tracks', q=self.artist)
                return {
                    'success': True,
                    'artists': artists,
                    'tracks': tracks
                }
            except Exception as e:
                return {
                    'success': False,
                    'detail': 'Error: {0}, Code: {1}'.format(e.message,
                                                             e.response.
                                                             status_code)
                }
