#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.module import ModuleBaseClass


class WeatherModule(ModuleBaseClass):
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
        super(WeatherModule, self).__init__(app, name, pepper_ip, folder_name)

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

    def initiate_dialog(self):
        self.tablet.hideWebview()

        self.tts.say("It's sunny")

        self.module_finished = True

