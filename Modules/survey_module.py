#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.module import ModuleBaseClass
from Applications.Survey import Survey
import os
import paramiko
from scp import SCPClient


class SurveyModule(ModuleBaseClass):
    """
    A survey module
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        # Folder name on Pepper
        folder_name = "survey"
        # Superclass init call
        super(SurveyModule, self).__init__(app, name, pepper_ip, folder_name)
        self.local_html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', r'pepper_html/Survey/'))
        # Survey handler
        self.survey = Survey(self.local_html_path)
        # Topics
        self.survey_topic_path = "/home/nao/Survey_enu.top"
        self.result_topic_path = "/home/nao/Survey_result_enu.top"

        # Button events
        self.good_button_subscriber = self.memory.subscriber("good_button_click")
        self.good_button_id = self.good_button_subscriber.signal.connect(self.good_click)

        self.neutral_button_subscriber = self.memory.subscriber("neutral_button_click")
        self.neutral_button_id = self.neutral_button_subscriber.signal.connect(self.neutral_click)

        self.bad_button_subscriber = self.memory.subscriber("bad_button_click")
        self.bad_button_id = self.bad_button_subscriber.signal.connect(self.bad_click)

        self.show_result_subscriber = self.memory.subscriber("show_result_trigger")
        self.show_result_id = self.show_result_subscriber.signal.connect(self.show_result)

        self.show_survey_subscriber = self.memory.subscriber("show_survey_trigger")
        self.show_survey_id = self.show_survey_subscriber.signal.connect(self.show_survey)

    def display_on_tablet(self, full_file_name):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        """
        super(SurveyModule, self).display_on_tablet(full_file_name)

    def run(self):
        """
        Initiate dialog upon method call. Run until finished, then shutoff.
        """
        self.module_finished = False
        self.show_survey()  # Run survey
        while not self.module_finished:
            time.sleep(1)
        self.shutoff()

    def shutoff(self, *_args):
        """
        Shutoff and unsubscribe to events. Trigger ModuleFinished event.
        """
        self.survey.save_survey()
        try:
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass

        try:
            self.unsubscribe_result_topic()
            print "Stopped result topic dialog"
        except RuntimeError:
            pass
        except AttributeError:
            pass

        try:
            self.unsubscribe_survey_topic()
            print "Stopped survey topic dialog"
        except RuntimeError:
            pass
        except AttributeError:
            pass

    def transfer_image_to_pepper(self, file_path):
        """
                Transfer file to Pepper using SSH
                :param file_path: local path to file
                """
        print "Transferring file to Pepper"
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.IP, username="nao", password="ericsson")

        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(ssh.get_transport())

        remote_path = '/home/nao/.local/share/PackageManager/apps/' + self.folder_name + '/html/images/'
        scp.put(file_path, remote_path=remote_path)
        print "Transfer complete"
        os.remove(file_path)  # Remove file after transfer

    def good_click(self, *_args):
        print "Good button clicked"
        self.tts.say('Thank you for the feedback')
        # self.tts.say('That is nice to hear')
        self.survey.register_click('good')

    def neutral_click(self, *_args):
        print "Neutral button clicked"
        self.tts.say('Thank you for the feedback')
        # self.tts.say('Hope it is better the next time')
        self.survey.register_click('neutral')

    def bad_click(self, *_args):
        print "Bad button clicked"
        self.tts.say('Thank you for the feedback')
        # self.tts.say('I am sorry to hear that. Hope it is better the next time')
        self.survey.register_click('bad')

    def show_result(self, *_args):
        self.tablet.hideWebview()
        try:
            self.unsubscribe_survey_topic()
            print "Stopped survey topic dialog"
        except RuntimeError:
            pass
        self.subscribe_result_topic()
        self.survey.plot_pie_chart()
        time.sleep(0.5)
        self.transfer_image_to_pepper(os.path.join(self.local_html_path, 'images', 'pie_chart.svg'))
        self.display_on_tablet('survey_summary.html')

    def subscribe_survey_topic(self):
        self.survey_topic = self.dialog.loadTopic(self.survey_topic_path)
        self.dialog.activateTopic(self.survey_topic)
        self.dialog.subscribe(self.name)
        print "Loaded survey topic"

    def subscribe_result_topic(self):
        self.result_topic = self.dialog.loadTopic(self.result_topic_path)
        self.dialog.activateTopic(self.result_topic)
        self.dialog.subscribe(self.name)
        print "Loaded result topic"

    def unsubscribe_survey_topic(self):
        self.dialog.deactivateTopic(self.survey_topic)
        self.dialog.unloadTopic(self.survey_topic)
        self.dialog.unsubscribe(self.name)

    def unsubscribe_result_topic(self):
        self.dialog.deactivateTopic(self.result_topic)
        self.dialog.unloadTopic(self.survey_topic)
        self.dialog.unsubscribe(self.name)

    def show_survey(self, *_args):
        """
        An example interaction
        """
        try:
            self.unsubscribe_result_topic()
            print "Stopped result topic dialog"
        except RuntimeError:
            pass
        except AttributeError:
            print "Result dialog not loaded"
        self.tablet.hideWebview()
        # Dialog
        self.subscribe_survey_topic()
        # Display on tablet
        self.display_on_tablet('survey.html')
        self.module_finished = False
