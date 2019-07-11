import forecastio
from datetime import date, timedelta
from bs4 import BeautifulSoup


class Weather:

    def __init__(self, lat=57.705824, long=11.940407):
        self.key = 'ed968a36266723f284f2caeace939fba'
        self.lat = lat
        self.long = long

    def get_current_weather(self):
        forecast = forecastio.load_forecast(self.key, self.lat, self.long, units='si')
        curr_weather = forecast.currently()
        curr_temp = curr_weather.temperature
        curr_summ = curr_weather.summary
        curr_icon = curr_weather.icon
        print curr_summ
        print 'Temperature: %.2f C' % curr_temp
        filehandle = open("pepper_html/weather/weather.html")
        soup = BeautifulSoup(filehandle, 'html.parser')
        soup.input.attrs['src'] = 'images/cloudy.png'
        print soup.prettify()
        with open("pepper_html/weather/output1.html", "w") as file:
            file.write(str(soup))
