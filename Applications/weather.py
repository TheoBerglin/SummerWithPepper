import forecastio
from datetime import datetime
from bs4 import BeautifulSoup


class Weather:

    def __init__(self, lat=57.705824, long=11.940407):
        self.key = 'ed968a36266723f284f2caeace939fba'
        self.lat = lat
        self.long = long
        self.icon_dict = {'clear-day': 'clear.png',
                          'clear-night': 'clear.png',
                          'rain': 'rain.png',
                          'snow': 'snow.png',
                          'sleet': 'snow.png',
                          'wind': 'cloudy.png',  # Change icon
                          'fog': 'cloudy.png',  # Change icon
                          'cloudy': 'cloudy.png',
                          'partly-cloudy-day': 'partly_cloudy.png',
                          'partly-cloudy-night': 'partly_cloudy.png'}  # Add night

    def get_current_weather(self):
        curr_hour = datetime.now().hour
        forecast = forecastio.load_forecast(self.key, self.lat, self.long, units='si')

        curr_weather = forecast.currently()
        curr_temp = curr_weather.temperature
        curr_summ = curr_weather.summary
        curr_icon = curr_weather.icon

        temps = [curr_temp]
        icons = [curr_icon]
        summ = [curr_summ]
        hours = [curr_hour+2, curr_hour+8, curr_hour+14, curr_hour+20]
        hours = [str(i % 24) + ':00' for i in hours]
        hours.insert(0, 'NOW')

        for i in range(4):
            # Get future forecasts 2hr from now and every 6th hour onwards
            data_point = forecast.hourly().data[6*i+2]
            temps.append(data_point.temperature)
            icons.append(data_point.icon)
            summ.append(data_point.summary)

        # Get template file
        filehandle = open("pepper_html/weather/weather.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        texts = soup.find_all('b')
        for idx in range(len(images)):
            images[idx]['src'] = 'images/' + self.icon_dict[icons[idx]]
            texts[3*idx].string = hours[idx]
            texts[3*idx+1].string = summ[idx]
            temp_string = str(temps[idx].__format__('.1f')) + ' deg'
            texts[3*idx+2].string = temp_string

        # Save file
        with open("pepper_html/weather/weather_test.html", "w") as file:
            file.write(str(soup.prettify()))
