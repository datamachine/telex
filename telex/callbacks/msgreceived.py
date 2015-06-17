from enum import Enum

from .callback import set_callback_kind, MSG_RECEIVED

def msg_received(func):
    set_callback_kind(func, MSG_RECEIVED)
    return func

def command(command, aliases=None):
    def _command(func):
        def _wrapper(*args, msg, **kwargs):
            if msg.text.startswith(command):
                return func(*args, msg=msg, **kwargs)
        return _wrapper
    return _command

