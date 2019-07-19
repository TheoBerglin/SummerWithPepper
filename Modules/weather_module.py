#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
import os
from Modules.module import ModuleBaseClass
from Applications.weather import Weather


class WeatherModule(ModuleBaseClass):
    """
    A module to handle interaction between the robot and the weather API.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "weather"
        # Superclass init call
        super(WeatherModule, self).__init__(app, name, pepper_ip, folder_name)
        # Create Weather object
        self.wt = Weather()

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(WeatherModule, self).display_on_tablet(full_file_name)
        self.introduce_view(full_file_name)

    def introduce_view(self, file_name):
        if file_name == 'weather_hour.html':
            if self.wt.get_forecast() is None:
                return
            current_weather = self.wt.get_current_weather_data()
            weather1 = current_weather['icon'][0].split('.svg')[0].replace('_', ' ')
            weather2 = current_weather['icon'][2].split('.svg')[0].replace('_', ' ')
            temperature1 = current_weather['temperature'][0].__format__('.0f')
            temperature2 = current_weather['temperature'][2].__format__('.0f')
            string1 = 'Right now it is %s with a temperature of %s degrees' % (weather1, temperature1)
            string2 = 'In two hours it will be %s with a temperature of %s degrees' % (weather2, temperature2)
            self.tts.say(string1)
            self.tts.say(string2)
        elif file_name == 'weather_day.html':
            if self.wt.get_forecast() is None:
                return
            future_weather = self.wt.get_future_weather_data()
            weather1 = future_weather['summaries'][1]
            temperatureLow1 = future_weather['temps_low'][1].__format__('.0f')
            temperatureHigh1 = future_weather['temps_high'][1].__format__('.0f')
            string1 = 'It will be %s tomorrow with lowest temperature %s degrees and highest temperature %s degrees.' % (weather1, temperatureLow1, temperatureHigh1)
            self.tts.say(string1)
        else:
            self.tts.say('Where do you want to know the weather?')

    def run(self):
        self.initiate_dialog()
        while not self.module_finished:
            time.sleep(1)
        self.shutoff()

    def shutoff(self, *_args):
        """
        Shutoff and unsubscribe to events. Trigger ModuleFinished event.
        """
        try:
            self.dialog.deactivateTopic(self.topic)
            self.dialog.unloadTopic(self.topic)
            self.dialog.unsubscribe(self.name)
            print "Stopped dialog"
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.hide_tablet = True
            if self.t is not None:
                print "Main waiting for thread to die"
                self.t.join()
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass
        self.module_finished = False

    def initiate_dialog(self):
        self.tablet.hideWebview()

        # Load dialog and display intro screen
        self.topic = self.dialog.loadTopic("/home/nao/Weather_enu.top")
        self.dialog.activateTopic(self.topic)
        self.dialog.subscribe(self.name)

        # Subscribe to events raised on button click
        self.location_subscriber = self.memory.subscriber("location")
        self.location_id = self.location_subscriber.signal.connect(self.forecast)
        self.hour_subscriber = self.memory.subscriber("new_view")
        self.hour_id = self.hour_subscriber.signal.connect(self.display_on_tablet)

        self.display_on_tablet('weather_intro.html')

    def forecast(self, *_args):
        self.tablet.hideWebview()

        self.loc = self.memory.getData("location")
        self.wt.download_forecast(self.loc)
        self.wt.create_weather_pages(self.loc)
        hour_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/weather/weather_hour.html'
        self.transfer_to_pepper(hour_path)
        weather_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/weather/weather_day.html'
        self.transfer_to_pepper(weather_path)
        self.display_on_tablet('weather_hour.html')
