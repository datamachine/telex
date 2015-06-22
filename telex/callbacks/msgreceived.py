import re
from enum import Enum
from functools import wraps
from .callback import callback, MSG_RECEIVED

def msg_received(func):
    @callback(MSG_RECEIVED)
    @wraps(func)
    def _msg_received(*args, bot, msg, **kwargs):
        return func(*args, bot=bot, msg=msg, **kwargs)
    return _msg_received

def command(cmd, aliases=None):
    def _command(func):
        @msg_received
        @wraps(func)
        def _wrapper(*args, bot, msg, **kwargs):
            if msg.text.startswith('{}{}'.format(bot.pfx, cmd)):
                return func(*args, bot=bot, msg=msg, **kwargs)
        return _wrapper
    return _command
    
def expand(expr):
    def _expand(func):
        @msg_received
        @wraps(func)
        def _wrapper(*args, bot, msg, **kwargs):
            match = re.search(expr, msg.text)
            if match:
                keyword_args = kwargs.copy()
                keyword_args.update(match.groupdict())
                return func(*args, bot=bot, msg=msg, **keyword_args)
        return _wrapper
    return _expand
