import forecastio
from datetime import datetime
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import re


class Weather:

    def __init__(self):
        self.key = 'ed968a36266723f284f2caeace939fba'
        self.icon_dict = {'clear-day': 'clear_day.svg',
                          'clear-night': 'clear_night.svg',
                          'rain': 'rainy.svg',
                          'snow': 'snowy.svg',
                          'sleet': 'sleet.svg',
                          'wind': 'windy.svg',
                          'fog': 'fog.svg',
                          'cloudy': 'cloudy.svg',
                          'partly-cloudy-day': 'partly_cloudy_day.svg',
                          'partly-cloudy-night': 'partly_cloudy_night.svg'}
        self.day_conv = {0: 'Monday',
                         1: 'Tuesday',
                         2: 'Wednesday',
                         3: 'Thursday',
                         4: 'Friday',
                         5: 'Saturday',
                         6: 'Sunday'}
        self.last_call = {'time': datetime(1, 1, 1),
                          'location': ''}
        self.forecast = None
        self.current_weather_data = None
        self.future_weather_data = None
        self.reset_current_weather_data()
        self.reset_future_weather_data()

    def reset_current_weather_data(self):
        self.current_weather_data = {'hours': list(),
                                     'icon': list(),
                                     'temperature': list()}

    def reset_future_weather_data(self):
        self.future_weather_data = {'temps_low': list(),
                                    'temps_high': list(),
                                    'icon': list(),
                                    'summaries': list(),
                                    'day': list()}

    def geocode_me(self, location):
        try:
            geolocator = Nominatim(user_agent="weather-module")
            return geolocator.geocode(location)
        except GeocoderTimedOut:
            print "caught time out"
            return self.geocode_me(location)

    def download_forecast(self, loc):

        curr_time = datetime.now()
        time_diff = curr_time - self.last_call['time']
        # Only get new weather if 5min has passed since last call or a new location has been requested
        if self.get_forecast() is None or self.last_call['location'] != loc or time_diff.seconds > 300:
            location = self.geocode_me(loc)
            lat = location.latitude
            long = location.longitude

            forecast = forecastio.load_forecast(self.key, lat, long, units='si')
            self.last_call['time'] = datetime.now()
            self.last_call['location'] = loc
            self.forecast = forecast
        return self.forecast

    def get_forecast(self):
        return self.forecast

    def get_current_weather_data(self):
        return self.current_weather_data

    def get_future_weather_data(self):
        return self.future_weather_data

    def create_weather_pages(self, loc):
        self.create_current_weather_page(loc)
        self.create_future_weather_page(loc)

    def create_current_weather_data(self):
        self.reset_current_weather_data()
        nbr_of_icons = 8

        curr_hour = datetime.now().hour

        curr_weather = self.get_forecast().currently()
        curr_temp = curr_weather.temperature
        curr_icon = curr_weather.icon

        self.current_weather_data['temperature'].append(curr_temp)
        self.current_weather_data['icon'].append(curr_icon)
        self.current_weather_data['hours'] = [str((curr_hour + idx + 1) % 24) + ':00' for idx in range(nbr_of_icons)]
        self.current_weather_data['hours'] .insert(0, 'NOW')

        for i in range(nbr_of_icons):
            # Get future forecasts 2hr from now and every 6th hour onwards
            data_point = self.get_forecast().hourly().data[i + 1]
            self.current_weather_data['temperature'].append(data_point.temperature)
            self.current_weather_data['icon'].append(data_point.icon)

    def create_future_weather_data(self):
        nbr_of_icons = 5

        curr_day = datetime.now().weekday()

        weather = self.forecast.daily()
        for i in range(nbr_of_icons):
            day_data = weather.data[i]
            self.future_weather_data['temps_low'].append(day_data.temperatureLow)
            self.future_weather_data['temps_high'].append(day_data.temperatureHigh)
            self.future_weather_data['icon'].append(day_data.icon)
            self.future_weather_data['summaries'].append(day_data.summary)

        self.future_weather_data['day'] = [self.day_conv[(curr_day + i) % 7] for i in range(2, nbr_of_icons)]
        self.future_weather_data['day'].insert(0, 'Tomorrow')
        self.future_weather_data['day'].insert(0, 'Today')

    def create_current_weather_page(self, loc):
        # Get template file
        if self.get_forecast() is None:
            self.download_forecast(loc)
        self.create_current_weather_data()

        filehandle = open("pepper_html/weather/weather_hour_template.html")
        soup = BeautifulSoup(filehandle, 'html.parser')
        # Some ugly html coding
        images = soup.find_all('input')
        texts = soup.find_all('b')
        for idx in range(len(images) - 2):  # Dont loop through buttons
            images[idx]['src'] = 'images/' + self.icon_dict[self.current_weather_data['icon'][idx]]
            texts[2 * idx].string = self.current_weather_data['hours'][idx]
            temp_string = str(self.current_weather_data['temperature'][idx].__format__('.0f')) + ' deg'
            texts[2 * idx + 1].string = temp_string

        loc_string = loc.capitalize()
        soup.h2.string = '%s: 8-hour forecast' % loc_string
        # Save file
        with open("pepper_html/weather/weather_hour.html", "w") as file:
            file.write(str(soup.prettify()))

    def create_future_weather_page(self, loc):
        if self.get_forecast() is None:
            self.download_forecast(loc)
        self.create_future_weather_data()
        # Get template file
        filehandle = open("pepper_html/weather/weather_day_template.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        text_days = soup.find_all(id=re.compile('day'))
        text_summary = soup.find_all(id=re.compile('summ'))
        text_temp_low = soup.find_all(id=re.compile('templow'))
        text_temp_high = soup.find_all(id=re.compile('temphigh'))

        for idx in range(len(images) - 2):  # Dont loop through buttons
            images[idx]['src'] = 'images/' + self.icon_dict[ self.future_weather_data['icon'][idx]]
            text_days[idx].string =  self.future_weather_data['day'][idx]
            text_summary[idx].string = self.future_weather_data['summaries'][idx]
            temp_low_string = str( self.future_weather_data['temps_low'][idx].__format__('.0f')) + ' deg'
            text_temp_low[idx].string = 'Low: ' + temp_low_string

            temp_high_string = str( self.future_weather_data['temps_high'][idx].__format__('.0f')) + ' deg'
            text_temp_high[idx].string = 'High: ' + temp_high_string

        loc_string = loc[0].upper() + loc[1:]
        soup.h2.string = '%s: 5-day forecast' % loc_string
        # Save file
        with open("pepper_html/weather/weather_day.html", "w") as file:
            file.write(str(soup.prettify()))
