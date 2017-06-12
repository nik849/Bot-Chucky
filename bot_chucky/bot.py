import requests as r

from .constants import API_URL
from .exc import BotChuckyInvalidToken, BotChuckyTokenError
from .helpers import FacebookData, WeatherData


class BotChucky:
    def __init__(self, token, open_weather_token=None):
        """
        :param token: Facebook Token, required
        :param open_weather_token: not required
        :param headers: Set default headers for the graph API, default
        :param fb: Instace of FacebookData class, default
        :param weather: Instace of WeatherData class, default
        """
        self.token = token
        self.open_weather_token = open_weather_token
        self.params = {'access_token': self.token}
        self.headers = {'Content-Type': 'application/json'}
        self.fb = FacebookData(self.token)
        self.weather = WeatherData(open_weather_token)

    def send_message(self, _id, text):
        """
        :param _id: User facebook id, type -> str
        :param text: some text, type -> str
        """
        data = {
            'recipient': {'id': _id},
            'message': {'text': text}
        }
        message = r.post(API_URL, params=self.params,
                         headers=self.headers, json=data)
        if message.status_code is not 200:
            return message.text

    def send_weather_message(self, _id, city_name):
        """
        :param _id: User facebook id, type -> str
        :param city_name: Find weather by city name
        :return send_message function,
         send message to a user, with current weather
        """
        if self.open_weather_token is None:
            raise BotChuckyTokenError

        weather_info = self.weather.get_current_weather(city_name)
        if weather_info['cod'] == 401:
            error = weather_info['message']
            raise BotChuckyInvalidToken(error)

        if weather_info['cod'] == '404':
            msg = f'Sorry I can\'t find information ' \
                  f'about weather in {city_name}, ' \
                  f'please check your name of city'
            return self.send_message(_id, msg)

        description = weather_info['weather'][0]['description']
        msg = f'Current weather in {city_name} is: {description}'
        return self.send_message(_id, msg)
