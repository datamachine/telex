from telex import plugin
from plugins.weather_util.py3owm import OpenWeatherMap
from plugins.weather_util.py3wu import WeatherUnderground

class WeatherPlugin(plugin.TelexPlugin):
    """
    Weather
    """

    patterns = [
        "^{prefix}weather? ([0-9]{5}|.*)",
    ]

    usage = [
        "{prefix}weather location"
    ]

    config_options = {
        "api_key": "API key for applicable backends",
        "units": "Units to return (F/C) as imperial/metric",
        "backend": "Data source, currently supporting openweathermap and weatherunderground (api_key required)",
    }

    def activate_plugin(self):
        if not self.has_option("api_key"):
            self.write_option("api_key", "")
        if not self.has_option("units"):
            self.write_option("units", "imperial")
        if not self.has_option("backend"):
            self.write_option("backend", "openweathermap")

        api_key = self.read_option("api_key")
        units = self.read_option("units")

        if self.read_option("backend") == "openweathermap":
            self.backend = OpenWeatherMap(api_key, units)
        elif self.read_option("backend") == "weatherunderground":
            if api_key == "":
                raise Exception("Weather Underground requires an API Key")
            self.backend = WeatherUnderground(api_key, units)
        else:
            raise Exception("Invalid backend selected")

    def run(self, msg, matches):
        try:
            if self.read_option("backend") == "wunderground":
                w = self.backend.weather_data(search=matches.group(1))
            else:
                w = self.backend.weather_data(zipcode=matches.group(1))
            if w:
                report = u"{} ({}) {}{}\n{} {} ({} Relative Humidity, {}{} Heat Index)".format(w.name, w.country, w.temp,
                                                                              w.unit_symbol, w.description, w.icon, w.humidity, w.heat_index, w.unit_symbol)

                return report
        except Exception as e:
            print("Exception {}".format(e))

        return "Error getting weather data"


