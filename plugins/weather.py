import plugintypes
import sys

sys.path.append('./plugins')

from py3owm import OpenWeatherMap

class WeatherPlugin(plugintypes.TelegramPlugin):
    """
    Weather
    """

    patterns = [
        "^!weather? ([0-9]{5})"
    ]

    usage = [
        "!weather <zip code>|<city>"
    ]

    def activate_plugin(self):
        if not self.has_option("api key"):
            self.write_option("api key", "")
        if not self.has_option("units"):
            self.write_option("units", "metric")
        
        api_key = self.read_option("api key")
        units = self.read_option("units")

        self.owm = OpenWeatherMap(api_key, units)


    def run(self, msg, matches):
        w = self.owm.weather_data(zipcode=matches.group(1))
        if w:
            report = "{} ({}) {}{}\n{}".format(w.name, w.country, w.temp, w.unit_symbol, w.description)
            return report
        return "Error getting weather data"


