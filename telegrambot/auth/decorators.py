from .authmanager import IAuthManager

# decorators for plugin functions of the form func(self, msg, ...)
def authenticate(users=[], groups=[]):
    def auth_func_wrapper(func):
        def authorized_func(*args, **kwargs):
            return func(*args, **kwargs)

