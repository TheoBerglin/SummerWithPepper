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

        self.wt.get_current_weather(self.loc)
        hour_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/weather/weather_hour.html'
        self.transfer_to_pepper(hour_path)
        weather_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/weather/weather_day.html'
        self.transfer_to_pepper(weather_path)
        self.display_on_tablet('weather_hour.html')
