
def rematch(func):
    import re
    def do_match(*args, msg, **kwargs):
        if re.match('/echo', msg.text):
            return func(*args, msg=msg, **kwargs)
        return None
    return do_match

