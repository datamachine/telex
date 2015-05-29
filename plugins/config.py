import plugintypes
from telegrambot import auth
from telegrambot.utils.decorators import pm_only

class ConfigPlugin(plugintypes.TelegramPlugin):
    """
    Plugin to manage other plugin configuration.
    """
    patterns = {
        "^!config ([\w-]+) show$": "show_options",
        "^!config ([\w-]+) set ([\w-]+) \"(.+)\"": "set_option",
        "^!config ([\w-]+) get ([\w-]+)": "get_option",
    }

    usage = [
        "!config <plugin_name> show: List all plugin options",
        "!config <plugin_name> set <configname> \"<value>\": Get plugin value.",
        "!config <plugin_name> get <configname>: Get config value.",
    ]

    @auth.authorize(groups=["admins"])
    @pm_only
    def show_options(self, msg, matches):
        try:
            plugin = self.plugin_manager.getPluginByName(matches.group(1)).plugin_object
        except AttributeError:
            return "No plugin found for {}".format(matches.group(1))

        if not hasattr(plugin, "config_options"):
            return "Plugin {} has no config_options defined, cannot list options".format(matches.group(1))
        text = "Configuration options for {}:\n{}".format(matches.group(1),
                "\n".join(["{}: {}".format(k, v) for k, v in plugin.config_options.items()]))

        return text


    @auth.authorize(groups=["admins"])
    @pm_only
    def set_option(self, msg, matches):
        try:
            plugin = self.plugin_manager.getPluginByName(matches.group(1)).plugin_object
        except AttributeError:
            return "No plugin found for {}".format(matches.group(1))
        plugin.write_option(matches.group(2), matches.group(3))
        return "Set {}.{} to {}".format(matches.group(1), matches.group(2), matches.group(3))


    @auth.authorize(groups=["admins"])
    @pm_only
    def get_option(self, msg, matches):
        try:
            plugin = self.plugin_manager.getPluginByName(matches.group(1)).plugin_object
        except AttributeError:
            return "No plugin found for {}".format(matches.group(1))
        return "{}.{} = {}".format(matches.group(1), matches.group(2), plugin.read_option(matches.group(2)))
