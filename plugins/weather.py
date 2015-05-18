import plugintypes

class WeatherPlugin(plugintypes.TelegramPlugin):
    """
    Weather
    """

    patterns = [
        "^!weather (.*)"
    ]

    usage = [
        "!weather <zip code>|<city>"
    ]

    def run(self, msg, matches):
        return "It's so cold in here"

