import plugintypes

class PluginsPlugin(plugintypes.TelegramPlugin):
    """
    Plugin to manage other plugins. Enable, disable or reload.
    """
    patterns = ["^!plugins$"]

    def run(self, msg, matches):
        self.bot.load_plugins()
        return "Reloaded"

