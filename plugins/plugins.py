import plugintypes

NO_ENTRY = b'\xf0\x9f\x9a\xab'.decode("utf-8")
CHECK_BOX = b'\xe2\x9c\x85'.decode("utf-8")

class PluginsPlugin(plugintypes.TelegramPlugin):
    """
    Plugin to manage other plugins. Enable, disable or reload.
    """
    patterns = [
        "^!plugins$",
        "^!plugins? (enable) ([\w_.-]+)$",
        "^!plugins? (disable) ([\w_.-]+)$",
        # "^!plugins? (enable) ([\w_.-]+) (chat)",
        # "^!plugins? (disable) ([\w_.-]+) (chat)",
        "^!plugins? (reload)$"
    ]

    usage = [
        "!plugins: list all plugins.",
        "!plugins enable [plugin]: enable plugin.",
        "!plugins disable [plugin]: disable plugin.",
        # "!plugins disable [plugin] chat: disable plugin only this chat.",
        "!plugins reload: reloads all plugins."
    ]

    def run(self, msg, matches):
        if matches.group(0) == "!plugins":
            return self.list_plugins()

        command = matches.group(1)

        if command == "enable":
            return self.enable_plugin(matches)

        if command == "disable":
            return self.disable_plugin(matches)

        if command == "reload":
            return self.reload_plugins()

    def enable_plugin(self, matches):
        if self.plugin_manager.activatePluginByName(matches.group(2)):
            return "Enabled plugin: {}".format(matches.group(2))
        else:
            return "Error loading plugin: {}".format(matches.group(2))

    def disable_plugin(self, matches):
        if self.plugin_manager.deactivatePluginByName(matches.group(2)):
            return "Disabled plugin: {}".format(matches.group(2))
        else:
            return "Error disabling plugin: {}".format(matches.group(2))
 
    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"

    def list_plugins(self):
        text = ""
        for plugin in self.plugin_manager.getAllPlugins():
            text += "{0}: {1}\n".format(
                CHECK_BOX if plugin.plugin_object.is_activated else NO_ENTRY, plugin.name)

        return text
