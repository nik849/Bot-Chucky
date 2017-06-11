import facebook


class FacebookData:
    def __init__(self, token):
        self.token = token
        self._api = facebook.GraphAPI(self.token)

    def get_user_name(self, _id):
        if not isinstance(_id, str):
            raise ValueError('id must be a str')
        user = self._api.get_object(_id)
        return user['first_name'] if user else None


class WeatherData:
    pass
