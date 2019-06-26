#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Main class to handle the Vasttrafik application"""

import qi
import time
import sys
import argparse
import os
import paramiko
import threading
from scp import SCPClient
from Applications.Vasttrafik import Vasttrafik

IP = "192.168.1.101"


class HumanGreeter(object):
    """
    A simple class to react to face detection events.
    """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()
        app.start()
        session = app.session

        self.name = "HumanGreeter"
        #self.lang = session.service("ALSpeechRecognition")
        #self.lang.pause(True)
        #self.lang.setLanguage('Swedish')
        #self.lang.pause(False)

        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Subscribe to FaceDetected event
        self.face_subscriber = self.memory.subscriber("FaceDetected")
        # Get the services ALTextToSpeech, ALDialog, ALTabletService and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        #self.motion = session.service("ALMotion")
        self.dialog = session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.tablet = session.service("ALTabletService")
        self.face_detection = session.service("ALFaceDetection")
        self.face_detection.subscribe(self.name)

        # Create a Vasttrafik object for handling API calls
        self.html_path = "C:\Users\elibada\SummerWithPepper\Applications"
        self.vt = Vasttrafik(self.html_path)

        self.face_id = 0
        self.got_face = False
        self.look_for_human()

    def look_for_human(self):
        self.tts.say("Im searching for human life")
        self.stop_event = True
        #self.dialog_running = False
        # Connect the event callback.
        self.face_id = self.face_subscriber.signal.connect(self.on_human_tracked)  # returns SignalSubscriber

    # def on_human_tracked(self, value):
    #    """
    #    Callback for event FaceDetected.
    #   """
    #   #print "Human tracked"
    #   if not self.dialog_running:
    #       self.initiate_dialog(value)

    def on_human_tracked(self, value):
        """
        Callback for event FaceDetected.
        """
        self.face_subscriber.signal.disconnect(self.face_id)
        if value == []:  # empty value when the face disappears
            self.got_face = False
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
            print "Face detected"
            self.tts.say("Hello carbon-based lifeform")

            self.rides_subscriber = self.memory.subscriber("next_ride")
            self.next_ride_id = self.rides_subscriber.signal.connect(self.next_ride)
            self.trip_subscriber = self.memory.subscriber("trip")
            self.trip_id = self.trip_subscriber.signal.connect(self.trip)

            self.topic = self.dialog.loadTopic("/home/nao/VasttrafikGreeting_enu.top")
            self.dialog.subscribe(self.name)
            self.dialog.activateTopic(self.topic)

    def next_ride(self, *_args):
        """
        Callback for when next_ride is set
        """
        print "Next ride callback started"

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        file_name = 'live_test'
        file_ending = '.htm'
        full_file_name = file_name + file_ending
        full_path = os.path.join(self.html_path, full_file_name)

        print "Connecting to Vasttrafik and getting next rides"
        self.vt.create_departure_html(file_name)
        print "Download complete"
        self.transfer_to_pepper(full_path)

        self.stop_event = False
        t = threading.Thread(target=self.display_on_tablet, args=(full_file_name, ))
        t.start()
        time.sleep(3)

        self.look_for_human()

    def trip(self, *_args):
        """
        Callback for when trip is set
        """
        print "Trip callback started"

        self.goal = self.memory.getData("arrStop")
        self.dep = self.memory.getData("depStop")
        print self.goal
        print self.dep

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        file_name = 'trip'
        file_ending = '.htm'
        full_file_name = file_name + file_ending
        full_path = os.path.join(self.html_path, full_file_name)

        print "Connecting to Vasttrafik and getting trip info"
        self.vt.calculate_trip(self.dep, self.goal)
        print "Download complete"
        self.transfer_to_pepper(full_path)

        self.display_on_tablet(full_file_name, 10)

        self.look_for_human()

    def transfer_to_pepper(self, file_path):
        print "Transferring file to Pepper"
        paramiko.util.log_to_file("filename.log")
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(IP, username="nao", password="ericsson")

        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(ssh.get_transport())

        scp.put(file_path, remote_path='/home/nao/.local/share/PackageManager/apps/vasttrafik/html')
        print "Transfer complete"

    def display_on_tablet(self, file_name):
        self.tablet.enableWifi()
        ip = self.tablet.robotIp()
        remote_path = 'http://' + ip + '/apps/vasttrafik/' + file_name
        self.tablet.showWebview(remote_path)
        self.tts.say("Here you go")
        while True:
            print('thread running')
            if self.stop_event:
                print "Stopping tablet viewer"
                self.tablet.hideWebview()
                break

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
            self.face_subscriber.signal.disconnect(self.face_id)
            self.face_detection.unsubscribe(self.name)
            print "Unsubscribed to face"
        except RuntimeError:
            pass
        try:
            self.stop_event = True
            print "Tabletview stopped"
        except:
            pass

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting HumanGreeter"
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping HumanGreeter"
            self.shutoff()
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.101'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["HumanGreeter", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    human_greeter = HumanGreeter(app)
    human_greeter.run()
