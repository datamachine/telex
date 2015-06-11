from telex.plugin import TelexPlugin

class HelpPlugin(TelexPlugin):
    """
    Print help for telegram-bot and plugins
    """
    patterns = [
        "^{prefix}help$",
        "^{prefix}help (.+)",
    ]

    usage = [
        "{prefix}help: Show list of plugins.",
        "{prefix}help [plugin name]: Commands for that plugin."
    ]

    def run(self, msg, matches):
        if matches.group(0)[1:] == "help":
            return self.telegram_help()

        text = self.plugin_help(matches.group(1))
        if text is None:
            return self.telegram_help()
        else:
            return text

    def plugin_help(self, name):
        text = None
        plugin = self.plugin_manager.getPluginByName(name)

        if plugin is not None:
            if plugin.plugin_object.is_activated:
                text = "{0}: {1}\n".format(plugin.name, plugin.description)
                if hasattr(plugin.plugin_object, 'usage'):
                    text += "\n".join(plugin.plugin_object.usage)
                    text = text.replace('{prefix}', self.bot.pfx)
                else:
                    text += "No Usage Help"
            else:
                text = "Plugin {0} is disabled\n".format(plugin.name)

        return text

    def telegram_help(self):
        text = "Plugin list: \n\n"

        for plugin in self.plugin_manager.getAllPlugins():
            if plugin.plugin_object.is_activated:
                text += "{0}: {1}\n".format(plugin.name, plugin.description)

        text += "\n Write \"{prefix}help [plugin name]\" for more info"
        text = text.replace('{prefix}', self.bot.pfx)

        return text
