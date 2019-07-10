#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.service import ServiceBaseClass


class ExampleService(ServiceBaseClass):
    """
    An example module.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "example"
        # Superclass init call
        super(ExampleService, self).__init__(app, name, pepper_ip, folder_name)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(ExampleService, self).display_on_tablet(full_file_name)

    def run(self):
        """
        Initiate dialog upon method call. Run until finished, then shutoff.
        """
        self.module_finished = False
        self.initiate_dialog()
        while not self.module_finished:
            time.sleep(1)
        self.shutoff()

    def shutoff(self, *_args):
        """
        Shutoff and unsubscribe to events. Trigger ModuleFinished event.
        """
        try:
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass

    def initiate_dialog(self):
        """
        An example interaction
        """
        self.tablet.hideWebview()

        self.tts.say("Im running an example module")

        self.module_finished = True



