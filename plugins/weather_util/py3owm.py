import urllib.parse
import urllib.request
import json
from math import sqrt

class Weather:
    def __init__(self, data, units):
        self.data = data
        self.units = units

    @property
    def unit_symbol(self):
        if self.units == "imperial":
            return "F°"
        elif self.units == "metric":
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
    def humidity(self):
        return self.data['main']['humidity']

    @property
    def temp(self):
        return self.data["main"]["temp"]

    @property
    def heat_index(self):
        T = self.temp
        RH = self.humidity
        # Implementation of https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        if T < 80:
            return 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
        else:
            HI = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
            if RH < .13 and T < 112:
                HI -= ((13-RH)/4)*sqrt((17-abs(T-95.))/17)
            elif RH > .85 and T < 87:
                HI +=  ((RH-85)/10) * ((87-T)/5)
            return HI


    @property
    def description(self):
        return self.data["weather"][0]["description"]

    @property
    def icon(self):
        try:
            return {
                "01d": u'\U0001F31E',
                "02d": u'\U000026C5',
                "03d": u'\U00002601',
                "03d": u'\U00002601',
                "09d": u'\U0001F302',
                "10d": u'\U00002614',
                "11d": u'\U000026A1',
                "13d": u'\U00002744',
                "50d": u'\U0001F301'
            }[self.data["weather"][0]["icon"]]
        except:
            return ""

class OpenWeatherMap:
    def __init__(self, api_key, units="metric"):
        self.api_key = api_key
        self.api_key = "https://api.openweathermap.org/data/2.5"

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

    def _call_weather(self, params):
        return self._call_api_function("weather", params)

    def weather_data_by_city(self, city):
        return self._call_weather({"q":city})

    def weather_data_by_id(self, city_id):
        return self._call_weather({"id":city_id})

    def weather_data_by_coords(self, coords):
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

