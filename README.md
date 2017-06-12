# Bot-Chucky

Python bot which able to work with messenger of facebook

[![Build Status](https://travis-ci.org/MichaelYusko/Bot-Chucky.svg?branch=master)](https://travis-ci.org/MichaelYusko/Bot-Chucky)

Installation
=================================
```
not uploaded yet on pypi
```

Usage
=================================
Chucky provide the next thigs:

 * Send message
 * Send weather information
 
the list will be expanded.

### Flask Example
```python
from flask import Flask, request
from bot_chucky.bot import BotChucky

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
                    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
                    # Get a user text
                    text = data['entry'][0]['messaging'][0]['message']['text']
                    # Send message to the user
                    bot.send_message(sender_id, text) 
                     
                if event.get('delivery'):
                    pass
                
    return 'ok', 200

if __name__ == '__main__':
    app.run(debug=True)
```
### Weather information
```python
@app.route('/', methods=['POST'])
def handle_messages():
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            for event in entry.get('messaging'):
                if event.get('message'):
                    # Get a user id
                    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
                    # User city for which we will search weather information
                    city = data['entry'][0]['messaging'][0]['message']['text']
                    # Send message with weather information to the user
                    bot.send_weather_message(sender_id, city)
                
                if event.get('delivery'):
                    pass
    
    return 'ok', 200
```

Contribution
=================================
1. Fork or clone repository
2. Create a branch such as **feature/bug/refactor** and send a Pull request

P.S. Feel free to make a PR;)