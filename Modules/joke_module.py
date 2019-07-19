#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

from Modules.module import ModuleBaseClass
from APIConnections.JokeClient import JokeClient


class JokeModule(ModuleBaseClass):
    """
    An example module.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "joke"
        # Superclass init call
        self.client = JokeClient()
        super(JokeModule, self).__init__(app, name, pepper_ip, folder_name)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(JokeModule, self).display_on_tablet(full_file_name)

    def run(self):
        """
        Initiate dialog upon method call. Run until finished, then shutoff.
        """
        self.module_finished = False
        self.tell_random_joke()
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

    def tell_random_joke(self):
        """
        An example interaction
        """
        joke = self.client.get_random_chuck_norris_joke()
        joke = joke.replace('Chuck Norris', 'Zlatan')
        self.tts.say(joke)
