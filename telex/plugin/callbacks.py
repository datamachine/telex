def on_msg_received(func):
    setattr(func, '_telex_plugin_callback_on_msg_received', True)
    return func

def callback(*, on_msg_recieved):
    def _callback(func):
        if on_msg_recieved:
            func = on_msg_recieved(func)
        return func
    return _callback
    
