from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
import configparser


PLUGIN_CONFIG_NAME="plugins.conf"

class TelegramPluginManager(ConfigurablePluginManager):
    def __init__(self, bot):
        self.config = configparser.ConfigParser()
        super().__init__(configparser_instance = self.config, 
                         config_change_trigger = lambda :self.save_config(),
                         directories_list = ["plugins"] )

        self.bot = bot

    def save_config(self):
        print("Saving plugins config...")
        with open(PLUGIN_CONFIG_NAME, 'w') as f:
            self.config.write(f)
            return True
        return False

