from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
import configparser


PLUGIN_CONFIG_NAME="plugins.conf"

class TelegramPluginManager(ConfigurablePluginManager):
    def __init__(self, bot):
        self.config = configparser.ConfigParser()
        self.config.read(PLUGIN_CONFIG_NAME)

        super().__init__(configparser_instance = self.config, 
                         config_change_trigger = lambda :self.save_config(),
                         directories_list = ["plugins"] )

        self.bot = bot

    def save_config(self):
        with open(PLUGIN_CONFIG_NAME, 'w') as f:
            self.config.write(f)
            return True
        return False

    def activatePluginByName(self, plugin_name, category_name="Default", save_state=True):
        plugin_object = super().activatePluginByName(plugin_name, category_name, save_state)

        if plugin_object:
            plugin_object.set_bot(self.bot)
            plugin_object.set_plugin_manager(self)
            return plugin_object
        
        return None
    
        
