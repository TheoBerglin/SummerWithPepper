import qi
import time
import sys
import argparse
import math
from Old.vasttrafik_module import VasttrafikModule
from Modules.weather_service import WeatherModule

IP = "192.168.1.102"


class HumanGreeter(object):
    """
    A class to react to face detection events and greet the user.
    """

    def __init__(self, app, name):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()
        self.app = app
        self.name = name

        self.app.start()
        self.session = self.app.session

        # Get the service ALMemory.
        self.memory = self.session.service("ALMemory")
        # Subscribe to FaceDetected event
        self.face_subscriber = self.memory.subscriber("FaceDetected")
        # Get the services ALTextToSpeech, ALDialog, ALTabletService and ALFaceDetection.
        self.tts = self.session.service("ALTextToSpeech")
        self.motion = self.session.service("ALMotion")
        self.motion.wakeUp()  # Must run command in order for Pepper to rotate if not in Auto life
        self.dialog = self.session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.tablet = self.session.service("ALTabletService")
        self.face_detection = self.session.service("ALFaceDetection")
        self.face_detection.subscribe(self.name)

        # ModuleFinished should be raised in each module upon shutoff.
        self.module_finished_subscriber = self.memory.subscriber("ModuleFinished")
        # Pepper will rotate to find new person
        self.module_finished_subscriber.signal.connect(self.rotate)

        self.face_id = 0
        self.modules = dict()

        # ---------- Subscribe to apps/modules here ------------
        self.vt_subscriber = self.memory.subscriber("vt_mod")  # vt_mod event raised in dialog and on click
        self.vt_id = self.vt_subscriber.signal.connect(self.vasttrafik_module)

        self.weather_subscriber = self.memory.subscriber("weather_mod")  # vt_mod event raised in dialog and on click
        self.weather_id = self.weather_subscriber.signal.connect(self.weather_module)

        self.look_for_human()

    def look_for_human(self, *_args):
        self.tablet.hideWebview()
        self.tts.say("Im searching for human life")
        # Connect the event callback.
        self.face_id = self.face_subscriber.signal.connect(self.on_human_tracked)  # returns SignalSubscriber

    def on_human_tracked(self, value):
        """
        Callback for event FaceDetected.
        """
        self.face_subscriber.signal.disconnect(self.face_id)

        print "Face detected"
        self.display_on_tablet('introduction.html')

        self.tts.say("Hello carbon-based lifeform")

        self.topic = self.dialog.loadTopic("/home/nao/HumanGreeting_enu.top")
        self.dialog.activateTopic(self.topic)
        self.dialog.subscribe(self.name)

    def rotate(self, *_args):
        """
        Callback for event ModuleFinished
        """
        print "Rotating 120 deg"
        self.motion.moveTo(0, 0, 2*math.pi/3)
        self.look_for_human()

    def vasttrafik_module(self, *_args):
        """
        Callback for event vt_mod which creates a Vasttrafik Module and runs it.
        """

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        print "Starting vt module"
        app_name = "VasttrafikModule"
        if app_name not in self.modules:
            print "Adding " + app_name + " to dict"
            vt_mod = VasttrafikModule(self.app, app_name, IP)  # _______________FIXA DETTA_______________
            self.modules[app_name] = vt_mod
        else:
            print app_name + " exists in dict"
            vt_mod = self.modules[app_name]
        vt_mod.run()

    def weather_module(self, *_args):
        """
        Callback for event weather_mod which creates a Weather Module and runs it.
        """

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)

        print "Starting weather module"
        app_name = "WeatherModule"
        if app_name not in self.modules:
            print "Adding " + app_name + " to dict"
            weather_mod = WeatherModule(self.app, app_name, IP)  # _______________FIXA DETTA_______________
            self.modules[app_name] = weather_mod
        else:
            print app_name + " exists in dict"
            weather_mod = self.modules[app_name]
        weather_mod.run()

    def display_on_tablet(self, full_file_name):
        """
        Displays file on Pepper's tablet
        :param full_file_name: file name including file ending.
        """
        self.tablet.enableWifi()
        ip = self.tablet.robotIp()
        remote_path = 'http://' + ip + '/apps/vasttrafik/' + full_file_name
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
            self.face_subscriber.signal.disconnect(self.face_id)
            self.face_detection.unsubscribe(self.name)
            print "Unsubscribed to face"
        except RuntimeError:
            pass
        try:
            self.tablet.hideWebview()
            print "Tabletview stopped"
        except:
            pass
        try:
            self.motion.rest()
            print "Going to sleep"
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
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.101'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    name = "HumanGreeter"
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application([name, "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    human_greeter = HumanGreeter(app, name)
    human_greeter.run()
