import plugintypes

class EchoPlugin(plugintypes.TelegramPlugin):
    """
    Just print the contents of the command
    """
    patterns = [
        "^!echo (.*)"
    ]

    usage = [
        "!echo msg: echoes the msg",
    ]

    def run(self, msg, matches):
        return matches.group(1)