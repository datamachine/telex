from inspect import signature, Parameter
from enum import Enum, unique
from inspect import signature, Parameter
from functools import partial

@unique
class _CallbackKind(str, Enum):
    _MSG_RECEIVED = '_telex_callback_msgreceived'

MSG_RECEIVED = _CallbackKind._MSG_RECEIVED

_CallBackSignatureRequirements = {}
_CallBackSignatureRequirements[MSG_RECEIVED] = dict(keywords=['msg'])

def _validate_signature(func, *, keywords=None):
    keywords = set(['bot'] + keywords)

    from inspect import signature, Parameter
    sig = signature(func)
    missing_kw_only = []
    for name in keywords:
        param = sig.parameters.get(name, None)
        if not param or param.kind != Parameter.KEYWORD_ONLY:
            missing_kw_only.append(name) 
    if missing_kw_only:
        raise SyntaxError('"{}: {}" missiong kwonly arg(s): {}'.format(func.__module__, func.__qualname__, ', '.join(missing_kw_only)))

def validate_signature(func, kind:_CallbackKind):
    _validate_signature(func, **_CallBackSignatureRequirements[kind])

def set_callback_kind(func, kind:_CallbackKind):
    validate_signature(func, kind)
    setattr(func, '_telex_callback', _CallbackKind(kind))

def callback(kind):
    def _callback(func):
        set_callback_kind(func, kind)
        return func
    return _callback
