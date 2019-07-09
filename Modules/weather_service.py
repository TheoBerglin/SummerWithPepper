#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.service import ServiceBaseClass


class WeatherService(ServiceBaseClass):
    """
    A module to handle interaction between the robot and the vasttrafik API.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "weather"
        # Superclass init call
        super(WeatherService, self).__init__(app, name, pepper_ip, folder_name)

    def initiate_dialog(self):
        self.tablet.hideWebview()

        self.tts.say("It's sunny")

        self.exit_subscriber = self.memory.subscriber("exit")
        self.exit_id = self.exit_subscriber.signal.connect(self.shutoff)

        self.module_finished = True

    def transfer_to_pepper(self, file_path):
        """
        Transfer file to Pepper using SSH
        :param file_path: local path to file
        """
        super(WeatherService, self).transfer_to_pepper(file_path)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        self.tablet.enableWifi()
        ip = self.tablet.robotIp()
        remote_path = 'http://' + ip + '/apps/' + self.folder_name + full_file_name
        self.tablet.showWebview(remote_path)

    def shutoff(self, *_args):
        """
        Shutoff and unsubscribe to events. Trigger ModuleFinished event.
        """
        try:
            #self.rides_subscriber.signal.disconnect(self.next_ride_id)
            #self.trip_subscriber.signal.disconnect(self.trip_id)
            #self.dialog.deactivateTopic(self.topic)
            #self.dialog.unloadTopic(self.topic)
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

    def run(self):
        self.initiate_dialog()
        while not self.module_finished:
            time.sleep(1)
        self.shutoff()
