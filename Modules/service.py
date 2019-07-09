from abc import ABCMeta, abstractmethod
import paramiko
from scp import SCPClient
import os


class ServiceBaseClass(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, app, name, pepper_ip, folder_name):
        # Storing relevant variables
        self.IP = pepper_ip
        self.name = name
        self.app = app
        self.folder_name = folder_name
        session = app.session

        # Set speech recognition language to swedish (in order for Pepper to understand stations)
        self.lang = session.service("ALSpeechRecognition")
        self.lang.pause(True)
        self.lang.setLanguage('Swedish')
        self.lang.pause(False)
        print "Currently set language is %s" % self.lang.getLanguage()

        # Get the services ALMemory, ALTextToSpeech, ALDialog, ALTabletService.
        self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.dialog = session.service("ALDialog")
        self.dialog.setLanguage("English")
        self.tablet = session.service("ALTabletService")

        # Set variable to not finished on startup
        self.module_finished = False

        # Path to folder for saving created html files
        self.local_html_path = os.path.dirname(os.path.abspath('main.py')) + r'\Applications'

    @abstractmethod
    def transfer_to_pepper(self, file_path):
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

        remote_path = '/home/nao/.local/share/PackageManager/apps/' + self.folder_name + '/html'
        scp.put(file_path, remote_path=remote_path)
        print "Transfer complete"
        os.remove(file_path)  # Remove file after transfer
