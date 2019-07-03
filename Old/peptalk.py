#!/usr/bin/env python
from __future__ import division, print_function

import argparse
import logging
import os
import time
from naoqi import ALProxy


def main():
    args = parse_args()
    setup_logger(args.verbose)
    logging.debug("Args: {}".format(args))

    robot = Robot(fname=args.file, ip=args.ip, port=args.port, dryrun=args.dryrun, rewrite=args.rewrite)

    robot.interact()
   

class Robot(object):
    def __init__(self, fname, ip, port, dryrun, rewrite):
        self.fname = fname
        self.dryrun = dryrun
        self.rewrite = rewrite
        if self.dryrun:
            logging.warning(">>>>>>>>>> Running in dry run mode <<<<<<<<<<")
        logging.debug("Reading file {}".format(fname))
        try:
            with open(fname) as f:
                self.texts = [line.rstrip('\n') for line in f]
        except IOError:
            self.texts = ["Hello", "Good Bye"]
            logging.info("Failed to read file {}. Initializing with default texts.".format(fname))
        logging.debug("Available texts: {}".format(self.texts))
        logging.info("Connecting to robot on {} port={}".format(ip, port))
        if not self.dryrun:
            self.tts = ALProxy("ALTextToSpeech", ip, port)

    def say(self, what):
        print('Saying "{}"'.format(what))
        if what not in self.texts:
            logging.debug('Adding "{}" to list of texts'.format(what))
            self.texts.append(what)
            if self.rewrite:
                with open(self.fname, 'w') as f:
                    logging.debug('Updating {} with new text "{}"'.format(self.fname, self.texts[-1]))
                    for text in self.texts:
                        f.write("{}\n".format(text))
        if not self.dryrun:
            self.tts.say(what)

    def interact(self):
        done = False
        while not done:
            s = raw_input('> ')
            if s == 'q':
                done = True
            elif s == '?' or s == '':
                helptext = 'Available commands: ?, q, n <text number>, s <actual text>'
                print(helptext)
                for i, x in enumerate(self.texts):
                    print(i, x)
            elif s.split()[0] == 'n':
                i = int(s.split()[1]) if len(s.split()) > 1 else -1
                if i >= 0 and i < len(self.texts):
                    self.say(self.texts[i])
                else:
                    print("Illegal index: {}. Allowed indices: 0-{}".format(i, len(self.texts)-1))                
            elif s.split()[0] == 's':
                text = " ".join(s.split()[1:])
                text = text.replace('"', '')
                self.say(text)
            else:
                print("Illegal command: {}".format(s))
            

def parse_args():
    fc = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(add_help=True, formatter_class=fc)

    parser.add_argument('-d', '--dryrun', action='store_true', default=False,
                        help='Run in dry run mode, i.e. do not talk to robot')
    parser.add_argument('-r', '--rewrite', action='store_true', default=False,
                        help='Update the file with texts when a text is added')
    parser.add_argument('-f', '--file', type=str, default='talk.txt',
                        help='Input text file containing utterances')
    parser.add_argument('-i', '--ip', type=str, default="192.168.1.110",
                        help='Robot IP address')
    parser.add_argument('-p', '--port', type=str, default=9559,
                        help='Robot port')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Increase verbosity. Use -vv for full debug')

    return parser.parse_args()


def setup_logger(verbose):
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    logging.getLogger().setLevel(level)

    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(filename)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logging.getLogger().addHandler(console_handler)


if __name__ == '__main__':
    main()
