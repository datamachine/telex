
import os
from configparser import ConfigParser
import regex
import sys

PERMISSION_FILE="permissions.conf"

class IAuthManager:
    def set_group(self, plugin_name, group, user_id):
        raise NotImplementedError(self.__class__.__name__ + ".set_group")
    
    def unset_group(self, plugin_name, group, user_id):
        raise NotImplementedError(self.__class__.__name__ + ".unset_group")

    def clear_group(self, plugin_name, group, user_id):
        raise NotImplementedError(self.__class__.__name__ + ".clear_group")

    def in_group(self, plugin_name, group, user_id):
        raise NotImplementedError(self.__class__.__name__ + ".in_group")

class ConfigAuthManager(IAuthManager):
    def __init__(self):
        self.config = ConfigParser()
        if not os.path.exists(PERMISSION_FILE):
            self.write_config()
        self.config.read(PERMISSION_FILE)

    def __get_users_from_group(self, plugin_name, group, user_id):
        try:
            return [uid.strip() for uid in self.config[plugin_name][group].split(",")]
        except KeyError as e:
            print(e)
        except:
            print(sys.exc_info()[0])
        return []

    def write_config(self):
        with open(PERMISSION_FILE, "w") as f:
            self.config.write(f)

    def in_group(self, plugin_name, group, user_id):
        self.config
        

AuthManager = ConfigAuthManager()

# wrapper for plugin functions of the form func(self, msg, matches)
def authenticate(users=[], groups=[]):
    def auth_func_wrapper(func):
        def authorized_func(*args, **kwargs):
            return func(*args, **kwargs)

