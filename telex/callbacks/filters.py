
def match(expr):
    import re
    prog = re.compile(expr)
    def match_wrapper(func):
        def do_match(*args, msg, **kwargs):
            if prog.match(msg.text):
                return func(*args, msg=msg, **kwargs)
            return None
        return do_match
    return match_wrapper

