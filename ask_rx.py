#!/usr/bin/python
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

import RPi.GPIO as GPIO 
import time 
import sys
import os.path
import argparse
from bitstring import *
from ask_signal import *
from ask_device import *
from ask_config import VERSION, PIN_ASK_EN, PIN_ASK_RX, DATA_FILE

def next_file_index():
    i = 0
    while True:
        i += 1
        filename = DATA_FILE % i
        if not os.path.isfile(filename):
            return i
    return 0

def receive_loop(rx, timeout, save=False, debug=0):
    total = 0
    findex = next_file_index()
    print "Receive signals for %d seconds..." % timeout
    start_time = time.time()
    sig = SignalAuto()
    while (time.time() - start_time < timeout): 
        wave = rx.receive()
        if wave:
            if debug == 2:
                wave.show()
            if sig.decode(wave):
                total += 1
                print time.strftime('%H:%M:%S -', time.localtime(time.time())),
                if save:
                    filename = DATA_FILE % findex
                    print "FILE %d: " % findex,
                    with open(filename, 'wb') as fp:
                        sig.dump(fp)
                        #wave.dump(fp)
                    findex += 1
                sig.show()
                if debug == 1:
                    wave.show()
    return total

def main():
    parser = argparse.ArgumentParser(version=VERSION,
        description="Receive & decode ASK/OOK signals, save to files") 

    parser.add_argument('-t', dest='timeout', type=int, default=30, 
        help="run TIMEOUT seconds then quit the program. default 30")
    parser.add_argument('-s', dest='save', action='store_true', 
        help="save received signals to files (DATA_FILE in ask_config.py)")
    parser.add_argument('-d', dest='debug', type=int, default=0, choices=range(3), 
        help="debug info level, greater for more. default 0")

    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM) 
    rx = Receiver(PIN_ASK_RX, PIN_ASK_EN)
    total = receive_loop(rx, args.timeout, args.save, args.debug)
    GPIO.cleanup()
    print "%d received." % total
    return 0

if __name__ == "__main__":
    sys.exit(main())

