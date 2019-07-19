#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

from Modules.module import ModuleBaseClass
from APIConnections.RandomFactClient import RandomFactClient


class RandomFactModule(ModuleBaseClass):
    """
    An example module.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "random_fact"
        # Superclass init call
        self.fact_client = RandomFactClient()
        super(RandomFactModule, self).__init__(app, name, pepper_ip, folder_name)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(RandomFactModule, self).display_on_tablet(full_file_name)

    def run(self):
        """
        Initiate dialog upon method call. Run until finished, then shutoff.
        """
        self.module_finished = False
        self.tell_random_fact()

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
        try:
            self.tts.resetSpeed()
            print 'Speech speed reset'
        except:
            pass

    def tell_random_fact(self):
        """
        An example interaction
        """
        self.tts.setParameter("speed", 92)
        self.tablet.hideWebview()
        random_fact = self.fact_client.get_random_english_fact()

        self.tts.say("Did you know that %s" % random_fact['text'])
        self.tts.resetSpeed()
