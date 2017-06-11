import facebook


def get_user_fb_name(token, _id):
    if not isinstance(id, str):
        raise ValueError('id must be a str')
    fb = facebook.GraphAPI(token)
    return fb.get_object(_id)
