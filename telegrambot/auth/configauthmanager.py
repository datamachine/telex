from .authmanager import IAuthManager
from configparser import ConfigParser
from pathlib import Path

class ConfigAuthManager(IAuthManager):
    def __init__(self, configfile):
        self.config_path = Path(configfile)
        if not self.config_path.exists():
            self.config_path.touch()

        self.config = ConfigParser()
        self._load_config()

    def _load_config(self):
        with self.config_path.open("r") as f:
            self.config.read(f)

    def get_groups(self):
        return []

    def get_users_from_group(self, group):
        return []

    def set_group(self, group, users):
        return []

    def delete_group(self, group):
        raise []

if __name__ == "__main__":
    c = ConfigAuthManager("testpermissions.conf")

