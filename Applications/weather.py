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

    def geocode_me(self, location):
        try:
            geolocator = Nominatim(user_agent="weather-module")
            return geolocator.geocode(location)
        except GeocoderTimedOut:
            print "caught time out"
            return self.geocode_me(location)

    def get_forecast(self, loc):
        location = self.geocode_me(loc)
        lat = location.latitude
        long = location.longitude

        forecast = forecastio.load_forecast(self.key, lat, long, units='si')
        return forecast

    def get_current_weather(self, loc):
        forecast = self.get_forecast(loc)
        self.create_current_weather_page(forecast, loc)

    def get_future_weather(self, loc):
        forecast = self.get_forecast(loc)
        self.create_future_weather_page(forecast, loc)

    def create_current_weather_page(self, forecast, loc):
        nbr_of_icons = 8

        curr_hour = datetime.now().hour

        curr_weather = forecast.currently()
        curr_temp = curr_weather.temperature
        curr_icon = curr_weather.icon

        temps = [curr_temp]
        icons = [curr_icon]
        hours = [str((curr_hour + idx + 1) % 24) + ':00' for idx in range(nbr_of_icons)]
        hours.insert(0, 'NOW')

        for i in range(nbr_of_icons):
            # Get future forecasts 2hr from now and every 6th hour onwards
            data_point = forecast.hourly().data[i + 1]
            temps.append(data_point.temperature)
            icons.append(data_point.icon)

        # Get template file
        filehandle = open("pepper_html/weather/weather_short.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        texts = soup.find_all('b')
        for idx in range(len(images)-1):
            images[idx]['src'] = 'images/' + self.icon_dict[icons[idx]]
            texts[2 * idx].string = hours[idx]
            temp_string = str(temps[idx].__format__('.0f')) + ' deg'
            texts[2 * idx + 1].string = temp_string

        soup.h2.string = 'Here is the weather in %s for the next 8h' % loc
        # Save file
        with open("pepper_html/weather/weather_current.html", "w") as file:
            file.write(str(soup.prettify()))

    def create_future_weather_page(self, forecast, loc):
        nbr_of_icons = 5

        curr_day = datetime.now().weekday()

        weather = forecast.daily()
        temps_low = []
        temps_high = []
        icons = []
        summaries = []

        for i in range(nbr_of_icons):
            day_data = weather.data[i]
            temps_low.append(day_data.temperatureLow)
            temps_high.append(day_data.temperatureHigh)
            icons.append(day_data.icon)
            summaries.append(day_data.summary)

        day = [self.day_conv[curr_day + i] for i in range(2, nbr_of_icons)]
        day.insert(0, 'Tomorrow')
        day.insert(0, 'Today')

        # Get template file
        filehandle = open("pepper_html/weather/weather_long.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        text_days = soup.find_all(id=re.compile('day'))
        text_summary = soup.find_all(id=re.compile('summ'))
        text_temp_low = soup.find_all(id=re.compile('templow'))
        text_temp_high = soup.find_all(id=re.compile('temphigh'))

        for idx in range(len(images)-1  ):
            images[idx]['src'] = 'images/' + self.icon_dict[icons[idx]]
            text_days[idx].string = day[idx]
            text_summary[idx].string = summaries[idx]
            temp_low_string = str(temps_low[idx].__format__('.0f')) + ' deg'
            text_temp_low[idx].string = 'Low: ' + temp_low_string

            temp_high_string = str(temps_high[idx].__format__('.0f')) + ' deg'
            text_temp_high[idx].string = 'High: ' + temp_high_string

        soup.h2.string = 'Here is the weather in %s for the next 5 days' % loc
        # Save file
        with open("pepper_html/weather/weather_day.html", "w") as file:
            file.write(str(soup.prettify()))
