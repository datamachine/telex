from telex import plugin

class TelegramInfoPlugin(plugin.TelexPlugin):
    patterns = [
        "^!tginfo (id)",
        "^!tginfo (repr) (.+)"
    ]

    usage = [
        "!tginfo id: echo's the requester's telegram id",
    ]

    def run(self, msg, matches):
        cmd = matches.group(1)
        if cmd == "id":
           return "{} {}: {}".format(msg.src.first_name, msg.src.last_name, msg.src.id)

        if cmd == "repr":
            return repr(matches.group(2).encode())
