from telex.plugin import TelexPlugin
from telex import auth

NO_ENTRY = b'\xf0\x9f\x9a\xab'.decode("utf-8")
CHECK_BOX = b'\xe2\x9c\x85'.decode("utf-8")

class PluginsPlugin(TelexPlugin):
    """
    Plugin to manage other plugins. Enable, disable or reload.
    """
    patterns = {
        "^{prefix}plugins$": "list_plugins",
        "^{prefix}plugins? (enable) ([\w_.-]+)$": "enable_plugin",
        "^{prefix}plugins? (disable) ([\w_.-]+)$": "disable_plugin",
        "^{prefix}plugins? (reload)$": "reload_plugins"
    }

    usage = [
        "{prefix}plugins: list all plugins.",
        "{prefix}plugins enable [plugin]: enable plugin.",
        "{prefix}plugins disable [plugin]: disable plugin.",
        # "{prefix}plugins disable [plugin] chat: disable plugin only this chat.",
        "{prefix}plugins reload: reloads all plugins."
    ]

    @auth.authorize(groups=["admins"])
    def enable_plugin(self, msg, matches):
        if self.plugin_manager.activatePluginByName(matches.group(2)):
            return "Enabled plugin: {}".format(matches.group(2))
        else:
            return "Error loading plugin: {}".format(matches.group(2))

    @auth.authorize(groups=["admins"])
    def disable_plugin(self, msg, matches):
        if self.plugin_manager.deactivatePluginByName(matches.group(2)):
            return "Disabled plugin: {}".format(matches.group(2))
        else:
            return "Error disabling plugin: {}".format(matches.group(2))

    @auth.authorize(groups=["admins"])
    def reload_plugins(self, msg, matches):
        self.plugin_manager.reloadPlugins()
        return "Plugins reloaded"

    def __plugin_sort_key(self, plugin):
        if plugin.plugin_object.is_activated:
            return "0{}".format(plugin.name)
        else:
            return "1{}".format(plugin.name)


    def list_plugins(self, msg, matches):
        text = ""
        plugins = sorted(self.plugin_manager.getAllPlugins(), key=self.__plugin_sort_key)
        for plugin in plugins:
            text += "{0}: {1}\n".format(
                CHECK_BOX if plugin.plugin_object.is_activated else NO_ENTRY, plugin.name)

        return text
