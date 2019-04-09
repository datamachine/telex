import urllib.parse
import urllib.request
import json


class Weather:
    def __init__(self, data, units):
        self.data = data
        self.units = units

    @property
    def unit_symbol(self):
        if self.units == 'imperial':
            return 'F°'
        elif self.units == 'metric':
            return 'C°'
        else:
            return 'K'

    @property
    def id(self):
        return self.data['id']

    @property
    def name(self):
        return '{}, {}'.format(self.data['location']['city'], self.data['location']['state'])

    @property
    def country(self):
        return self.data['location']['country']

    @property
    def humidity(self):
        return self.data['current_observation']['relative_humidity']

    @property
    def heat_index(self):
        return self.data['current_observation']['heat_index_f']

    @property
    def temp(self):
        if self.units == 'imperial':
            return self.data['current_observation']['temp_f']
        else:
            return self.data['current_observation']['temp_c']

    @property
    def description(self):
        return self.data['current_observation']['weather']

    @property
    def icon(self):
        try:
            return {
                'clear': '\U0001F31E',
                'snow': '\U00002744',
                'chancesnow': '\U00002744',
                'cloudy': '\U00002601',
                'flurries': '\U00002744',
                'chanceflurries': '\U00002744',
                'fog': '\U000026C5',
                'hazy': '\U000026C5',
                'mostlycloudy': '\U000026C5',
                'mostlysunny': '\U000026C5',
                'partlycloudy': '\U000026C5',
                'rain': '\U00002614',
                'chancerain': '\U00002614',
                'sleet': '\U00002614',
                'chancesleet': '\U00002614',
                'sunny': '\U0001F31E',
                'tstorms': '\U000026A1',
                'chancetstorms': '\U000026A1',
            }[self.data['current_observation']['icon']]
        except:
            return ''


class WeatherUnderground:
    def __init__(self, api_key, units='metric'):
        self.api_key = api_key
        self.base_url = 'http://api.wunderground.com/api/{}/geolookup/conditions/q'.format(self.api_key)
        self.set_units(units)

    def set_units(self, units):
        self.units = units

    def _build_url(self, param):
        param = urllib.parse.quote(param)
        url = '{0}/{1}.json'.format(self.base_url, param)

        return url

    def _call_api(self, param):
        url = self._build_url(param)
        with urllib.request.urlopen(url) as f:
            data = f.read().decode('utf-8')
            result = json.loads(data)
            if 'results' in result['response']: # We found more than one result, returning the first.
                return self._call_api(result['response']['results'][0]['zmw'])
            else:
                return result

    def _call_weather(self, param):
        return self._call_api(param)

    def weather_data_by_city(self, city):
        return self._call_weather(city)

    def weather_data_by_coords(coords):
        return Weather(self._call_weather('{0},{1}'.format(coords[0], coords[1])))

    def weather_data_by_zip(self, zipcode):
        return Weather(self._call_weather(zipcode), self.units)

    def weather_data(self, search=None, city=None, city_id=None, coords=None, zipcode=None):
        if city:
            return self.weather_data_by_city(city)
        elif city_id:
            raise NotImplementedError('Weather Underground does not support city_id')
        elif coords:
            return self.weather_data_by_coords(coords)
        elif zipcode:
            return self.weather_data_by_zip(zipcode)
        elif search:
            return self._call_weather(search)

        return None

