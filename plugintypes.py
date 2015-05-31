from telegrambot import plugin

class TelegramPlugin(plugin.TelegramPlugin):
    def __init__(self):
        print("DEPRECATED!!! Use module telegrambot.plugin instead of plugintypes")
        super().__init__()

    def set_name(self, name):
        print("DEPRECATED!!! {}: Use module telegrambot.plugin instead of plugintypes".format(name))
        super().set_name(name)
        

