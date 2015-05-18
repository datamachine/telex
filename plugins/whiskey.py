import plugintypes

class WhiskeyPlugin(plugintypes.TelegramPlugin):
    """
    Pass the whiskey.
    """

    patterns = [
        "^!whiskey(.*)"
    ]

    usage = [
        "!whiskey"
    ]

    def run(self, msg, matches):
        return "Pass the whiskey."

