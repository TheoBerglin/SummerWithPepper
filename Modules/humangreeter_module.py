import time
import math


class HumanGreeter(object):
    """
    A class to react to face detection events and greet the user.
    """

    def __init__(self, app, name, walk=False):
        """
        Initialisation of qi framework and event detection.
        Walk determines if Pepper should walk randomly when trying to detect a face.
        """
        super(HumanGreeter, self).__init__()

        self.app = app
        self.name = name
        print "Starting application"
        self.app.start()
        self.session = self.app.session
        self.folder_name = "humangreeter"

        # Get the service ALMemory.
        self.memory = self.session.service("ALMemory")
        # Subscribe to FaceDetected event
        self.face_subscriber = self.memory.subscriber("FaceDetected")
        # Subscribe to move failed event
        self.obstacle_subscriber = self.memory.subscriber('ALMotion/MoveFailed')
        self.obstacle_id = None
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

        # Subscribe to the event "mod_to_run" and connect to a callback func
        self.subscriber = self.memory.subscriber("mod_to_run")
        self.subscriber.signal.connect(self.run_module)

        self.module_set = False
        self.module_to_run = ''

        self.walk = walk

    def get_module(self):
        return self.module_to_run

    def look_for_human(self, *_args):
        self.tablet.hideWebview()
        self.tts.say("Im searching for human life")
        # Connect the event callback.
        self.face_id = self.face_subscriber.signal.connect(self.on_human_tracked)  # returns SignalSubscriber
        if self.walk:
            self.random_walk()

    def obstacle_rotate(self, *_args):
        # So that we do not listen to the event while rotating. Event can be triggered by part of rotation.
        self.obstacle_subscriber.signal.disconnect(self.obstacle_id)
        self.motion.moveTo(-0.1, 0, 0)
        print "Obstacle rotate"
        self.rotate(math.pi / 4)  # Rotate 90 degrees
        # We have rotated, let's listen to the event again.
        self.obstacle_id = self.obstacle_subscriber.signal.connect(self.obstacle_rotate)

    def random_walk(self):
        self.move_around = True
        self.obstacle_id = self.obstacle_subscriber.signal.connect(self.obstacle_rotate)
        while self.move_around:
            self.motion.move(0.15, 0, 0)  # Move forward, x-direction, 0.15 m/s
        self.motion.stopMove()

    def on_human_tracked(self, _args):
        """
        Callback for event FaceDetected.
        """
        try:
            self.obstacle_subscriber.signal.disconnect(self.obstacle_id)
        except RuntimeError:
            print "Found face while not moving"

        self.face_subscriber.signal.disconnect(self.face_id)
        self.motion.stopMove()  # Stand still
        self.move_around = False  # Should not move around
        print "Face detected"
        self.display_on_tablet('introduction.html')

        self.tts.say("Hello carbon-based lifeform")

        self.topic = self.dialog.loadTopic("/home/nao/HumanGreeting_enu.top")
        self.dialog.activateTopic(self.topic)
        self.dialog.subscribe(self.name)

    def rotate(self, rad, *_args):
        """
        Method to make Pepper rotate
        """
        print "Rotating " + str(rad * 180 / math.pi) + " deg"
        self.motion.moveTo(0, 0, rad)

    def run_module(self, *_args):
        """
        Callback for module events.
        """
        print "Entered run module with value %s" % _args[0]
        self.module_to_run = _args[0]
        self.module_set = True

    def display_on_tablet(self, full_file_name):
        """
        Displays file on Pepper's tablet
        :param full_file_name: file name including file ending.
        """
        self.tablet.enableWifi()
        ip = self.tablet.robotIp()
        remote_path = 'http://' + ip + '/apps/' + self.folder_name + '/' + full_file_name
        self.tablet.showWebview(remote_path)

    def shutoff(self):
        """
        Shutoff and unsubscribe to events
        """
        try:
            self.move_around = False
            print 'Stopped moving around'
        except:
            pass

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
            if self.obstacle_id is not None:
                self.obstacle_subscriber.signal.disconnect(self.obstacle_id)
                print 'Unsubscribed to obstacle avoidance'
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
            self.rotate(math.pi * 2 / 3)
            self.module_set = False
            self.module_to_run = ''
        self.look_for_human()

        # Module runs until a new module has been called
        while not self.module_set:
            time.sleep(1)
        self.shutoff()
