from telegrambot import plugin

class SupportPlugin(plugin.TelegramPlugin):
    patterns = {
        "^!support": "list_support_contact_info"
    }

    usage = [
        "!support: lists support contact info",
    ]

    def list_support_contact_info(self, msg, matches):
        contact_info = [
        "Bugs and issues can be reported at: https://github.com/datamachine/telegram-pybot/issues",
        "Or you can contact the devs directly at:",
        "https://telegram.me/Surye",
        "https://telegram.me/Tyrannosaurus"
        ]
        return "\n".join(contact_info)
