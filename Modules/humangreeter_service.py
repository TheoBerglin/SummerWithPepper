import time
import math


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
        print "Starting application"
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

        self.face_id = 0

        # ---------- Subscribe to apps/modules here ------------
        self.vt_subscriber = self.memory.subscriber("vt_mod")  # vt_mod event raised in dialog and on click
        self.vt_id = self.vt_subscriber.signal.connect(self.vasttrafik_module)

        self.module_set = False
        self.module_to_run = ''

    def get_module(self):
        return self.module_to_run

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

    def rotate(self, rad, *_args):
        """
        Callback for event ModuleFinished
        """
        print "Rotating " + str(rad*180/math.pi) + " deg"
        self.motion.moveTo(0, 0, rad)

    def vasttrafik_module(self, *_args):
        """
        Callback for event vt_mod which creates a Vasttrafik Module and runs it.
        """

        self.module_to_run = 'VasttrafikService'
        self.module_set = True

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

    def go_to_sleep(self):
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

        if self.module_set:
            self.rotate(math.pi*2/3)
            self.module_set = False
            self.module_to_run = ''
        self.look_for_human()

        # Module runs until a new module has been called
        while not self.module_set:
            time.sleep(1)
        self.shutoff()
