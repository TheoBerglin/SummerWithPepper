from abc import ABCMeta, abstractmethod
import os


class ServiceBaseClass(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, app, name, pepper_ip):
        # Storing relevant variables
        self.IP = pepper_ip
        self.name = name
        self.app = app
        session = app.session

        # Set speech recognition language to swedish (in order for Pepper to understand stations)
        self.lang = session.service("ALSpeechRecognition")
        self.lang.pause(True)
        self.lang.setLanguage('Swedish')
        self.lang.pause(False)
        print "Currently set language is %s" % self.lang.getLanguage()

        # Get the services ALMemory, ALTextToSpeech, ALDialog, ALTabletService.
        self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.dialog = session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.tablet = session.service("ALTabletService")

        # Set variable to not finished on startup
        self.module_finished = False

