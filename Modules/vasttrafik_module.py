#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
import os
import paramiko
import threading
from scp import SCPClient
from Applications.Vasttrafik import Vasttrafik

IP = ''


class VasttrafikModule(object):
    """
    A module to handle interaction between the robot and the vasttrafik API.
    """

    def __init__(self, app, name, pepper_ip):
        """
        Initialisation of module and event detection.
        """
        super(VasttrafikModule, self).__init__()
        self.name = name
        global IP
        IP = pepper_ip

        session = app.session

        # Set speech recognition language to swedish (in order for Pepper to understand stations)
        self.lang = session.service("ALSpeechRecognition")
        self.lang.pause(True)
        self.lang.setLanguage('Swedish')
        self.lang.pause(False)
        print "Currently set language is %s" % self.lang.getLanguage()

        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Get the services ALTextToSpeech, ALDialog, ALTabletService.
        self.tts = session.service("ALTextToSpeech")
        #self.motion = session.service("ALMotion")
        self.dialog = session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.tablet = session.service("ALTabletService")

        # Create a Vasttrafik object for handling API calls
        self.html_path = os.path.dirname(os.path.abspath('main.py')) + r'\Applications'
        self.vt = Vasttrafik(self.html_path)

        self.t = None

        self.face_id = 0
        self.got_face = False

    def run(self):
        self.tablet.hideWebview()

        self.tts.say("Do you want to see the next rides or plan a trip")

        self.rides_subscriber = self.memory.subscriber("next_ride")
        self.next_ride_id = self.rides_subscriber.signal.connect(self.next_ride)
        self.trip_subscriber = self.memory.subscriber("trip")
        self.trip_id = self.trip_subscriber.signal.connect(self.trip)
        self.corr_trip_subscriber = self.memory.subscriber("corr_trip_view")
        self.corr_trip_id = self.corr_trip_subscriber.signal.connect(self.show_correct_trip)
        self.trip_input_subscriber = self.memory.subscriber("trip_input_view")
        self.trip_input_id = self.trip_input_subscriber.signal.connect(self.show_trip_input)

        self.topic = self.dialog.loadTopic("/home/nao/VasttrafikGreetingMod_enu.top")
        self.dialog.activateTopic(self.topic)
        self.dialog.subscribe(self.name)

    def show_correct_trip(self, *_args):
        """
        Callback for when corr_trip_view is set
        """
        self.display_on_tablet('correct_trip_vasttrafik.html', False)

    def show_trip_input(self, *_args):
        """
        Callback for when trip_input_view is set
        """
        self.display_on_tablet('trip_input.html', False)

    def next_ride(self, *_args):
        """
        Callback for when next_ride is set
        """
        print "Next ride callback started"

        self.tablet.hideWebview()
        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        file_name = 'next_ride'
        file_ending = '.htm'
        full_file_name = file_name + file_ending

        self.hide_tablet = False
        self.t = threading.Thread(target=self.display_on_tablet, args=(full_file_name, True))
        self.t.start()
        time.sleep(5)

        self.shutoff()

    def trip(self, *_args):
        """
        Callback for when trip is set
        """
        print "Trip callback started"
        self.tts.say("Fetching trip data")

        goal = self.memory.getData("arr_stop")
        dep = self.memory.getData("dep_stop")
        print "From: %s" % dep
        print "To: %s" % goal
        self.tablet.hideWebview()
        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        file_name = 'trip'
        file_ending = '.htm'
        full_file_name = file_name + file_ending
        full_path = os.path.join(self.html_path, full_file_name)

        print "Connecting to Vasttrafik and getting trip info"
        self.vt.calculate_trip(dep, goal)
        print "Download complete"
        self.transfer_to_pepper(full_path)

        self.display_on_tablet(full_file_name, False)
        time.sleep(10)

        self.shutoff()

    def transfer_to_pepper(self, file_path):
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

    def shutoff(self):
        """
        Shutoff and unsubscribe to events
        """
        try:
            #self.rides_subscriber.signal.disconnect(self.next_ride_id)
            #self.trip_subscriber.signal.disconnect(self.trip_id)
            self.dialog.deactivateTopic(self.topic)
            self.dialog.unloadTopic(self.topic)
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

