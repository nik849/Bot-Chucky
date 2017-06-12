""" Exception classes """


class BotChuckyTokenError(Exception):
    def __str__(self):
        return 'Seems like you missing add' \
               ' \'Open Weather\' token to the ChuckyBot class'


class BotChuckyInvalidToken(Exception):
    pass
