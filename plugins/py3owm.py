import urllib.parse
import urllib.request
import json


class Weather:
    def __init__(self, data, units):
        self.data = data
        self.units = units

    @property
    def unit_symbol(self):
        if self.units is "imperial":
            return "F°"
        elif self.units is "metric":
            return "C°"
        else:
            return "K"

    @property
    def id(self):
        return self.data["id"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def country(self):
        return self.data["sys"]["country"]

    @property
    def temp(self):
        return self.data["main"]["temp"]

    @property
    def description(self):
        return self.data["weather"][0]["description"]
        
        
class OpenWeatherMap:
    def __init__(self, api_key, units="metric"):
        self.api_key = api_key
        self.api_key = "http://api.openweathermap.org/data/2.5"

        self.set_units(units)

    def set_units(self, units):
        self.units = units
    
    def _build_url(self, api_function, params):
        params["APPID"] = self.api_key
        params["units"] = self.units

        encoded_params = urllib.parse.urlencode(params)

        url = "{0}/{1}?{2}".format(self.api_key, api_function, encoded_params)
    
        return url

    def _call_api_function(self, api_function, params):
        url = self._build_url(api_function, params)
        with urllib.request.urlopen(url) as f:
            data = f.read().decode('utf-8')
            return json.loads(data)

        return None

    def _call_weather(self, params):
        return self._call_api_function("weather", params)

    def weather_data_by_city(self, city):
        return self._call_weather({"q":city})

    def weather_data_by_id(self, city_id):
        return self._call_weather({"id":city_id})

    def weather_data_by_coords(coords):
        return self._call_weather({"lat":coords[0], "lon":coords[1]})

    def weather_data_by_zip(self, zipcode):
        return Weather(self._call_weather({"zip":zipcode}), self.units)

    def weather_data(self, city=None, city_id=None, coords=None, zipcode=None):
        if city:
            return self.weather_data_by_city(city)
        elif city_id:
            return self.weather_data_by_id(city_id)
        elif coords:
            return self.weather_data_by_coords(coords)
        elif zipcode:
            return self.weather_data_by_zip(zipcode)

        return None

