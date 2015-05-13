from yapsy.IPlugin import IPlugin


class TelegramPlugin(IPlugin):
    def __init__(self, bot):
        self.bot = bot

    def run(self, msg, matches):
        raise NotImplementedError

    def pre_process(self, msg):
        return msg