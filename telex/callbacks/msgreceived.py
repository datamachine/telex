from enum import Enum

from .callback import validate_signature, set_callback_kind
from .kind import MSG_RECEIVED

def msg_received(func):
    validate_signature(func, keywords=['msg'])
    set_callback_kind(func, MSG_RECEIVED)
    return func

