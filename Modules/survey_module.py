#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
from Modules.module import ModuleBaseClass
import json
import datetime
import os
import matplotlib.pyplot as plt
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
        self.survey_information = {'full_information': list(),
                                   'result': {'good': 0,
                                              'neutral': 0,
                                              'bad': 0}}
        self.local_html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', r'pepper_html/Survey/'))
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
        self.save_survey()
        try:
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass

        try:
            self.unsubscribe_topic()
            print "Stopped done topic dialog"
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
        self.tts.say('That is nice to hear')
        self.register_click('good')

    def neutral_click(self, *_args):
        print "Neutral button clicked"
        self.tts.say('Hope it is better the next time')
        self.register_click('neutral')

    def bad_click(self, *_args):
        print "Bad button clicked"
        self.tts.say('I am sorry to hear that. Hope it is better the next time')
        self.register_click('bad')

    def show_result(self, *_args):
        self.tablet.hideWebview()
        try:
            self.unsubscribe_topic()
            print "Stopped survey topic dialog"
        except RuntimeError:
            pass
        self.plot_pie_chart()
        self.transfer_image_to_pepper(os.path.join(self.local_html_path, 'images', 'pie_chart.svg'))
        self.display_on_tablet('survey_summary.html')
        self.subscribe_result_topic()

    def register_click(self, button):
        reg_time = datetime.datetime.now()
        reg_time = reg_time.strftime('%d/%m/%Y, %H:%M:%S')
        self.survey_information['full_information'].append({'time': reg_time,
                                                            'button': button})
        self.survey_information['result'][button] += 1

    def save_survey(self):
        """"""
        save_str = json.dumps(self.survey_information, indent=2, sort_keys=True)
        full_file_name = 'survey_information.txt'
        full_save_path = '%s/%s' % (self.local_html_path, full_file_name)
        with open(full_save_path, 'w+') as f:
            f.write(save_str)
        print 'Saving survey data to: ' + full_save_path

    def print_survey(self):
        fields = ['good', 'neutral', 'bad']
        total_clicks = 0
        for field in fields:
            total_clicks += self.survey_information['result'][field.lower()]
        print 50 * '-'
        print 'Survey summary'
        for field in fields:
            v = self.survey_information['result'][field.lower()]
            print '%d people (%.1f%%) thought the event was %s' % (v, 100.0 * v / total_clicks, field)
        print 50 * '-'

    def plot_pie_chart(self):
        # Plot data
        labels = [label.capitalize() for label in self.survey_information['result'].keys()]
        sizes = [self.survey_information['result'][label] for label in self.survey_information['result'].keys()]
        # colors red, green and yellow
        colors = ['#ff9999', '#99ff99', '#ffcc99']
        # Pop out the pie charts
        explode = (0.05, 0.05, 0.05)
        # Plot pie chart
        fig1, ax1 = plt.subplots()
        _, texts, pct = ax1.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90,
                                explode=explode, pctdistance=0.7)
        # Set sizes of percentage and text
        [_.set_fontsize(14) for _ in pct]
        [_.set_fontsize(18) for _ in texts]
        # draw circle in the middle
        centre_circle = plt.Circle((0, 0), 0.5, fc='white')
        # plot text in the middle of the circle
        plt.text(-0.3, -0.075, "Result", fontsize=24, fontweight='bold')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.axis('equal')
        plt.tight_layout()
        self.save_figure(fig, 'pie_chart.svg')
        plt.close()

    def save_figure(self, fig, fig_name):
        fig.savefig(os.path.join(self.local_html_path, 'images', fig_name), format='svg', dpi=1000)

    def subscribe_survey_topic(self):
        self.subscribe_topic("/home/nao/Survey_enu.top")

    def subscribe_result_topic(self):
        self.subscribe_topic("/home/nao/Survey_result_enu.top")

    def subscribe_topic(self, topic_path):
        # Dialog
        self.loaded_topic = self.dialog.loadTopic(topic_path)
        self.dialog.activateTopic(self.loaded_topic)
        self.dialog.subscribe(self.name)

    def unsubscribe_topic(self):
        if hasattr(self, 'loaded_topic'):
            self.dialog.deactivateTopic(self.loaded_topic)
            self.dialog.unloadTopic(self.loaded_topic)
            self.dialog.unsubscribe(self.name)

    def show_survey(self, *_args):
        """
        An example interaction
        """
        try:
            self.unsubscribe_topic()
            print "Stopped result topic dialog"
        except RuntimeError:
            pass
        self.tablet.hideWebview()
        # Dialog
        self.subscribe_survey_topic()
        # Display on tablet
        self.display_on_tablet('survey.html')
        self.module_finished = False
