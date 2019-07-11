import forecastio
from datetime import date, timedelta, datetime
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
        print curr_summ
        print 'Temperature: %.2f C' % curr_temp
        temps = [curr_temp]
        icons = [curr_icon]
        for i in range(4):
            data_point = forecast.hourly().data[6*i+2]
            temps.append(data_point.temperature)
            icons.append(data_point.icon)
        filehandle = open("pepper_html/weather/weather.html")
        soup = BeautifulSoup(filehandle, 'html.parser')
        images = soup.find_all('input')
        for idx, img in enumerate(images):
            img['src'] = 'images/' + self.icon_dict[icons[idx]]
        print soup.prettify()
        with open("pepper_html/weather/output1.html", "w") as file:
            file.write(str(soup))
