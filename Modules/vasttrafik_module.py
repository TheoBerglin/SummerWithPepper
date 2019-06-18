from naoqi import *


class VasttrafikModule(ALModule):
    """A module for running Vasttrafik dialogue and handle information"""

    def __init__(self, name, ip, port, dryrun, rewrite):
        ALModule.__init__(self, name)
        self.dryrun = dryrun
        if self.dryrun:
            logging.warning(">>>>>>>>>> Running in dry run mode <<<<<<<<<<")
        logging.info("Connecting to robot on {} port={}".format(ip, port))
        if not self.dryrun:
            self.tts = ALProxy("ALTextToSpeech", ip, port)
            self.asr = ALProxy("ALSpeechRecognition")
            self.memory = ALProxy("ALMemory")
            self.asr.setVocabulary(['next rides', 'trip'], True)
            self.memory.subscribeToEvent("WordRecognized", self.getName(), "handle_input")
            #self.vtobj = Vasttrafik()  # create vt object here
            self.tts.say("Next rides or search for a trip")

    def handle_input(self, key, value, message):
        pass

