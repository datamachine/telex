import plugintypes

class PingPlugin(plugintypes.TelegramPlugin):
    """
    Return PONG in response to !ping
    """
    patterns = ["^!ping.*"]

    def run(self, msg, matches):
        return "PONG"