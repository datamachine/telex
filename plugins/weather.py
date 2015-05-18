import plugintypes
import sys

sys.path.append('./plugins')

from py3owm import OpenWeatherMap

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

    def activate_plugin(self):
        if not self.has_option("api key"):
            self.write_option("api key", "")
        
        api_key = self.read_option("api key")
        self.owm = OpenWeatherMap(api_key, "imperial")


    def run(self, msg, matches):
        w = self.owm.weather_data(zipcode=91941)
        report = "{} ({}) {}{}\n{}".format(w.name, w.country, w.temp, w.unit_symbol, w.description)
        print(report)
        return "Nothing to report"

