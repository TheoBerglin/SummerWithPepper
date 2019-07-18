#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.module import ModuleBaseClass
from Applications.RSSNewsHandler import RSSNewsHandler
import os
import re
class NewsModule(ModuleBaseClass):
    """
    An example module.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "newsModule"
        # Superclass init call
        super(NewsModule, self).__init__(app, name, pepper_ip, folder_name)
        self.rss = RSSNewsHandler()

        # Subscribe to events raised in dialog or on button click
        self.exit_subscriber = self.memory.subscriber("exit_button_clicked")
        self.exit_id = self.exit_subscriber.signal.connect(self.click_exit_button)
        self.news_click_subscriber = self.memory.subscriber("news_clicked")
        self.news_click_id = self.news_click_subscriber.signal.connect(self.click_news_button)

        # Subscribe to dialog
        self.news_topic = self.dialog.loadTopic("/home/nao/News_enu.top")
        self.dialog.activateTopic(self.news_topic)
        self.dialog.subscribe(self.name)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(NewsModule, self).display_on_tablet(full_file_name)

    def run(self):
        """
        Initiate dialog upon method call. Run until finished, then shutoff.
        """
        self.module_finished = False
        full_file_name = "news.html"
        self.display_on_tablet(full_file_name)
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
        try:
            self.tts.resetSpeed()
            print "Speech speed reset"
        except:
            pass

        try:
            self.dialog.deactivateTopic(self.news_topic)
            self.dialog.unloadTopic(self.news_topic)
            self.dialog.unsubscribe(self.name)
            print "Stopped news dialog"
        except RuntimeError:
            pass
        except AttributeError:
            pass

    def click_news_button(self, news_clicked):
        """
        Callback for module events.
        """
        print "Entered clickNewsButton with value %s" % news_clicked
        self.say_random_news(news_clicked)

    def click_exit_button(self, *_args):
        self.tablet.hideWebview()
        self.tts.say('That was the news with me, Pepper')
        self.module_finished = True

    def say_random_news(self, site_key):
        """
        An example interaction
        """
        self.tts.setParameter("speed", 85)
        news_article = self.rss.get_random_news(site_key)
        self.tts.say(re.sub('<[^<]+?>', '', news_article.title))
        time.sleep(1)
        if site_key != 'fox':
            self.tts.say(re.sub('<[^<]+?>', '', news_article.summary.split('<div')[0]))  # Reuters trick
        self.tts.resetSpeed()


