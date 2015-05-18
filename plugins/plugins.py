import plugintypes


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

        if matches.group(1) == "enable":
            if self.plugin_manager.activatePluginByName(matches.group(2)):
                return "Plugin {} enabled".format(matches.group(2))
            else:
                return "Error loading plugin {}".format(matches.group(2))

        if matches.group(1) == "disable":
            return self.bot.disable_plugin(matches.group(2))

        if matches.group(1) == "reload":
            self.bot.load_plugins()

    def list_plugins(self):
        text = ""
        for plugin in self.bot.get_plugins():
            text += "{0}: ({1})\n".format(plugin.name,
                                          "(Enabled)" if plugin.plugin_object.is_activated else "(Disabled)")

        return text
