from inspect import signature, Parameter
from .kind import _CallbackKind, _validate_signature

def set_callback_kind(func, kind:_CallbackKind):
    setattr(func, '_telex_callback', _CallbackKind(kind))

def validate_signature(func, *, keywords=None):
    from inspect import signature, Parameter
    sig = signature(func)
    missing_kw_only = []
    for name in keywords:
        param = sig.parameters.get(name, None)
        if not param or param.kind != Parameter.KEYWORD_ONLY:
            missing_kw_only.append(name) 
    if missing_kw_only:
        raise SyntaxError('"{}: {}" missiong kwonly arg(s): {}'.format(func.__module__, func.__qualname__, ', '.join(missing_kw_only)))


