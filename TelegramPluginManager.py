from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
import configparser


PLUGIN_CONFIG_NAME="plugins.conf"

def __get_section_name(category_name, plugin_name):
    if category_name and category_name != "Default":
        return "{}: {}".format(category_name, plugin_name)
    return plugin_name

def __override_registerOptionFromPlugin(self, category_name, plugin_name, option_name, option_value):
    section_name = __get_section_name(category_name, plugin_name)
    if not self.config_parser.has_section(section_name):
        self.config_parser.add_section(section_name)
    self.config_parser.set(section_name,option_name,option_value)
    self.config_has_changed()

def __override_hasOptionFromPlugin(self, category_name, plugin_name, option_name):
    section_name = __get_section_name(category_name, plugin_name)
    return self.config_parser.has_section(section_name) and self.config_parser.has_option(section_name,option_name)

def __override_readOptionFromPlugin(self, category_name, plugin_name, option_name):
    section_name = __get_section_name(category_name, plugin_name)
    return self.config_parser.get(section_name,option_name)

ConfigurablePluginManager.registerOptionFromPlugin = __override_registerOptionFromPlugin
ConfigurablePluginManager.hasOptionFromPlugin = __override_hasOptionFromPlugin
ConfigurablePluginManager.readOptionFromPlugin = __override_readOptionFromPlugin

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
            plugin_object.set_name(plugin_name)
            plugin_object.set_category_name(category_name)
            return plugin_object
        
        return None
    
        
