#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
import os
from Modules.module import ModuleBaseClass
from Applications.imdb import Imbd


class IMDBModule(ModuleBaseClass):
    """
    A module to handle interaction between the robot and the imdb API.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "imdb"
        # Superclass init call
        super(IMDBModule, self).__init__(app, name, pepper_ip, folder_name)
        # Create Weather object
        self.imdb = Imbd()

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(IMDBModule, self).display_on_tablet(full_file_name)

    def run(self):
        self.old_movie = True
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
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass
        self.module_finished = False

    def initiate_dialog(self):
        self.tablet.hideWebview()

        # Load dialog and display intro screen
        self.topic = self.dialog.loadTopic("/home/nao/Imdb_enu.top")
        self.dialog.activateTopic(self.topic)
        self.dialog.subscribe(self.name)

        # Subscribe to events raised on button click
        self.random_subscriber = self.memory.subscriber("random")
        self.random_id = self.random_subscriber.signal.connect(self.random_movie)
        self.new_subscriber = self.memory.subscriber("new")
        self.new_id = self.new_subscriber.signal.connect(self.new_movie)

        self.random_movie()

    def random_movie(self, *_args):
        self.tablet.hideWebview()
        if self.old_movie:
            self.imdb.random_pop()
        else:
            self.imdb.random_new_pop()

        random_pop_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/imdb/movie.html'
        self.transfer_to_pepper(random_pop_path)
        poster_path = os.path.dirname(os.path.abspath('main.py')) + '/pepper_html/imdb/images/movie_poster.jpg'
        self.transfer_to_pepper(poster_path)
        self.display_on_tablet('movie.html')
        self.tts.say('How about ' + self.imdb.movie_data['title'] + ' directed by ' + self.imdb.movie_data['director'])

    def new_movie(self, *_args):
        print "entered callback"
        self.old_movie = False
        self.random_movie()
