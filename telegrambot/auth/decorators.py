from .__init__ import AuthManager

# decorators for plugin functions of the form func(self, msg, ...)
def authorize(users=[], groups=[]):
    def auth_decorator(f):
        def auth_wrapper(*args, **kwargs):
            msg = args[1]
            user = msg.src.id
            if user in users:
                return f(*args, **kwargs)
            for group in groups:
                if AuthManager.group_has_user(group, user):
                    return f(*args, **kwargs)
            return "You are not authorized to run this command"
        return auth_wrapper
    return auth_decorator

if __name__ == "__main__":
    print("...")
