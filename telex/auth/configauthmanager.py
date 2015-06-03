from .authmanager import IAuthManager
from configparser import ConfigParser
from pathlib import Path

class ConfigAuthManager(IAuthManager):
    def __init__(self, configfile):
        self.config_path = Path(configfile)
        self.config = ConfigParser()

        if not self.config_path.exists():
            self.config_path.touch()
        else:
            self._load_config()

        if not self.config.has_section("groups"):
            self.config.add_section("groups")
            self.config.set("groups", "admins", "")
            self._save_config()

    def _load_config(self):
        with self.config_path.open("r") as f:
            self.config.read_file(f)

    def _save_config(self):
        with self.config_path.open("w") as f:
            self.config.write(f)

    def set_group(self, group, users):
        if not self.config.has_section("groups"):
            self.config["groups"] = {}
        self.config["groups"][group] = ','.join(map(str, users))
        self._save_config()

    def remove_group(self, group):
        if self.config.has_section("groups") and self.config["groups"].has_option[group]:
            del self.config["groups"][group]

    def get_groups(self):
        if self.config.has_section("groups"):
            return self.config.options("groups") 
        return []

    def get_users_from_group(self, group):
        if self.config.has_section("groups"):
            return list(map(int,self.config.get("groups", group, raw=True, fallback="").split(",")))
        return []
        

if __name__ == "__main__":
    c = ConfigAuthManager("testpermissions.conf")
    print(c.get_groups())
    print(c.get_users_from_group("admins"))
    c.set_group("admins", ["1111"])
    print(c.get_groups())
    print(c.get_users_from_group("admins"))
    c.add_user_to_group("admins", "2344")
    print(c.get_groups())
    print(c.get_users_from_group("admins"))
    print(c.group_has_user("admins", "1111"))
    c.remove_user_from_group("admins", "1111")
    print(c.group_has_user("admins", "1111"))
    print(c.get_groups())
    print(c.get_users_from_group("admins"))
