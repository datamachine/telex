from enum import Enum

from .callback import *

@callback(kind=MSG_RECEIVED)
def on_msg_received(func):
    on_msg_received._telex_validate_signature(func)
    setattr(func, '_telex_plugin_callback_on_msg_received', True)
    return func

