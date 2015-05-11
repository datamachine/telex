from yapsy.PluginManager import PluginManager


class TelegramPluginManager(PluginManager):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def instanciateElement(self, element):
        """
        Override this method to customize how plugins are instanciated
        """
        return element(self.bot)