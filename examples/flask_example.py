from flask import Flask, request

from bot_chucky.bot import BotChucky
from bot_chucky.utils import get_sender_id, get_user_text

token = 'YOUR_FACEBOOK_PAGE_TOKEN'

# Init a Flask app
app = Flask(__name__)

# Create an instance of Chucky object
# If you want to send weather information
# You need to set your Open Weather API key
bot = BotChucky(token, open_weather_token='YOUR_OPEN_WEATHER_TOKEN')


@app.route('/', methods=['GET'])
def handle_verification():
    # Verify your facebook PAGE.
    return request.args['hub.challenge']


@app.route('/', methods=['POST'])
def handle_messages():
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            for event in entry.get('messaging'):
                if event.get('message'):
                    # Get a user id
                    sender_id = get_sender_id(data)

                    # Get a user text
                    text = get_user_text(data)

                    # NOTICE: if you want send message to a user
                    # use send_message function
                    # if you want to send a weather info
                    # use only send_weather_info function
                    bot.send_message(sender_id, text)
                    bot.send_weather_message(sender_id, text)

                if event.get('delivery'):
                    pass

    return 'ok', 200


if __name__ == '__main__':
    app.run(debug=True)
