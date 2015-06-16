
def _verify_signature(func, *, kw_only_args=None):
    from inspect import signature, Parameter
    sig = signature(func)
    missing_kwonlyargs = []
    for name in kw_only_args:
        param = sig.parameters.get(name, None)
        if not param or param.kind != Parameter.KEYWORD_ONLY:
            missing_kwonlyargs.append(name) 
    if missing_kwonlyargs:
        raise SyntaxError('"{}: {}" missiong kwonly arg(s): {}'.format(func.__module__, func.__qualname__, ', '.join(missing_kwonlyargs)))

def on_msg_received(func):
    _verify_signature(func, kw_only_args=['msg'])
    setattr(func, '_telex_plugin_callback_on_msg_received', True)
    return func

def callback(*, on_msg_recieved=False):
    def _callback(func):
        if on_msg_recieved:
            func = on_msg_recieved(func)
        return func
    return _callback 

