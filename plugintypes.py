from yapsy.IPlugin import IPlugin

class TelegramPlugin(IPlugin):
    def __init__(self):
        super().__init__()
        self.bot = None
        self.plugin_manager = None
        self.name = None
        self.category_name = None

    def set_bot(self, bot):
        self.bot = bot

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def set_name(self, name):
        self.name = name

    def set_category_name(self, category_name):
        self.category_name = category_name

    def write_option(self, option, value):
        self.plugin_manager.registerOptionFromPlugin(self.category_name, self.name, option, value)

    def read_option(self, option):
        return self.plugin_manager.readOptionFromPlugin(self.category_name, self.name, option)

    def has_option(self, option):
        return self.plugin_manager.hasOptionFromPlugin(self.category_name, self.name, option)

    def activate_plugin(self):
        pass

    def run(self, msg, matches):
        raise NotImplementedError

    def pre_process(self, msg):
        return msg
