from .__init__ import AuthManager

# decorators for plugin functions of the form func(self, msg, ...)
def authorize(users=[], groups=[], peer_type=[]):
    def auth_decorator(f):
        def auth_wrapper(*args, **kwargs):
            msg = args[1]
            src_user = msg.src.id
            if src_user in users:
                return f(*args, **kwargs)
            if AuthManager.groups_has_user(groups, src_user):
                return f(*args, **kwargs)
            return "You are not authorized to run this command"
        return auth_wrapper
    return auth_decorator

if __name__ == "__main__":
    print("...")
