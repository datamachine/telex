from functools import wraps

from .callbacks import callback

def match(expr):
    import re
    prog = re.compile(expr)
    def _match(func):
        def match_wrapper(*args, msg, **kwargs):
            if prog.match(msg.text):
                return func(*args, msg=msg, **kwargs)
            return None
        return match_wrapper
    return _match

def command(command, *, aliases=[]):
    def _command(func):
        setattr(func, '_telex_filter_command', True)
        def command_wrapper(*args, msg, **kwargs):
            return func(*args, msg=msg, **kwargs)
        return command_wrapper
    return _command

