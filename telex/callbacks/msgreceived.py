from enum import Enum

from .callback import set_callback_kind, MSG_RECEIVED

def msg_received(func):
    set_callback_kind(func, MSG_RECEIVED)
    return func

def command(cmd, aliases=None):
    def _command(func):
        def _wrapper(*args, bot, msg, **kwargs):
            if msg.text.startswith('{}{}'.format(bot.pfx, cmd)):
                return func(*args, bot=bot, msg=msg, **kwargs)
        return _wrapper
    return _command

