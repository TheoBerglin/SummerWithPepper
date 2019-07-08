#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
import os
import paramiko
import threading
from scp import SCPClient
from Modules.service import ServiceBaseClass


class WeatherService(ServiceBaseClass):
    """
    A module to handle interaction between the robot and the vasttrafik API.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        super(WeatherService, self).__init__(app, name, pepper_ip)

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
        print "Transferring file to Pepper"
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(IP, username="nao", password="ericsson")

        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(ssh.get_transport())

        scp.put(file_path, remote_path='/home/nao/.local/share/PackageManager/apps/vasttrafik/html')
        print "Transfer complete"
        os.remove(file_path)  # Remove file after transfer

    def display_on_tablet(self, full_file_name, update=True):
        """
        Display file on Pepper's tablet
        :param full_file_name: file name including file ending
        :param update: if view should be updated (only used with next rides)
        """
        self.tablet.enableWifi()
        ip = self.tablet.robotIp()
        remote_path = 'http://' + ip + '/apps/vasttrafik/' + full_file_name
        if update:
            while True:
                full_path = os.path.join(self.html_path, full_file_name)

                file_name = full_file_name.split('.')[0]

                print "Connecting to Vasttrafik and getting next rides"
                self.vt.create_departure_html(file_name)
                print "Download complete"

                self.transfer_to_pepper(full_path)
                self.tablet.showWebview(remote_path)

                time.sleep(5)  # Update view with new data every 3 seconds
                if self.hide_tablet:
                    print "Killing thread and hiding tablet"
                    self.tablet.hideWebview()
                    break
        else:
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
