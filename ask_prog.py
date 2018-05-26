# Copyright 2017 loblab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import sys
import time
import signal
import os.path
import argparse
import RPi.GPIO as GPIO
from bitstring import *
from ask_signal import *
from ask_device import *
from ask_config import *

VERSION = "Ver 0.7, 5/26/2018, loblab"

class ProgramBase:

    def __init__(self, name, description):
        self.name = name
        self.commands = {}
        self.quit_flag = False
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

        self.argps = argparse.ArgumentParser(description=description)
        self.argps.add_argument('-v', '--version', action='version', version=VERSION)
        self.init_arguments()
        self.args = self.argps.parse_args()

        self.load_commands()
        GPIO.setmode(GPIO.BCM)
        self.init_device()

    def cleanup(self):
        GPIO.cleanup()

    def log_msg(self, msg):
        tstr = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        with open(LOG_FILE, 'a') as fp:
            fp.write("%s [%s] - %s\r\n" % (tstr, self.name, msg))

    def sig_handler(self, signum, frame):
        msg = "Got system signal %d... quit now." % signum
        print(msg)
        if self.args.log:
            self.log_msg(msg)
        self.quit_flag = True

    def load_commands(self):
        for key in ASK_CMD:
            cfg = ASK_CMD[key]
            self.commands[key] = Signal(cfg)

    def find_command(self, signal):
        for key in self.commands:
            if signal == self.commands[key]:
                return key
        return 'Unknown'

    def list_commands(self, debug=0):
        if debug == 0:
            print("Commands:", end=' ')
        for key in sorted(self.commands):
            if debug == 0:
                print(key, end=' ')
            elif debug >= 1:
                print("CMD %9s:" % key, end=' ')
                self.commands[key].show()
        if debug == 0:
            print()

    def run_action(self, cmd):
        script = ASK_ACTION.get(cmd)
        if script:
            os.system(script)

    def next_file_index(self):
        i = 0
        while True:
            i += 1
            filename = DATA_FILE % i
            if not os.path.isfile(filename):
                return i
        return 0

    def list_files(self, debug=0):
        i = 0
        while not self.quit_flag:
            i += 1
            filename = DATA_FILE % i
            if not os.path.isfile(filename):
                break
            if debug >= 1:
                sig = Signal()
                with open (filename, 'rb') as fp:
                    sig.load(fp)
                print("FILE %6s:" % i, end=' ')
                sig.show()
        if (i == 1):
            print("No file as %s" % DATA_FILE)
            return
        if debug == 0:
            print("Files: 1~%d" % (i - 1))

    def main(self):
        try:
            rc = self.process()
        finally:
            self.cleanup()
        return rc

