import plugintypes

class TelegramInfoPlugin(plugintypes.TelegramPlugin):
    patterns = [
        "^!tginfo (id)"
    ]

    usage = [
        "!tginfo id: echo's the requester's telegram id",
    ]

    def run(self, msg, matches):
        try:
            first, last, id = msg.src.first_name, msg.src.last_name, msg.src.id
            return u"{} {}: {}".format(first, last, id)
        except:
            return None
