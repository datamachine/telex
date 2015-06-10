from yapsy.IPlugin import IPlugin

class TelexPlugin(IPlugin):
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

    def all_options(self):
        from configparser import ConfigParser
        from pathlib import Path
        cp = ConfigParser()
        p = Path("plugins.conf")
        if p.exists():
            cp.read_file(p.open("r"))
        if not cp.has_section(self.name):
            return []
        return cp.options(self.name)

    def has_option(self, option):
        return self.plugin_manager.hasOptionFromPlugin(self.category_name, self.name, option)

    def activate_plugin(self):
        pass

    def run(self, msg, matches):
        raise NotImplementedError

    def pre_process(self, msg):
        pass

    def respond_to_msg(self, src_msg, msg_text, **kwargs):
        msg_text = msg_text.replace('{prefix}', self.bot.pfx)
        self.bot.get_peer_to_send(src_msg).send_msg(msg_text, **kwargs)

