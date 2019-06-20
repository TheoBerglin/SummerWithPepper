#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: A Simple class to get & read FaceDetected Events"""

import qi
import time
import sys
import argparse


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
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        #self.motion = session.service("ALMotion")
        self.dialog = session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.face_detection = session.service("ALFaceDetection")
        self.face_detection.subscribe("HumanGreeter")
        self.got_face = False
        self.look_for_human()

    def look_for_human(self):
        self.tts.say("Im searching for human life")
        # Connect the event callback.
        self.face_subscriber = self.memory.subscriber("FaceDetected")
        self.face_id = self.face_subscriber.signal.connect(self.on_human_tracked)  # returns SignalSubscriber

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
            # First Field = TimeStamp.
            timeStamp = value[0]
            print "TimeStamp is: " + str(timeStamp)

            self.rides_subscriber = self.memory.subscriber("next_ride")
            self.next_ride_id = self.rides_subscriber.signal.connect(self.next_ride)
            self.trip_subscriber = self.memory.subscriber("trip")
            self.trip_id = self.trip_subscriber.signal.connect(self.trip)

            self.topic = self.dialog.loadTopic("/home/nao/VasttrafikGreeting_enu.top")
            self.dialog.subscribe("HumanGreeter")
            self.dialog.activateTopic(self.topic)

    def next_ride(self, *_args):
        """
        Callback for when next_ride is set
        """
        print "Next ride callback started"

        #self.rides_subscriber.signal.disconnect(self.next_ride_id)
        #self.trip_subscriber.signal.disconnect(self.trip_id)

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe("HumanGreeter")
        self.look_for_human()

    def trip(self, *_args):
        """
        Callback for when trip is set
        """
        print "Trip callback started"

        #self.rides_subscriber.signal.disconnect(self.next_ride_id)
        #self.trip_subscriber.signal.disconnect(self.trip_id)
        self.goal = self.memory.getData("arrStop")
        self.dep = self.memory.getData("depStop")
        print self.goal
        print self.dep

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe("HumanGreeter")

        self.look_for_human()

    def shutoff(self):
        try:
            self.rides_subscriber.signal.disconnect(self.next_ride_id)
            self.trip_subscriber.signal.disconnect(self.trip_id)
            self.dialog.deactivateTopic(self.topic)
            self.dialog.unloadTopic(self.topic)
            self.dialog.unsubscribe("HumanGreeter")
            print "Stopped dialog"
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.face_subscriber.signal.disconnect(self.face_id)
            self.face_detection.unsubscribe("HumanGreeter")
            print "Unsubscribed to face"
        except RuntimeError:
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
    parser.add_argument("--ip", type=str, default="192.168.1.104",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.104'.")
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
