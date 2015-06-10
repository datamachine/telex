from telex import plugin

class SupportPlugin(plugin.TelexPlugin):
    patterns = {
        "^{prefix}support": "list_support_contact_info"
    }

    usage = [
        "{prefix}support: lists support contact info",
    ]

    def list_support_contact_info(self, msg, matches):
        contact_info = [
        "Bugs and issues can be reported at: https://github.com/datamachine/telegram-pybot/issues",
        "Or you can contact the devs directly at:",
        "https://telegram.me/joinchat/05c5c2f60112fa104d1c0c563b2fd34a",
        ]
        return "\n".join(contact_info)
