# http://doc.aldebaran.com/2-1/getting_started/helloworld_python.html
from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "192.168.1.110", 9559)
tts.say("Hello, world!")
