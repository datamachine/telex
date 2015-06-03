from functools import wraps

def group_only(f):
    """ Only allow this msg to be processed if it was sent to a group """
    @wraps(f)
    def wrapper(*args, **kwargs):
        msg = args[1]
        if msg.dest.type_name != "chat":
                return None
        return f(*args, **kwargs)
    return wrapper


def pm_only(f):
    """ Only allow this msg to be processed if it was sent to the bot """
    @wraps(f)
    def wrapper(*args, **kwargs):
        msg = args[1]
        if msg.dest.type_name != "user":
            return None
        return f(*args, **kwargs)
    return wrapper

