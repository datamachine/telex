from yapsy.IPlugin import IPlugin

class TelegramPlugin(IPlugin):
    def __init__(self):
        super().__init__()
        self.bot = None
        self.plugin_manager = None

    def set_bot(self, bot):
        self.bot = bot

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def run(self, msg, matches):
        raise NotImplementedError

    def pre_process(self, msg):
        return msg

